import uuid

def uuid_gen():
	uid = uuid.uuid4().hex
	return uid