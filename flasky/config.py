
import os

class Config(object):

	SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = "postgresql://postgres:admin@123@localhost/weibo_develop"


class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = "postgresql://postgres:admin@123@localhost/weibo_test"


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = "postgresql://postgres:admin@123@localhost/flask_weibo"


config = {
	"development": DevelopmentConfig,
	"testing": TestingConfig,
	"production": ProductionConfig,
	"default": ProductionConfig
}