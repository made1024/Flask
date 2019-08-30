from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):

	name = StringField("What's your name?", validators=[DataRequired(message="input your name.")])

	role = SelectField("chose your role type",
	                   validators=[DataRequired(message="chose your role type.")],
	                   choices="")
	submit = SubmitField("submit")
