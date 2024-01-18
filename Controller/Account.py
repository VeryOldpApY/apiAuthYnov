import uuid

from flask import jsonify, request, Blueprint

from Controller import Database
from Util.API import returnAPIFormat

route_blueprint = Blueprint('account', __name__)


### NORMALEMENT uniquement ton compte via l'uid ou l'alias "me". Sauf si tu as un compte avec le role ROLE_ADMIN ou tu peux voir tous les comptes.
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
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error, status peut uniquement être 'open' ou 'closed'")
	
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
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
	
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
		
	return returnAPIFormat(data=data, link=request.path, method=request.method)


### NORMALEMENT uniquement ton compte via l'uid ou l'alias "me". Sauf si tu as un compte avec le role ROLE_ADMIN ou tu peux modifier tous les comptes.
# PUT account
@route_blueprint.route("/account", methods=["PUT"])
def putAccount():
	param = request.get_json()
	uid = param["uid"]
	username = param["username"]
	password = param["password"]
	roles = param["roles"]
	status = param["status"]
	if uid is None or username is None or password is None or roles is None or status is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error")
	if status != 'open' and status != 'closed':
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error, status peut uniquement être 'open' ou 'closed'")
	
	# CHECK si l'account existe
	sql = "SELECT id FROM account WHERE uid = ?"
	dataAccountId = Database.request(sql, (uid,))
	if not dataAccountId:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error, l'account n'existe pas")
	
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

	# UPDATE de l'account
	sql = "UPDATE account SET username = ?, password = ?, status = ?, updatedAt = current_timestamp WHERE id = ?"
	data = Database.request(sql, (username, password, status, dataAccountId[0][0]))
	if data is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error 1")

	# DELETE tous les anciens roles de l'user
	sql = "DELETE FROM account_role WHERE account_id = ?"
	data = Database.request(sql, (dataAccountId[0][0],))
	if data is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error 2")
	
	# INSERT tous les nouveaux roles de l'user
	if len(listeRoleId) != 0:
		for roleId in listeRoleId:
			sql = "INSERT INTO account_role (account_id, role_id) VALUES (?, ?)"
			Database.request(sql, (dataAccountId[0][0], roleId))

	# SELECT les infos de l'account après les modifications
	sql = "SELECT uid, username, password, createdAt, updatedAt FROM account WHERE uid = ?"
	data = Database.request(sql, (uid,))
	if data is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error 3")
	
	finalData = {
		"uid": data[0][0],
		"username": data[0][1],
		"password": data[0][2],
		"role": listeRoleName,
		"createdAt": data[0][3],
		"updatedAt": data[0][4]
	}

	return returnAPIFormat(data=finalData, link=request.path, method=request.method)