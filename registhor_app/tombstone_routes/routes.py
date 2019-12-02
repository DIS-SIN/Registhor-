from flask import Blueprint, request
from registhor_app.tombstone_routes.queries import queries
from registhor_app.tombstone_routes.utils import fields
from registhor_app.utils import check_api_key, _invalid_args, _valid_get

# Instantiate blueprint
tombstone = Blueprint('tombstone', __name__)


@tombstone.route('/api/v1/tombstone/<string:course_code>')
@check_api_key
def get_all_tombstone(course_code, methods=['GET']):
	"""Return all tombstone information for a given course code."""
	course_code = course_code.upper()
	results = queries.load_all_attrs(course_code)
	results_processed = _valid_get(results)
	return results_processed


@tombstone.route('/api/v1/tombstone/<string:course_code>/<string:course_attr>')
@check_api_key
def get_tombstone(course_code, course_attr, methods=['GET']):
	"""Return tombstone information for a given course code."""
	course_attr_db = fields.ATTR_DICT.get(course_attr, None)
	if course_attr_db is None:
		return _invalid_args('Invalid tombstone_value.')
	course_code = course_code.upper()
	results = queries.load_attr(course_attr_db, course_code)
	results_processed = _valid_get(results)
	return results_processed
