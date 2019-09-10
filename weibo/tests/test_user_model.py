import unittest
import time
from datetime import datetime

from app.models import User, Permission, Role, AnonymousUser, Follow
from app import db, create_app


class MyTestCase(unittest.TestCase):

	def setUp(self) -> None:
		self.app = create_app("testing")
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()

	def tearDown(self) -> None:
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_password_setter(self):
		user = User(password="cat")
		self.assertTrue(user.password_hash is not None)

	def test_no_password_getter(self):
		user = User(password="cat")
		with self.assertRaises(AttributeError):
			user.password

	def test_password_verification(self):
		user = User(password="cat")
		self.assertTrue(user.verify_password("cat"))
		self.assertFalse(user.verify_password("dog"))

	def test_password_are_random(self):
		user1 = User(password="cat")
		user2 = User(password="cat")
		self.assertTrue(user1.password_hash != user2.password_hash)

	def test_valid_confirmation_token(self):
		user = User(password="cat")
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		self.assertTrue(user.confirm(token))

	def test_invalid_confirmation_token(self):
		user1 = User(password="cat")
		user2 = User(password="dog")
		db.session.add_all([user1, user2])
		db.session.commit()
		token = user1.generate_confirmation_token()
		self.assertFalse(user2.confirm(token))

	def test_expired_confirmation_token(self):
		user = User(password="cat")
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token(1)
		time.sleep(2)
		self.assertFalse(user.confirm(token))

	def test_change_password(self):
		user = User(password="cat")
		db.session.add(user)
		db.session.commit()
		user.password = "dog"
		self.assertFalse(user.verify_password("cat"))
		self.assertTrue(user.verify_password("dog"))

	def test_valid_reset_password_token(self):
		user = User(password="cat")
		db.session.add(user)
		db.session.commit()
		token = user.generate_reset_token()
		self.assertTrue(user.reset_password(token, "dog"))
		self.assertFalse(user.verify_password("cat"))
		self.assertTrue(user.verify_password("dog"))

	def test_invalid_reset_password_token(self):
		user = User(password="cat")
		db.session.add(user)
		db.session.commit()
		token = user.generate_reset_token()
		self.assertFalse(user.reset_password(token+"string", "dog"))
		self.assertFalse(user.verify_password("dog"))
		self.assertTrue(user.verify_password("cat"))

	def test_valid_change_email_token(self):
		user = User(email="susan@163.com")
		db.session.add(user)
		db.session.commit()
		token = user.generate_change_email_token("lily@163.com")
		self.assertTrue(user.change_email(token))
		self.assertFalse(user.email == "susan@163.com")
		self.assertTrue(user.email == "lily@163.com")

	def test_invalid_change_email_token(self):
		user1 = User(email="lucy@163.com")
		user2 = User(email="lilei@163.com")
		db.session.add_all([user1, user2])
		db.session.commit()
		token = user1.generate_change_email_token("sumail@163.com")
		self.assertFalse(user2.change_email(token))
		self.assertFalse(user2.email == "sumail@163.com")
		self.assertTrue(user2.email == "lilei@163.com")

	def test_duplicate_change_email_token(self):
		user1 = User(email="john@163.com")
		user2 = User(email="marchy@163.com")
		db.session.add_all([user1, user2])
		db.session.commit()
		token = user2.generate_change_email_token("john@163.com")
		self.assertFalse(user2.change_email(token))
		self.assertFalse(user2.email == "john@163.com")
		self.assertTrue(user2.email == "marchy@163.com")

	def test_user_role(self):
		u = User(email="john@163.com", password="cat")
		self.assertTrue(u.can(Permission.FOLLOW))
		self.assertTrue(u.can(Permission.COMMENT))
		self.assertTrue(u.can(Permission.WRITE_ARTICALES))
		self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
		self.assertFalse(u.can(Permission.ADMINISTRATOR))
		self.assertFalse(u.is_administrator)

	def test_moderater_role(self):
		u = User(email="tom@163.com", password="dog", role=Role.query.filter_by(name="Moderator").first())
		self.assertTrue(u.can(Permission.FOLLOW))
		self.assertTrue(u.can(Permission.COMMENT))
		self.assertTrue(u.can(Permission.WRITE_ARTICALES))
		self.assertTrue(u.can(Permission.MODERATE_COMMENTS))
		self.assertFalse(u.can(Permission.ADMINISTRATOR))
		self.assertFalse(u.is_administrator)

	def test_administrator_role(self):
		u = User(email="jack@163.com", password="mouse", role=Role.query.filter_by(name="Administrator").first())
		self.assertTrue(u.can(Permission.FOLLOW))
		self.assertTrue(u.can(Permission.COMMENT))
		self.assertTrue(u.can(Permission.WRITE_ARTICALES))
		self.assertTrue(u.can(Permission.MODERATE_COMMENTS))
		self.assertTrue(u.can(Permission.ADMINISTRATOR))
		self.assertTrue(u.is_administrator)

	def test_anonymoususer_role(self):
		u = AnonymousUser()
		self.assertFalse(u.can(Permission.FOLLOW))
		self.assertFalse(u.can(Permission.COMMENT))
		self.assertFalse(u.can(Permission.WRITE_ARTICALES))
		self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
		self.assertFalse(u.can(Permission.ADMINISTRATOR))
		self.assertFalse(u.is_administrator)

	def test_timestamps(self):
		u = User(password="cat")
		db.session.add(u)
		db.session.commit()
		self.assertTrue((datetime.utcnow() - u.member_since).total_seconds() < 3)
		self.assertTrue((datetime.utcnow() - u.last_since).total_seconds() < 3)

	def test_ping(self):
		u = User(password="cat")
		db.session.add(u)
		db.session.commit()
		time.sleep(2)
		last_seen_before = u.last_since
		u.ping()
		self.assertTrue(u.last_since > last_seen_before)

	def test_gravatar(self):
		u = User(email="john@example.com", password="cat")
		with self.app.test_request_context("/"):
			gravatar = u.gravatar()
			gravatar_256 = u.gravatar(256)
			gravatar_pg = u.gravatar(rating="pg")
			gravatar_retro = u.gravatar(default="retro")

		self.assertTrue('d4c74594d841139328695756648b6bd6' in gravatar)
		self.assertTrue('s=256' in gravatar_256)
		self.assertTrue('r=pg' in gravatar_pg)
		self.assertTrue('d=retro' in gravatar_retro)

	def test_follows(self):
		u1 = User(email='john@example.com', password='cat')
		u2 = User(email='susan@example.org', password='dog')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		self.assertTrue(u1.is_following(u1))
		self.assertTrue(u1.is_followed_by(u1))
		self.assertFalse(u1.is_following(u2))
		self.assertFalse(u1.is_followed_by(u2))
		self.assertTrue(u2.is_following(u2))
		self.assertTrue(u2.is_followed_by(u2))
		self.assertFalse(u2.is_following(u1))
		self.assertFalse(u2.is_followed_by(u1))
		timestamp_before = datetime.utcnow()
		u1.follow(u2)
		db.session.add(u1)
		db.session.commit()
		timestamp_after = datetime.utcnow()
		self.assertTrue(u1.is_following(u2))
		self.assertFalse(u1.is_followed_by(u2))
		self.assertTrue(u2.is_followed_by(u1))
		self.assertTrue(u1.followed.count() == 2)
		self.assertTrue(u2.followers.count() == 2)
		f = u1.followed.all()[-1]
		self.assertTrue(f.followed == u2)
		self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
		f = u2.followers.all()[0]
		self.assertTrue(f.follower == u1)
		u1.unfollow(u2)
		db.session.add(u1)
		db.session.commit()
		self.assertTrue(u1.followed.count() == 1)
		self.assertTrue(u2.followers.count() == 1)
		self.assertTrue(Follow.query.count() == 2)
		u2.follow(u1)
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		db.session.delete(u2)
		db.session.commit()
		self.assertTrue(Follow.query.count() == 1)

if __name__ == '__main__':
	unittest.main()
