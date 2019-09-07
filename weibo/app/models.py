from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app

from . import db
from . import login_manager


class Permission:
	FOLLOW = 0x01
	COMMENT = 0x02
	WRITE_ARTICALES = 0x04
	MODERATE_COMMENTS = 0x08
	ADMINISTRATOR = 0x80


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

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config.get("FLASKY_ADMIN"):
				self.role = Role.query.filter_by(permissions=0xff).first()
			self.role = Role.query.filter_by(default=True).first()

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

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))