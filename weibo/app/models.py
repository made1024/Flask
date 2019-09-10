
from datetime import datetime
import hashlib

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, request
from markdown import markdown
import bleach

from . import db
from . import login_manager


class Permission:
	FOLLOW = 0x01
	COMMENT = 0x02
	WRITE_ARTICALES = 0x04
	MODERATE_COMMENTS = 0x08
	ADMINISTRATOR = 0x80

class Follow(db.Model):
	__tablename__ = "follows"
	follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Role(db.Model):
	__tablename__ = "roles"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True, index=True)
	default = db.Column(db.Boolean, default=False, index=True)
	permissions = db.Column(db.Integer)
	users = db.relationship("User", backref="role")

	@staticmethod
	def insert_roles():
		roles = {
			"User": (Permission.FOLLOW |
					 Permission.COMMENT |
					 Permission.WRITE_ARTICALES, True),
			"Moderator": (Permission.FOLLOW |
						 Permission.COMMENT |
						 Permission.WRITE_ARTICALES |
						 Permission.MODERATE_COMMENTS, False),
			"Administrator": (0xff, False)
		}

		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			role.permissions = roles.get(r)[0]
			role.default = roles.get(r)[1]
			db.session.add(role)
		db.session.commit()


class User(UserMixin, db.Model):
	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String, unique=True, index=True)
	username = db.Column(db.String(64), unique=True, index=True)
	password_hash = db.Column(db.String(128))
	role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
	confirmed = db.Column(db.Boolean, default=False)
	name = db.Column(db.String(64), index=True)
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default=datetime.utcnow)
	last_since = db.Column(db.DateTime(), default=datetime.utcnow)
	avatar_hash = db.Column(db.String(32))
	posts = db.relationship("Post", backref="author", lazy="dynamic")
	followed = db.relationship('Follow',
	                           foreign_keys=[Follow.follower_id],
	                           backref=db.backref('follower', lazy='joined'),
	                           lazy='dynamic',
	                           cascade='all, delete-orphan')
	followers = db.relationship('Follow',
	                            foreign_keys=[Follow.followed_id],
	                            backref=db.backref('followed', lazy='joined'),
	                            lazy='dynamic',
	                            cascade='all, delete-orphan')
	comments = db.relationship("Comment", backref="author", lazy="dynamic")

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config.get("FLASKY_ADMIN"):
				self.role = Role.query.filter_by(permissions=0xff).first()
			self.role = Role.query.filter_by(default=True).first()

		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash = hashlib.md5(self.email.encode("utf-8")).hexdigest()

		self.follow(self)

	def ping(self):
		self.last_since = datetime.utcnow()
		db.session.add(self)

	def gravatar_hash(self):
		return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

	def gravatar(self, size=100, default="identicon", rating="g"):
		if request.is_secure:
			url = "https://secure.gravatar.com/avatar"
		else:
			url = "http://www.gravatar.com/avatar"
		hash = self.avatar_hash or self.gravatar_hash()
		return "{url}/{hash}?s={size}&d={default}&r={rating}".format(url=url, hash=hash, size=size,
		                                                             default=default, rating=rating)

	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py

		seed()
		for i in range(count):
			u = User(email=forgery_py.internet.email_address(),
			         username=forgery_py.internet.user_name(True),
			         password=forgery_py.lorem_ipsum.word(),
			         confirmed=True,
			         name=forgery_py.name.full_name(),
			         location=forgery_py.address.city(),
			         about_me=forgery_py.lorem_ipsum.sentence(),
			         member_since=forgery_py.date.date(True))
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()

	def follow(self, user):
		if not self.is_following(user):
			f = Follow(follower=self, followed=user)
			db.session.add(f)
			db.session.commit()

	def unfollow(self, user):
		f = self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)
			db.session.commit()

	def is_following(self, user):
		if user.id is None:
			return False
		return self.followed.filter_by(followed_id=user.id).first() is not None

	def is_followed_by(self, user):
		if user.id is None:
			return False
		return self.followers.filter_by(follower_id=user.id).first() is not None

	@property
	def followed_posts(self):
		return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

	@staticmethod
	def add_self_follows():
		for user in User.query.all():
			if not user.is_following(user):
				user.follow(user)
				db.session.add(user)
				db.session.commit()

	@property
	def password(self):
		raise AttributeError("password is not a readable attribute.")

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def generate_confirmation_token(self, expiration=3600):
		s = Serializer(current_app.config.get("SECRET_KEY"), expiration)
		return s.dumps({"confirm": self.id})

	def confirm(self, token):
		s = Serializer(current_app.config.get("SECRET_KEY"))
		try:
			data = s.loads(token)
		except:
			return False
		# 判断用户id与令牌对应的id是否相等，不同则返回False
		if data.get("confirm") != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		db.session.commit()
		return True

	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config.get("SECRET_KEY"), expiration)
		return s.dumps({"reset":self.id}).decode("utf-8")

	@staticmethod
	def reset_password(token, password):
		s = Serializer(current_app.config.get("SECRET_KEY"))
		try:
			data = s.loads(token.encode("utf-8"))
		except:
			return False
		user = User.query.get(data.get("reset"))
		if user is None:
			return False
		user.password = password
		db.session.add(user)
		return True

	def generate_change_email_token(self, new_email, expiration=3600):
		s = Serializer(current_app.config.get("SECRET_KEY"), expiration)
		return s.dumps({"reset": self.id, "new_email": new_email})

	def change_email(self, token):
		s = Serializer(current_app.config.get("SECRET_KEY"))
		try:
			data = s.loads(token)
		except:
			return False
		if data.get("reset") != self.id:
			return False
		new_email = data.get("new_email")
		if not new_email:
			return False
		if self.query.filter_by(email=new_email).first():
			return False
		self.email = new_email
		self.avatar_hash = hashlib.md5(self.email.encode("utf-8")).hexdigest()
		db.session.add(self)
		return True

	def can(self, permissions):
		return self.role is not None and (self.role.permissions & permissions) == permissions

	@property
	def is_administrator(self):
		return self.can(Permission.ADMINISTRATOR)

class AnonymousUser(AnonymousUserMixin):

	def can(self, permissions):
		return False

	@property
	def is_administrator(self):
		return False

class Post(db.Model):
	__tablename__ = "posts"

	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
	body_html = db.Column(db.Text)

	comments = db.relationship("Comment", backref="post", lazy="dynamic")

	@staticmethod
	def generate_fake(count=100):
		from random import seed, randint
		import forgery_py

		seed()
		user_count = User.query.count()

		for i in range(count):
			u = User.query.offset(randint(0, user_count-1)).first()
			p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
			         timestamp=forgery_py.date.date(True),
			         author=u)
			db.session.add(p)
			db.session.commit()

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ["a", "abbr", "acronym", "b", "blockquote", "code", "em", "i", "li",
		                "ol", "pre", "strong", "ul", "h1", "h2", "h3", "p"]
		target.body_html = bleach.linkify(bleach.clean(
			markdown(value, output_format="html"),
			tags=allowed_tags, strip=True
		))


class Comment(db.Model):
	__tablename__ = "comments"

	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	disabled = db.Column(db.Boolean)
	author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
	post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ["a", "abbr", "acronym", "b", "blockquote", "code", "em", "i", "li",
		                "ol", "pre", "strong", "ul", "h1", "h2", "h3", "p"]
		target.body_html = bleach.linkify(bleach.clean(
			markdown(value, output_format="html"),
			tags=allowed_tags, strip=True
		))


db.event.listen(Post.body, "set", Post.on_changed_body)
db.event.listen(Comment.body, "set", Comment.on_changed_body)
login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))