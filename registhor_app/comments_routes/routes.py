from flask import Blueprint, request
from registhor_app.comments_routes.queries import queries
from registhor_app.comments_routes.utils import fields
from registhor_app.utils import check_api_key, _invalid_args, _missing_args, _valid_get

# Instantiate blueprint
comments = Blueprint('comments', __name__)


@comments.route('/api/v1/comments/course-codes/<string:short_question>')
@check_api_key
def course_codes(short_question, methods=['GET']):
	"""Return list of course codes that match criteria."""
	# Unpack arguments
	short_question = fields.QUESTION_DICT.get(short_question, None)
	department_code = request.args.get('department_code', '').upper()
	fiscal_year = request.args.get('fiscal_year', '')
	
	# Mandatory arguments
	if short_question is None:
		return _invalid_args('Invalid question type.')
	if not department_code:
		return _missing_args(missing=['department_code'])
	
	results = queries.load_course_codes(short_question, fiscal_year, department_code)
	results_processed = _valid_get(results)
	return results_processed


@comments.route('/api/v1/comments/counts/<string:short_question>')
@check_api_key
def counts(short_question, methods=['GET']):
	"""Return number of comments of a given type (e.g. general comments)."""
	# Unpack arguments
	short_question = fields.QUESTION_DICT.get(short_question, None)
	course_code = request.args.get('course_code', '').upper()
	department_code = request.args.get('department_code', '').upper()
	fiscal_year = request.args.get('fiscal_year', '')
	
	# Mandatory arguments
	if short_question is None:
		return _invalid_args('Invalid question type.')
	if not department_code:
		return _missing_args(missing=['department_code'])
	
	results = queries.load_counts(short_question, course_code, fiscal_year, department_code)
	results_processed = _valid_get(results)
	return results_processed


@comments.route('/api/v1/comments/text/<string:short_question>')
@check_api_key
def text(short_question, methods=['GET']):
	"""Return all comments of a given type (e.g. general comments)."""
	# Unpack arguments
	# Only allow 'en' and 'fr' to be passed to app
	lang = 'fr' if request.args.get('lang', None) == 'fr' else 'en'
	short_question = fields.QUESTION_DICT.get(short_question, None)
	course_code = request.args.get('course_code', '').upper()
	department_code = request.args.get('department_code', '').upper()
	fiscal_year = request.args.get('fiscal_year', '')
	stars = request.args.get('stars', '')
	limit = request.args.get('limit', '')
	offset = request.args.get('offset', '0')
	
	# Mandatory arguments
	if short_question is None:
		return _invalid_args('Invalid question type.')
	if not department_code:
		return _missing_args(missing=['department_code'])
	if not limit:
		return _missing_args(missing=['limit'])
	
	# Ensure args 'limit' and 'offset' are both integers
	if not limit.isdigit() or not offset.isdigit():
		return _invalid_args('Invalid limit and/or offset.')
	
	# Run query and return as JSON
	results = queries.load_comments(short_question, course_code, lang, fiscal_year, department_code, stars, limit, offset)
	if not results:
		return _valid_get(list())
	results = [_make_dict(tup, lang) for tup in results]
	results_processed = _valid_get(results)
	return results_processed


def _make_dict(my_tup, lang):
	"""Make tuple in a dictionary so can be jsonified into an object."""
	labels = ['comment_text', 'course_code', 'learner_classification', 'offering_city',
			  'offering_fiscal_year', 'offering_quarter', 
			  'overall_satisfaction', 'stars', 'magnitude', 'nanos']
	results = {key: val for key, val in zip(labels, my_tup)}
	return results
