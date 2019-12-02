import re
from registhor_app.db import query_mysql
from registhor_app.utils import (_combine_overlapping_cities_hashed,
	_dict_decimal_to_float, _dict_remove_none)
from registhor_app.registrations_routes.utils import fields


def load_course_codes(lang):
	"""Query list of all course codes and their titles as seen
	in the LSR.
	"""
	field_name = 'course_title_{0}'.format(lang)
	query = """
		SELECT a.course_code, a.{0} AS course_title
		FROM (
			SELECT DISTINCT course_code, {0}
			FROM lsr_last_year
			UNION
			SELECT DISTINCT course_code, {0}
			FROM lsr_this_year
		) AS a
		ORDER BY 1 ASC;
	""".format(field_name)
	results = query_mysql(query, dict_=True)
	results_processed = [_dict_clean_course_title(my_dict) for my_dict in results]
	return results_processed


def load_department_codes(lang):
	"""Query list of all department codes and their names as seen
	in the LSR.
	"""
	field_name = 'dept_name_{0}'.format(lang)
	query = """
		SELECT dept_code AS department_code, {0} AS department_name
		FROM departments;
	""".format(field_name)
	results = query_mysql(query, dict_=True)
	results_processed = [_dict_clean_departments(my_dict) for my_dict in results if my_dict['department_code'] not in fields.JUNK_DEPT_CODES]
	# Sort list now that certain departments have been renamed
	results_processed = sorted(results_processed, key=lambda my_dict: my_dict['department_name'])
	return results_processed


def load_training_locations(lang, department_code):
	"""Query names and counts of cities in which a department's learners
	took training.
	"""
	field_name = 'offering_city_{0}'.format(lang)
	# GROUP BY city name as well as latitude and longitude in case cities in
	# different provinces share same name
	# ORDER BY COUNT() DESC so that the largest cities appear and are logged first in func '_combine_overlapping_cities_hashed'
	query = """
		SELECT {0} AS offering_city, offering_lat, offering_lng, COUNT(reg_id) AS count
		FROM lsr_this_year
		WHERE
			billing_dept_code = %s
		AND
			reg_status = 'Confirmed'
		GROUP BY 1, 2, 3
		ORDER BY 4 DESC;
	""".format(field_name)
	results = query_mysql(query, (department_code,), dict_=True)
	
	# Cast any values of dtype 'Decimal' to float so can be JSONified
	results_processed = [_dict_decimal_to_float(my_dict) for my_dict in results]
	# Replace 'None' with empty string for consistency
	results_processed = [_dict_remove_none(my_dict) for my_dict in results]
	# Combine nearby cities to avoid clogging map e.g. Kanata, Vanier -> Ottawa
	results_processed = _combine_overlapping_cities_hashed(results_processed)
	return results_processed


regex = re.compile(pattern=r'[(\[]{0,1}[a-zA-Z]{1}\d{3}[)\]]{0,1}')
def _dict_clean_course_title(my_dict):
	"""Remove course codes and parentheses from titles."""
	my_dict['course_title'] = regex.sub('', my_dict['course_title']).strip()
	return my_dict


def _dict_clean_departments(my_dict):
	"""Remove internal annotations."""
	my_dict['department_name'] = my_dict['department_name'].replace('_archive_', '').replace('_obsolete_', '').replace('_Obsolete_', '').replace('Obsolete_', '')
	return my_dict
