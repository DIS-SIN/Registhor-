from flask import Blueprint, request
from registhor_app.evalhalla_routes.queries import queries
from registhor_app.utils import check_api_key, _valid_get

# Instantiate blueprint
evalhalla = Blueprint('evalhalla', __name__)


@evalhalla.route('/api/v1/evalhalla/cities', methods=['GET'])
@check_api_key
def cities():
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.args.get('lang', None) == 'fr' else 'en'
	
	# Run query and return as JSON
	results = queries.load_cities(lang)
	results_processed = _valid_get(results)
	return results_processed


@evalhalla.route('/api/v1/evalhalla/classifications', methods=['GET'])
@check_api_key
def classifications():
	# Run query and return as JSON
	results = queries.load_classifications()
	results_processed = _valid_get(results)
	return results_processed


@evalhalla.route('/api/v1/evalhalla/departments', methods=['GET'])
@check_api_key
def departments():
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.args.get('lang', None) == 'fr' else 'en'
	
	# Run query and return as JSON
	results = queries.load_departments(lang)
	results_processed = _valid_get(results)
	return results_processed
