
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SECRET_KEY"] = "hard to guess string"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:admin@123@localhost/dev_weibo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)


class NameForm(FlaskForm):
	username = StringField("what's your name?", validators=[DataRequired()])
	role = SelectField("your role", validators=[DataRequired()], choices="")
	submit = SubmitField("submit")


class Role(db.Model):
	__tablename__ = "roles"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	users = db.relationship("User", backref="role")


class User(db.Model):
	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))


@app.route("/", methods=["POST", "GET"])
def index():
	form = NameForm()
	form.role.choices = [(role.name,)*2 for role in Role.query.all()]
	if form.validate_on_submit():
		old_name = session.get("name")
		if old_name is not None and old_name != form.username.data:
			flash("Look like you have changed name.")
		user = User.query.filter_by(username=form.username.data).first()
		if user is None and form.username.data is not None:
			user = User(username=form.username.data,
			            role=Role.query.filter_by(name=form.role.data).first())
			db.session.add(user)
			db.session.commit()
		session["name"] = form.username.data
		form.username.data = ""
		return redirect(url_for("index"))
	return render_template("index.html",
	                       current_time=datetime.utcnow(),
	                       form=form,
	                       name=session.get("name"))


@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404


@app.errorhandler
def server_error(e):
	return render_template("500.html"), 500


if __name__ == "__main__":
	# db.drop_all()
	# db.create_all()
	# role_admin = Role(name="Admin")
	# role_guest = Role(name="Guest")
	# user_john = User(username="John", role=role_admin)
	# user_susan = User(username="Susan", role=role_guest)
	# db.session.add_all([role_admin, role_guest, user_john, user_susan])
	# db.session.commit()
	app.run(debug=True)
