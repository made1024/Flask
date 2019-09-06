
# app包构造文件，用于初始化flask扩展

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import config


bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"


def create_app(config_name):
	"""
	app工厂函数，在程序运行时才生成app
	:param config_name: 需要以哪种配置类实例化app，可选项：develop, testing, default
	:return: 实例化后的app程序
	"""
	app = Flask(__name__)
	app.config.from_object(config.get(config_name))
	config[config_name].init_app(app)

	# 实例化app扩展
	bootstrap.init_app(app)
	moment.init_app(app)
	mail.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)

	# 添加认证蓝图并注册到app中
	from .main import main as main_blueprint
	from .auth import auth as auth_blueprint

	app.register_blueprint(main_blueprint)
	app.register_blueprint(auth_blueprint, url_prefix="/auth")

	return app

