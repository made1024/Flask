
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Regexp, Email, Length
from wtforms.validators import ValidationError
from flask_login import current_user

from ..models import User


class LoginForm(FlaskForm):
	"""登录表单
	"""

	email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	remember_me = BooleanField("keep me logged in.")
	submit = SubmitField("Login")


class RegisterForm(FlaskForm):
	"""
	用户注册表单
	"""

	email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
	username = StringField("Username", validators=[DataRequired(), Length(1, 64),
	                                               Regexp("^[A-Za-z0-9_.]*$", 0,
	                                                      "username must have only letters, numbers, dots or underscores")])
	password = PasswordField("Password", validators=[DataRequired(), Length(1, 32)])
	password2 = PasswordField("Confirm password", validators=[DataRequired(), Length(1, 32),
	                                                          EqualTo("password", message="password must match.")])
	submit = SubmitField("Regist")

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError("email has already registered.")

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError("username has already in use.")


class ChangePasswordForm(FlaskForm):

	current_password = PasswordField("Current Password", validators=[DataRequired(), Length(1, 32)])
	new_password = PasswordField("New Password", validators=[DataRequired(), Length(1, 32)])
	new_password2 = PasswordField("Confirm Password",
	                              validators=[DataRequired(), Length(1, 32),
	                                        EqualTo("new_password", message="password must match.")])
	submit = SubmitField("Submit")

	def validate_current_password(self, field):
		if not current_user.verify_password(field.data):
			raise ValidationError("invalid current password")


class ResetPasswordRequestForm(FlaskForm):

	email = StringField("Email", validators=[DataRequired(), Email(), Length(1, 64)])
	submit = SubmitField("Reset Password")


class ResetPasswordForm(FlaskForm):

	new_password = PasswordField("New Password", validators=[DataRequired(), Length(1, 32)])
	new_password2 = PasswordField("Confirm Password",
	                              validators=[DataRequired(), Length(1, 32),
	                                          EqualTo("new_password", message="password must match.")])
	submit = SubmitField("Submit")


class ChangeMailForm(FlaskForm):
	new_email = StringField("New Email", validators=[DataRequired(), Email(), Length(1, 64)])
	password = PasswordField("New Password", validators=[DataRequired(), Length(1, 32)])
	submit = SubmitField("Change Email")

	def validate_new_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError("Email already registered.")