import uuid

from flask import jsonify, request, Blueprint

from Controller import Database
from Util.API import returnAPIFormat

route_blueprint = Blueprint('account', __name__)


# GET account
@route_blueprint.route("/account", methods=["GET"])
def getAccount():
	param = request.get_json()
	uid = param["uid"]
	if uid is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error")
	
	sql = "SELECT uid, username FROM account WHERE uid = ?"
	dataAccount = Database.request(sql, (uid,))
	if dataAccount is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
	
	data = {
		"uid": dataAccount[0][0],
		"username": dataAccount[0][1],
		"role": []
	}

    # SELECT account's roles
	sql = """SELECT r.uid, r.name FROM role r, account_role ar
	WHERE ar.account_id = (SELECT id FROM account WHERE uid = ?)
	AND r.id = ar.role_id
	"""
	dataRole = Database.request(sql, (uid,))
	if dataRole is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
	
	for i in dataRole:
		data["role"].append(i[1])
		
	return returnAPIFormat(data=data, link=request.path, method=request.method)


# POST account
@route_blueprint.route("/account", methods=["POST"])
def postAccount():
	param = request.get_json()
	username = param["username"]
	password = param["password"]
	roles = param["roles"]
	status = param["status"]
	uid = str(uuid.uuid4())

	if username is None or password is None or roles is None or status is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error")
	if status != 'open' and status != 'closed':
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error")
	
	# CHECK si l'account existe déjà
	sql = "SELECT uid FROM account WHERE username = ?"
	data = Database.request(sql, (username,))
	if data:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error, le l'username existe déjà")

	
	# RECUP les uid des roles + CHECK s'ils existent
	listeRoleId = []
	listeRoleName = []
	for i in roles:
		sql = "SELECT id, name FROM role WHERE name = ?"
		data = Database.request(sql, (i,))
		if data is None:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error, le role '"+i+"' n'existe pas")
		listeRoleId.append(data[0][0])
		listeRoleName.append(data[0][1])
	
	# CREER l'account
	sql = """INSERT INTO account (uid, username, password, token, dateExpire_Token, refresh_token, dateExpire_RefreshToken, dateExpire_ErrorLogin, status)
	VALUES (?, ?, ?, 'tokenTemp', 'dateExpire_TokenTemp', 'refresh_tokenTemp', 'dateExpire_RefreshTokenTemp', 'dateExpire_ErrorLoginTemp', ?)
	"""
	data = Database.request(sql, (uid, username, password, status))
	
	# RECUP id de l'account
	sql = "SELECT id, createdAt, updatedAt FROM account WHERE uid = ?"
	dataAccount = Database.request(sql, (uid,))
	if dataAccount is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error 2")
	
	print('LE SUPER PRINT : ')
	print(dataAccount)

	# INSERT account_role s'il y a des roles à ajouter
	if len(listeRoleId) != 0:
		for roleId in listeRoleId:
			sql = "INSERT INTO account_role (account_id, role_id) VALUES (?, ?)"
			Database.request(sql, (dataAccount[0][0], roleId))
	

	data = {
		"uid": uid,
		"username": username,
		"role": listeRoleName,
		"createdAt": dataAccount[0][1],
		"updatedAt": dataAccount[0][2]
	}
	# for role in listeRoleId:
	# 		data[-1]["categorie"].append(categorie[1])
		
	return returnAPIFormat(data=data, link=request.path, method=request.method)