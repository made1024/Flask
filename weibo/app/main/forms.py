
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms.validators import ValidationError
from flask_pagedown.fields import PageDownField

from ..models import Role, User


class NameForm(FlaskForm):

	username = StringField("what's your name?", validators=[DataRequired()])
	submit = SubmitField("submit")


class ProfileForm(FlaskForm):

	name = StringField("Real Name?", validators=[Length(1, 64)])
	location = StringField("Location", validators=[Length(1, 64)])
	about_me = TextAreaField("About Me")
	submit = SubmitField("Submit")


class EditProfileAdminForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Length(1, 64),Email()])
	username = StringField("Username", validators=[DataRequired(), Length(1, 64),
	                                               Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0,
	                                                      "Username must have only letters，numbers, dots or underscores")])
	confirmed = BooleanField("Confirmed")
	role = SelectField("Role", validators=[DataRequired()], coerce=int)
	name = StringField("Real Name", validators=[Length(0, 64)])
	location = StringField("Location", validators=[Length(0, 64)])
	about_me = TextAreaField("About Me")
	submit = SubmitField("Submit")

	def __init__(self, user, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
		self.user = user

	def validate_email(self, field):
		if field.data != self.user.email and User.query.filter_by(email=field.data).first():
			raise ValidationError("email already registered.")

	def validate_username(self, field):
		if field.data != self.user.username and User.query.filter_by(username=field.data).first():
			raise ValidationError("username already in used.")


class PostForm(FlaskForm):
	body = PageDownField("What's on your mind?", validators=[DataRequired()])
	submit = SubmitField("Submit")


class CommentForm(FlaskForm):
	body = StringField("Comment", validators=[DataRequired()])
	submit = SubmitField("Submit")