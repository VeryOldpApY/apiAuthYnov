import os
from flask import Flask
from Controller import Database

app = Flask(__name__)


@app.route('/')
def index():
	return {"status": "API is running"}


@app.route("/fixture")
def setFixture():
	Database.fixture()
	return {"status": "ok"}


if __name__ == "__main__":
	if os.path.exists("bdd.db") is False:
		Database.fixture()
	app.run(debug=True)
