
def admin_parser(data) -> dict:
    return {
        'userID': str(data['_id']),
        'firstName': data['firstName'],
        'lastName': data['lastName'],
        'email': data['email'],
        'type': data['type'],
        'verified': data['verified']
        }

def event_parser(item, counts = 0) -> dict:

    return {
        'all': counts,
        "reurned":len(item),
        "events":[{key: value for key, value in dict.items() if key != '_id'} for dict in item]
        }