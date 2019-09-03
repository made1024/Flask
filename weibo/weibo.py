
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config["SECRET_KEY"] = "hard to guess string"

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
	name = StringField("what's your name?", validators=[DataRequired()])
	submit = SubmitField("submit")


@app.route("/", methods=["POST", "GET"])
def index():
	form = NameForm()
	if form.validate_on_submit():
		old_name = session.get("name")
		if old_name is not None and old_name != form.name.data:
			flash("Look like you have changed name.")
		session["name"] = form.name.data
		form.name.data = ""
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
	app.run(debug=True)
