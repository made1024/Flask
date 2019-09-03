from datetime import datetime

from flask import Flask, render_template, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell, Manager
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message

app = Flask(__name__)
app.config["SECRET_KEY"] = "hard to guess string"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:admin@123@localhost/dev_weibo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["MAIL_SERVER"] = "smtp.163.com"
app.config["MAIL_PORT"] = 25
app.config["MAIL_USER_TLS"] = True
app.config["MAIL_USERNAME"] = "flask@163.com"
app.config["MAIL_PASSWORD"] = "password"
app.config["FLASKY_MAIL_SUBJECT_PREFIX"] = "[FLASKY]"
app.config["FLASKY_MAIL_SENDER"] = "Flasky Admin <flask@163.com>"
app.config["FLASKY_ADMIN"] = "example@qq.com"

bootstrap = Bootstrap(app)
moment = Moment(app)
mail = Mail(app)
db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app, db)


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
	form.role.choices = [(role.name,) * 2 for role in Role.query.all()]
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
			session["Known"] = False
			if app.config["FLASKY_ADMIN"]:
				send_mail(app.config["FLASKY_ADMIN"], "New User", "mail/new_user", user=user)
		else:
			session["Known"] = True
		session["name"] = form.username.data
		form.username.data = ""
		return redirect(url_for("index"))
	return render_template("index.html",
	                       current_time=datetime.utcnow(),
	                       form=form,
	                       name=session.get("name"),
	                       known=session.get("Known"))


@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404


@app.errorhandler
def server_error(e):
	return render_template("500.html"), 500


def make_shell_context():
	return dict(app=app, db=db, Role=Role, User=User)


def send_mail(to, subject, template, **kwargs):
	msg = Message(app.config["FLASKY_MAIL_SUBJECT_PREFIX"] + subject,
	              sender=app.config["FLASKY_MAIL_SENDER"],
	              recipients=[to])
	msg.body = render_template(template + ".txt", **kwargs)
	msg.html = render_template(template + ".html", **kwargs)
	mail.send(msg)


if __name__ == "__main__":
	manager.add_command("shell", Shell(make_context=make_shell_context))
	manager.add_command("db", MigrateCommand)
	manager.run()
