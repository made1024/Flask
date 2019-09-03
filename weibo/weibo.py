
from datetime import datetime

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)


@app.route("/")
def index():
	return render_template("index.html", current_time=datetime.utcnow())


@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404


@app.errorhandler
def server_error(e):
	return render_template("500.html"), 500


if __name__ == "__main__":
	app.run(debug=True)
