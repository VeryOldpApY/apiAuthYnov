import os
from flask import Flask

from Controller import Database
from Controller import Account

app = Flask(__name__)
app.register_blueprint(Account.route_blueprint)

@app.route('/')
def index():
	return {"status": "API is running"}


@app.route("/fixture")
def setFixture():
	Database.fixture()
	return {"status": "ok"}


if __name__ == "__main__":
	Database.fixture()
	if os.path.exists("bdd.db") is False:
		Database.fixture()
	app.run(debug=True)
