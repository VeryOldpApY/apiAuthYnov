import uuid

from flask import jsonify, request, Blueprint

from Controller import Database
from Util.API import returnAPIFormat

route_blueprint = Blueprint('account', __name__)


# GET account
@route_blueprint.route("/account", methods=["GET"])
def getAccount():
	# try: # A ENLEVER LORS DU DEBUG
		param = request.get_json()
		try:
			userToken = param["userToken"]
			uid = param["uid"]
		except:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error")
		if uid is None or userToken is None:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error")
		
		# SELECT l'user par le token + verif si token est toujours valide
		sql = """SELECT id, uid, username, createdAt, updatedAt, CASE WHEN dateExpire_Token > current_timestamp THEN 1
		WHEN dateExpire_Token <= current_timestamp THEN 0 END FROM account WHERE token = ?
		"""
		dataUser = Database.request(sql, (userToken,))
		if dataUser is None:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
		if not dataUser:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Token error")

		if dataUser[0][5] == 0:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Token plus valide")

		# SELECT les roles de l'user
		sql = "SELECT name FROM role r, account_role ar WHERE ar.account_id = ? AND r.id = ar.role_id"
		data = Database.request(sql, (dataUser[0][0],))
		if data is None:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
		
		roleAdmin = False
		for i in data:
			if (i[0] == 'ROLE_ADMIN'):
				roleAdmin = True
				break


		if roleAdmin == False:	# SI USER N'EST PAS ADMIN
			
			if uid != "me":
				# SELECT le compte demandé
				sql = "SELECT uid, username, createdAt, updatedAt FROM account WHERE uid = ?"
				dataAccount = Database.request(sql, (uid,))
				if dataAccount is None:
					return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
				if not dataAccount:
					return returnAPIFormat(data=None, link=request.path, method=request.method, status=404)
		
				# VERIF si c'est bien le même compte demandé que celui utilisé
				if dataAccount[0][0] != dataUser[0][1]:
					return returnAPIFormat(data=None, link=request.path, method=request.method, status=404) # 404 car on ne veut pas montrer qu'il y a bien un account avec cet uid
				
				data = {
					"uid": dataAccount[0][0],
					"username": dataAccount[0][1],
					"role": [],
					"createdAt": dataAccount[0][2],
					"updatedAt": dataAccount[0][3]
				}
				bonUid = dataAccount[0][0]

			else:	# SI uid = "me", pas besoin de select
				data = {
					"uid": dataUser[0][1],
					"username": dataUser[0][2],
					"role": [],
					"createdAt": dataUser[0][3],
					"updatedAt": dataUser[0][4]
				}
				bonUid = dataUser[0][1]

			# SELECT account's roles
			sql = """SELECT r.uid, r.name FROM role r, account_role ar
			WHERE ar.account_id = (SELECT id FROM account WHERE uid = ?)
			AND r.id = ar.role_id
			"""
			dataRole = Database.request(sql, (bonUid,))
			if dataRole is None:
				return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
				
			for i in dataRole:
				data["role"].append(i[1])
					
			return returnAPIFormat(data=data, link=request.path, method=request.method)


		else:	# SI USER EST ADMIN

			if uid != "me":
				# SELECT le compte demandé
				sql = "SELECT uid, username, createdAt, updatedAt FROM account WHERE uid = ?"
				dataAccount = Database.request(sql, (uid,))
				if dataAccount is None:
					return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")

				data = {
					"uid": dataAccount[0][0],
					"username": dataAccount[0][1],
					"role": [],
					"createdAt": dataAccount[0][2],
					"updatedAt": dataAccount[0][3]
				}
				bonUid = dataAccount[0][0]
			
			else:	# SI uid = "me", pas besoin de select
				data = {
					"uid": dataUser[0][1],
					"username": dataUser[0][2],
					"role": [],
					"createdAt": dataUser[0][3],
					"updatedAt": dataUser[0][4]
				}
				bonUid = dataUser[0][1]

			# SELECT account's roles
			sql = """SELECT r.uid, r.name FROM role r, account_role ar
			WHERE ar.account_id = (SELECT id FROM account WHERE uid = ?)
			AND r.id = ar.role_id
			"""
			dataRole = Database.request(sql, (bonUid,))
			if dataRole is None:
				return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
				
			for i in dataRole:
				data["role"].append(i[1])

			return returnAPIFormat(data=data, link=request.path, method=request.method)

	# except: # A ENLEVER LORS DU DEBUG
	# 	return returnAPIFormat(data=None, link=request.path, method=request.method, status=404)




# POST account
@route_blueprint.route("/account", methods=["POST"])
def postAccount():
	param = request.get_json()
	try:
		username = param["username"]
		password = param["password"]
		roles = param["roles"]
		status = param["status"]
	except:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error")
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
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
		if not data:
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




# PUT account
@route_blueprint.route("/account", methods=["PUT"])
def putAccount():
	param = request.get_json()
	try:
		userToken = param["userToken"]
		uid = param["uid"]
		username = param["username"]
		password = param["password"]
		status = param["status"]
	except:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error")
	if uid is None or username is None or password is None or status is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error")
	if status != 'open' and status != 'closed':
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error, status peut uniquement être 'open' ou 'closed'")
	
	# SELECT l'user par le token + verif si token est toujours valide
	sql = """SELECT id, uid, username, createdAt, updatedAt, CASE WHEN dateExpire_Token > current_timestamp THEN 1
	WHEN dateExpire_Token <= current_timestamp THEN 0 END FROM account WHERE token = ?
	"""
	dataUser = Database.request(sql, (userToken,))
	if dataUser is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
	if not dataUser:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Token error")

	if dataUser[0][5] == 0:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Token plus valide")

	# SELECT les roles de l'user
	sql = "SELECT name FROM role r, account_role ar WHERE ar.account_id = ? AND r.id = ar.role_id"
	data = Database.request(sql, (dataUser[0][0],))
	if data is None:
		return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
		
	roleAdmin = False
	for i in data:
		if (i[0] == 'ROLE_ADMIN'):
			roleAdmin = True
			break

	if roleAdmin == False:	# SI USER N'EST PAS ADMIN
			
		if uid != "me":
			# CHECK si l'account existe
			sql = "SELECT id FROM account WHERE uid = ?"
			dataAccountId = Database.request(sql, (uid,))
			if dataAccountId is None:
				return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
			if not dataAccountId:
				return returnAPIFormat(data=None, link=request.path, method=request.method, status=404)
		
			# VERIF si c'est bien le même compte demandé que celui utilisé
			if dataAccountId[0][0] != dataUser[0][0]:
				return returnAPIFormat(data=None, link=request.path, method=request.method, status=404) # 404 car on ne veut pas montrer qu'il y a bien un account avec cet uid
			
			bonId = dataAccountId[0][0]

		else:	# SI uid = "me", pas besoin de select
			bonId = dataUser[0][0]

		# UPDATE de l'account
		sql = "UPDATE account SET username = ?, password = ?, status = ?, updatedAt = current_timestamp WHERE id = ?"
		data = Database.request(sql, (username, password, status, bonId))
		if data is None:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")

		# SELECT les infos de l'account après les modifications
		sql = "SELECT uid, username, password, createdAt, updatedAt FROM account WHERE id = ?"
		data = Database.request(sql, (bonId,))
		if data is None:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
		
		# SELECT les roles de l'account
		listeRoleName = []
		sql = "SELECT name FROM role r, account_role ar WHERE ar.account_id = ? AND r.id = ar.role_id"
		dataRole = Database.request(sql, (bonId,))
		if dataRole is None:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
		for i in dataRole:
			listeRoleName.append(i[0])

		finalData = {
			"uid": data[0][0],
			"username": data[0][1],
			"password": data[0][2],
			"role": listeRoleName,
			"createdAt": data[0][3],
			"updatedAt": data[0][4]
		}

		return returnAPIFormat(data=finalData, link=request.path, method=request.method)

	else:	# SI USER EST ADMIN

		try:
			roles = param["roles"]
			if roles is None:
				return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error")
		except:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error")

		if uid != "me":
			# CHECK si l'account existe
			sql = "SELECT id FROM account WHERE uid = ?"
			dataAccountId = Database.request(sql, (uid,))
			if dataAccountId is None:
				return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
			if not dataAccountId:
				return returnAPIFormat(data=None, link=request.path, method=request.method, status=404)

			bonId = dataAccountId[0][0]

		else:	# SI uid = "me", pas besoin de select
			bonId = dataUser[0][0]

		# RECUP les uid des roles + CHECK s'ils existent
		listeRoleId = []
		listeRoleName = []
		for i in roles:
			sql = "SELECT id, name FROM role WHERE name = ?"
			data = Database.request(sql, (i,))
			if data is None:
				return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
			if not data:
				return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="Parameters Error, le role '"+i+"' n'existe pas")
			listeRoleId.append(data[0][0])
			listeRoleName.append(data[0][1])

		# UPDATE de l'account
		sql = "UPDATE account SET username = ?, password = ?, status = ?, updatedAt = current_timestamp WHERE id = ?"
		data = Database.request(sql, (username, password, status, bonId))
		if data is None:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")

		# DELETE tous les anciens roles de l'user
		sql = "DELETE FROM account_role WHERE account_id = ?"
		data = Database.request(sql, (bonId,))
		if data is None:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
		
		# INSERT tous les nouveaux roles de l'user
		if len(listeRoleId) != 0:
			for roleId in listeRoleId:
				sql = "INSERT INTO account_role (account_id, role_id) VALUES (?, ?)"
				Database.request(sql, (bonId, roleId))

		# SELECT les infos de l'account après les modifications
		sql = "SELECT uid, username, password, createdAt, updatedAt FROM account WHERE id = ?"
		data = Database.request(sql, (bonId,))
		if data is None:
			return returnAPIFormat(data=None, link=request.path, method=request.method, status=422, message="SQL Error")
		
		finalData = {
			"uid": data[0][0],
			"username": data[0][1],
			"password": data[0][2],
			"role": listeRoleName,
			"createdAt": data[0][3],
			"updatedAt": data[0][4]
		}

		return returnAPIFormat(data=finalData, link=request.path, method=request.method)
		