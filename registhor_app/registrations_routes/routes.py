from flask import Blueprint, request
from registhor_app.registrations_routes.queries import queries
from registhor_app.utils import check_api_key, _missing_args, _valid_get

# Instantiate blueprint
registrations = Blueprint('registrations', __name__)


@registrations.route('/api/v1/registrations/course-codes', methods=['GET'])
@check_api_key
def course_codes():
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.args.get('lang', None) == 'fr' else 'en'
	
	# Run query and return as JSON
	results = queries.load_course_codes(lang)
	results_processed = _valid_get(results)
	return results_processed


@registrations.route('/api/v1/registrations/department-codes', methods=['GET'])
@check_api_key
def department_codes():
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.args.get('lang', None) == 'fr' else 'en'
	
	# Run query and return as JSON
	results = queries.load_department_codes(lang)
	results_processed = _valid_get(results)
	return results_processed


@registrations.route('/api/v1/registrations/training-locations', methods=['GET'])
@check_api_key
def training_locations():
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.args.get('lang', None) == 'fr' else 'en'
	
	# Unpack arguments
	department_code = request.args.get('department_code', '').upper()
	
	if not department_code:
		return _missing_args(missing=['department_code'])
	
	# Run query and return as JSON
	results = queries.load_training_locations(lang, department_code)
	results_processed = _valid_get(results)
	return results_processed
