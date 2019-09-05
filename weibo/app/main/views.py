
from datetime import datetime

from flask import render_template, redirect, session, url_for, flash, current_app

from . import main
from .forms import NameForm
from .. import db
from ..models import Role, User
from ..email import send_mail


@main.route("/", methods=["POST", "GET"])
def index():
	form = NameForm()
	# form.role.choices = [(role.name,)*2 for role in Role.query.all()]
	if form.validate_on_submit():
		# 如果新登录的用户与session中保存的用户不同时，给出提示信息
		old_name = session.get("name")
		if old_name is not None and old_name != form.username.data:
			flash("Looks like you have changed your name.")

		# 如果是新用户，则在数据库中添加该用户
		user = User.query.filter_by(username=form.username.data).first()
		if user is None:
			# user = User(username=form.username.data,
			#             role=Role.query.filter_by(name=form.role.data).first())
			user = User(username=form.username.data)
			db.session.add(user)
			db.session.commit()
			session["Known"] = False
			if current_app.config["FLASKY_ADMIN"]:
				send_mail(current_app.config["FLASKY_ADMIN"], "New User", "mail/new_user", user=user)
		else:
			session["Known"] = True
		session["name"] = form.username.data
		form.username.data = ""
		return redirect(url_for("main.index"))
	return render_template("index.html", current_time=datetime.utcnow(),
	                       name=session.get("name"),
	                       known=session.get("Known"),
	                       form=form)
