from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, request

from . import main
from .forms import NameForm
from .. import db
from ..models import User, Role


@main.route("/", methods=["POST", "GET"])
def index():
	form = NameForm()
	form.role.choices = [(role.name, role.name) for role in Role.query.all()]
	if form.validate_on_submit():
		# flash 用法示例
		old_name = session.get("name")
		if old_name is not None and old_name != form.name.data:
			flash("looks like you have changed your name.")

		user = User.query.filter_by(username=form.name.data).first()
		if user is None:
			user = User(username=form.name.data,
			            role=Role.query.filter_by(name=form.role.data).first())
			db.session.add(user)
			db.session.commit()
			session["known"] = False
		else:
			session["known"] = True

		session["name"] = form.name.data
		# form.name.data = ""
		return redirect(url_for(".index"))
	return render_template("index.html",
	                       current_time=datetime.utcnow(),
	                       form=form, name=session.get("name"),
	                       known=session.get("known", False))
