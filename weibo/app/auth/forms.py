
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Regexp, Email, Length


class LoginForm(FlaskForm):
	"""登录表单
	"""

	email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	remember_me = BooleanField("keep me logged in.")
	submit = SubmitField("Login")
