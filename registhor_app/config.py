import os

class Config:
	DEBUG = False
	SECRET_KEY = os.environ.get('SECRET_KEY')
	# Options for flask.jsonify
	JSON_AS_ASCII = False
	JSONIFY_PRETTYPRINT_REGULAR = True
	JSON_SORT_KEYS = False
