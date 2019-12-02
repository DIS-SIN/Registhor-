from flask import Blueprint, request
from registhor_app.offerings_routes.queries import queries
from registhor_app.utils import (check_api_key, _invalid_args, _missing_args,
	_valid_get)

# Instantiate blueprint
offerings = Blueprint('offerings', __name__)


@offerings.route('/api/v1/offerings/offering-information', methods=['GET'])
@check_api_key
def offering_info():
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.args.get('lang', None) == 'fr' else 'en'
	
	# User must pass at least date_1
	date_1 = request.args.get('date_1', None)
	if not date_1:
		return _missing_args(missing=['date_1'])
	
	# If date_2 not specified, simply assume a 1-day range
	date_2 = request.args.get('date_2', None)
	if not date_2:
		date_2 = date_1
	
	# If exclude_cancelled is true, exclude 'Cancelled - Normal' from
	# permitted values for offering_status
	exclude_cancelled = request.args.get('exclude_cancelled', 'false')
	offering_status = ['Delivered - Normal', 'Open - Normal', 'Open - Normal'] if exclude_cancelled == 'true' else ['Cancelled - Normal', 'Delivered - Normal', 'Open - Normal']
	
	# Optional
	course_code = request.args.get('course_code', '').upper()
	instructor_name = request.args.get('instructor_name', '')
	business_line = request.args.get('business_line', '')
	clients_only = request.args.get('clients_only', 'false')
	limit = request.args.get('limit', '999999')
	offset = request.args.get('offset', '0')
	
	# Ensure args 'limit' and 'offset' are both integers
	if not limit.isdigit() or not offset.isdigit():
		return _invalid_args('Invalid limit and/or offset.')
	
	# Run query and return as JSON
	results = queries.load_offering_info(date_1, date_2, offering_status, course_code, instructor_name, business_line, clients_only, limit, offset, lang)
	results_processed = _valid_get(results)
	return results_processed


@offerings.route('/api/v1/offerings/counts-by-city', methods=['GET'])
@check_api_key
def offering_counts():
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.args.get('lang', None) == 'fr' else 'en'
	
	# User must pass at least date_1
	date_1 = request.args.get('date_1', None)
	if not date_1:
		return _missing_args(missing=['date_1'])
	
	# If date_2 not specified, simply assume a 1-day range
	date_2 = request.args.get('date_2', None)
	if not date_2:
		date_2 = date_1
	
	# If exclude_cancelled is true, exclude 'Cancelled - Normal' from
	# permitted values for offering_status
	exclude_cancelled = request.args.get('exclude_cancelled', 'false')
	offering_status = ['Delivered - Normal', 'Open - Normal', 'Open - Normal'] if exclude_cancelled == 'true' else ['Cancelled - Normal', 'Delivered - Normal', 'Open - Normal']
	
	# Optional
	course_code = request.args.get('course_code', '').upper()
	instructor_name = request.args.get('instructor_name', '')
	business_line = request.args.get('business_line', '')
	clients_only = request.args.get('clients_only', 'false')
	
	# Run query and return as JSON
	results = queries.load_offering_counts(date_1, date_2, offering_status, course_code, instructor_name, business_line, clients_only, lang)
	results_processed = _valid_get(results)
	return results_processed
