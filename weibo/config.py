
import os

"""Flask配置类相关定义
"""


class Config:
	"""
	公共配置类
	"""
	SECRET_KEY = os.environ.get("SECREt_KEY") or "hard to guess string"
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	FLASKY_MAIL_SUBJECT_PREFIX = "[FLASKY]"
	FLASKY_MAIL_SENDER = "Flasky Admin <blackeyes1023@163.com>"
	FLASKY_ADMIN = os.environ.get("FLASKY_ADMIN")
	FLASKY_FOLLOWERS_PER_PAGE = 20
	FLASKY_COMMENTS_PER_PAGE = 20

	def init_app(self):
		pass


class DevelopmentConfig(Config):
	"""
	开发配置类
	"""
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = "postgresql://postgres:admin@123@localhost/dev_weibo"
	MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
	MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
	MAIL_SERVER = "smtp.163.com"
	MAIL_PORT = 25
	MAIL_USER_TLS = True


class TestingConfig(Config):
	"""
	测试配置类
	"""
	TESTING = True
	SQLALCHEMY_DATABASE_URI = "postgresql://postgres:admin@123@localhost/test_weibo"


# 全局配置变量
config = {
	"develop": DevelopmentConfig,
	"testing": TestingConfig,
	"default": DevelopmentConfig
}
