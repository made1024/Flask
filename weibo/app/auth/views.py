
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from . import auth
from .forms import LoginForm, RegisterForm, ChangePasswordForm, \
	ResetPasswordForm, ResetPasswordRequestForm, ChangeMailForm
from .. import db
from ..models import User
from ..email import send_mail


@auth.route("/login/", methods=["POST", "GET"])
def login():
	"""
	登录视图函数
	:return:
	"""
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get("next") or url_for("main.index"))
		flash("Invalid username or password.")
	return render_template("auth/login.html", form=form)


@auth.route("/logout/")
@login_required
def logout():
	"""
	登出视图函数
	:return:
	"""
	logout_user()
	flash("You have been logged out.")
	return redirect(url_for("auth.login"))


@auth.route("/register/", methods=["POST", "GET"])
def register():
	"""
	用户注册视图函数
	:return:
	"""
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,
		            username=form.username.data,
		            password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_mail(user.email, "Confirm your account",
		          "/auth/email/confirm", user=user, token=token)
		flash("A confirmation email has been sent to your email.")
		return redirect(url_for("auth.login"))
	return render_template("auth/register.html", form=form)


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for("main.index"))
	if current_user.confirm(token):
		flash("You have confirmed, Thanks!")
		return redirect(url_for("main.index"))
	else:
		flash("The confirmation link is invalid or has expired.")
	return redirect(url_for("auth.login"))


@auth.before_app_request
def before_request():
	if (current_user.is_authenticated
		and not current_user.confirmed
		and request.endpoint[:5] != "auth."
		and request.endpoint != "static"):
		return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed/")
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for("main.index"))
	return render_template("auth/unconfirmed.html")


@auth.route("/confirm/")
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_mail(current_user.email, "Confirm your account",
		          "/auth/email/confirm", user=current_user, token=token)
	flash("A new confirmation email has been sent to you by email.")
	return redirect(url_for("auth.login"))


@auth.route("/changepassword", methods=["POST", "GET"])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=current_user.username).first()
		user.password = form.new_password.data
		db.session.add(user)
		db.session.commit()
		flash("You have changed your password.")
		return redirect(url_for("auth.login"))
	return render_template("auth/change_password.html", form=form)


@auth.route("/reset/", methods=["POST", "GET"])
def reset_password_request():
	if not current_user.is_anonymous:
		return redirect(url_for("auth.login"))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.generate_reset_token()
			send_mail(user.email, "Reset your password",
		          "/auth/email/reset_password", user=user, token=token)
			flash("A reset password email has been sent to your email.")
			return redirect(url_for("auth.login"))
	return render_template("auth/reset_password.html", form=form)


@auth.route("/reset/<token>", methods=["POST", "GET"])
def reset_password(token):
	if not current_user.is_anonymous:
		return redirect("auth.login")
	form = ResetPasswordForm()
	if form.validate_on_submit():
		if User.reset_password(token, form.new_password.data):
			db.session.commit()
			flash('Your password has been updated.')
			return redirect(url_for('auth.login'))
		else:
			flash("Reset your password failed.")
			return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html', form=form)


@auth.route("/change_email/", methods=["POST", "GET"])
@login_required
def change_email_request():
	form = ChangeMailForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.password.data):
			new_email = form.new_email.data
			token = current_user.generate_change_email_token(new_email)
			send_mail(current_user.email, "Change your email",
			          "/auth/email/change_email", user=current_user, token=token)
			flash("A change email address email has been sent to your email.")
			return redirect(url_for("main.index"))
		else:
			flash("Invalid email or password.")
	return render_template("auth/change_email.html", form=form)


@auth.route("/change_email/<token>")
def change_email(token):
	if current_user.change_email(token):
		db.session.commit()
		flash("You have changed email success.")
	else:
		flash("Invalid request.")
	return redirect(url_for("main.index"))