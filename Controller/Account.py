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