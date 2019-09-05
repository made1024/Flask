
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):

	username = StringField("what's your name?", validators=[DataRequired()])
	# role = SelectField("what's your role?", validators=[DataRequired()], choices="")
	submit = SubmitField("submit")
