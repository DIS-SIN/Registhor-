from flask import Blueprint, request
from mysql.connector.errors import IntegrityError
from registhor_app.departments_routes.queries import queries
from registhor_app.utils import (check_api_key, _invalid_delete,
	_invalid_post, _missing_args, _valid_delete, _valid_post,
	_valid_get)

# Instantiate blueprint
departments = Blueprint('departments', __name__)


@departments.route('/api/v1/departments/mandatory-courses', methods=['GET'])
@check_api_key
def get_mandatory_courses():
	"""Return list of all active courses and if the given department
	considers them mandatory for its employees.
	"""
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.args.get('lang', None) == 'fr' else 'en'
	
	# Unpack arguments
	department_code = request.args.get('department_code', '').upper()
	
	if not department_code:
		return _missing_args(missing=['department_code'])
	
	# Run query and return as JSON
	results = queries.load_mandatory_courses(lang, department_code)
	results_processed = _valid_get(results)
	return results_processed


@departments.route('/api/v1/departments/mandatory-courses', methods=['POST'])
@check_api_key
def add_mandatory_course():
	# Unpack arguments
	data = request.json
	department_code = data.get('department_code', None)
	course_code = data.get('course_code', None)
	
	if not department_code:
		return _missing_args(missing=['department_code'])
	if not course_code:
		return _missing_args(missing=['course_code'])
	
	try:
		queries.add_mandatory_course(department_code, course_code)
	# If IntegrityError i.e. course entry already exists, return status 'OK'
	except IntegrityError:
		return _valid_post()
	except Exception as e:
		return _invalid_post()
	else:
		return _valid_post()


@departments.route('/api/v1/departments/mandatory-courses', methods=['DELETE'])
@check_api_key
def remove_mandatory_course():
	# Unpack arguments
	data = request.json
	department_code = data.get('department_code', None)
	course_code = data.get('course_code', None)
	
	if not department_code:
		return _missing_args(missing=['department_code'])
	if not course_code:
		return _missing_args(missing=['course_code'])
	
	try:
		queries.remove_mandatory_course(department_code, course_code)
	except Exception as e:
		return _invalid_delete()
	else:
		return _valid_delete()
