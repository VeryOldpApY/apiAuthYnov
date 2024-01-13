def returnAPIFormat(data, link, method, status=200, message=None):
	return {
		"_status": status,
		"_method": method,
		"_links": {
			"self": {"href": link}
		},
		"_embedded": {
			"items": {
				"data": data,
				"message": message
			}
		}
	}
