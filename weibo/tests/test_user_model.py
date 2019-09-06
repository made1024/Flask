import unittest
import time

from app.models import User
from app import db, create_app


class MyTestCase(unittest.TestCase):

	def setUp(self) -> None:
		self.app = create_app("testing")
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()

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


if __name__ == '__main__':
	unittest.main()
