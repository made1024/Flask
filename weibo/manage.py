
from flask_script import Shell, Manager
from flask_migrate import MigrateCommand, Migrate

from app import create_app, db
from app.models import Role, User


app = create_app("default")

manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
	return dict(app=app, db=db, Role=Role, User=User)


@manager.command
def test():
	import unittest
	tests = unittest.TestLoader().discover("tests")
	unittest.TextTestRunner(verbosity=2).run(tests)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


if __name__ == "__main__":
	manager.run()
