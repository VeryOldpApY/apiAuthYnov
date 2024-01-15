import secrets
import Database
import datetime

from flask import request, Blueprint

from Util.API import returnAPIFormat

route_blueprint = Blueprint("api", __name__)


def createToken(user_id):
	token = secrets.token_hex(32)
	sql = "UPDATE account SET token = ?, date = ? WHERE id = ?;"
	data = Database.request(sql, (token, (datetime.datetime.now() + datetime.timedelta(hours=1)), user_id))
	if data is None:
		return False
	return token


def createRefreshToken(user_id):
	token = secrets.token_hex(32)
	sql = "UPDATE account SET refresh_token = ?, dateExpire_RefreshToken = ? WHERE id = ?;"
	data = Database.request(sql, (token, (datetime.datetime.now() + datetime.timedelta(hours=2)), user_id))
	if data is None:
		return False
	return token


def errorLogin(user_id):
	sql = "SELECT countErrorLogin, dateExpire_ErrorLogin FROM account WHERE id = ?;"
	data = Database.request(sql, user_id)
	if data is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error")
	if data[0][1] < datetime.datetime.now():
		sql = "UPDATE account SET countErrorLogin = 1, dateExpire_ErrorLogin = ? WHERE id = ?;"
		data = Database.request(sql, ((datetime.datetime.now() + datetime.timedelta(minutes=5)), user_id))
		if data is None:
			returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
	elif data[0][0] == 2:
		sql = "UPDATE account SET status = ?, dateExpire_Status = ?, countErrorLogin = 0, dateExpire_ErrorLogin = null WHERE id = ?;"
		data = Database.request(sql, ("BANNED", (datetime.datetime.now() + datetime.timedelta(minutes=30)), user_id))
		if data is None:
			returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
	elif data[0][0] < 2:
		sql = "UPDATE account SET countErrorLogin = ? WHERE id = ?;"
		data = Database.request(sql, (data[0][0] + 1, user_id))
		if data is None:
			returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
	return True


@route_blueprint.route("/api/token", methods=["POST"])
def getToken():
	param = request.get_json()
	username = param["login"]
	password = param["password"]
	truc = param["from"]
	
	sql = "SELECT id FROM account WHERE username = ? AND password = ?;"
	data = Database.request(sql, (username, password))
	if data is None:
		sql = "SELECT id FROM account WHERE username = ?;"
		data = Database.request(sql, username)
		if data is None:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=404, message="Identifiers Error")
		else:
			errorLogin(data[0][0])
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=404, message="Invalid password")
	
	sql = "UPDATE account SET countErrorLogin = 0, dateExpire_ErrorLogin = null, 'from' = ? WHERE id = ?;"
	data = Database.request(sql, (truc, data[0][0]))
	if data is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
	
	token = createToken(data[0][0])
	tokenRefresh = createRefreshToken(data[0][0])
	data = {
		"token": token,
		"refreshToken": tokenRefresh
	}
	
	return returnAPIFormat(data=data, link=request.path, method=request.method, status=200, message="Token Created")


@route_blueprint.route("/api/validate", methods=["GET"])
def validateToken():
	param = request.get_json()
	token = param["token"]
	
	sql = "SELECT id, dateExpire_Token FROM account WHERE token = ?;"
	data = Database.request(sql, token)
	if data is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=404, message="Token Error")
	if data[0][1] < datetime.datetime.now():
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=404, message="Token Expired")
	return returnAPIFormat(data=None, link=request.path, method=request.method, status=200, message="Token Validated")


@route_blueprint.route("/api/refresh-token/token", methods=["POST"])
def refreshToken():
	param = request.get_json()
	tokenRefresh = param["refreshToken"]
	
	sql = "SELECT id, dateExpire_RefreshToken FROM account WHERE refresh_token = ?;"
	data = Database.request(sql, tokenRefresh)
	if data is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=404, message="Refresh Token Error")
	if data[0][1] < datetime.datetime.now():
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=404, message="Refresh Token Expired")
		
	token = createToken(data[0][0])
	tokenRefresh = createRefreshToken(data[0][0])
	data = {
		"token": token,
		"refreshToken": tokenRefresh
	}
	
	return returnAPIFormat(data=data, link=request.path, method=request.method, status=200, message="Token Refreshed")
