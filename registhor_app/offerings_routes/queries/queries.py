from registhor_app.db import query_mysql
from registhor_app.utils import (_combine_overlapping_cities_hashed, _dict_decimal_to_float,
	_dict_remove_none, _dict_fix_dates, _dict_assign_background_color, _dict_fix_lang)


def load_offering_info(date_1, date_2, offering_status, course_code, instructor_name, business_line, clients_only, limit, offset, lang):
	"""Return info for all offerings matching user criteria."""
	# Add percent signs to var 'instructor_name' for LIKE statement
	instructor_name = '{0}{1}{0}'.format('%', instructor_name)
	
	# Add clause to see only client requests
	clients_only = "AND (a.client != '')" if clients_only == 'true' else ''
	
	query = """
		SELECT a.offering_id, a.course_title_{0} AS course_title, a.course_code, a.instructor_names,
			a.confirmed_count, a.cancelled_count, a.waitlisted_count, a.no_show_count, a.business_type,
			a.event_description, a.start_date, a.end_date, c.business_line_{0} AS business_line,
			a.client AS client_dept_code, b.dept_name_{0} AS client_dept_name, a.offering_status,
			a.offering_language, a.offering_region_{0} AS offering_region, a.offering_province_{0} AS offering_province,
			a.offering_city_{0} AS offering_city, a.offering_lat, a.offering_lng
		FROM offerings AS a
		LEFT OUTER JOIN departments AS b
		ON a.client = b.dept_code
		LEFT OUTER JOIN product_info AS c
		ON a.course_code = c.course_code
		WHERE
			(
				(a.start_date BETWEEN %s AND %s)
				OR
				(a.end_date BETWEEN %s AND %s)
				OR
				(a.start_date <= %s AND a.end_date >= %s)
			)
			AND a.offering_status IN (%s, %s, %s)
			AND (a.course_code = %s OR %s = '')
			AND (a.instructor_names LIKE %s OR %s = '%%')
			AND (c.business_line_{0} = %s OR %s = '')
			{1}
		ORDER BY 20 ASC, 3 ASC
		LIMIT %s OFFSET %s;
	""".format(lang, clients_only)
	results = query_mysql(query, (date_1, date_2, date_1, date_2, date_1, date_2, offering_status[0], offering_status[1],
								  offering_status[2], course_code, course_code, instructor_name,
								  instructor_name, business_line, business_line, int(limit), int(offset)), dict_=True)
	# Cast any values of dtype 'Decimal' to float so can be JSONified
	results_processed = [_dict_decimal_to_float(my_dict) for my_dict in results]
	# Replace 'None' with empty string for consistency
	results_processed = [_dict_remove_none(my_dict) for my_dict in results]
	# Fix date formats = use standard ISO format
	results_processed = [_dict_fix_dates(my_dict) for my_dict in results]
	# Add background colours
	# Processing Python-side for consistency as dates as implementation-specific in JS
	results_processed = [_dict_assign_background_color(my_dict) for my_dict in results]
	# Fix French edge cases
	results_processed = [_dict_fix_lang(my_dict, lang) for my_dict in results]
	return results_processed


def load_offering_counts(date_1, date_2, offering_status, course_code, instructor_name, business_line, clients_only, lang):
	"""Return counts by city for all offerings matching user criteria."""
	# Add percent signs to var 'instructor_name' for LIKE statement
	instructor_name = '{0}{1}{0}'.format('%', instructor_name)
	
	# Add clause to see only client requests
	clients_only = "AND (a.client != '')" if clients_only == 'true' else ''
	
	# GROUP BY city name as well as latitude and longitude in case cities in
	# different provinces share same name
	# ORDER BY COUNT() DESC so that the largest cities appear and are logged first in func '_combine_overlapping_cities_hashed'
	query = """
		SELECT a.offering_city_{0} AS offering_city, a.offering_lat, a.offering_lng, COUNT(a.offering_id) AS count
		FROM offerings AS a
		LEFT OUTER JOIN product_info AS c
		ON a.course_code = c.course_code
		WHERE
			(
				(a.start_date BETWEEN %s AND %s)
				OR
				(a.end_date BETWEEN %s AND %s)
				OR
				(a.start_date <= %s AND a.end_date >= %s)
			)
			AND a.offering_status IN (%s, %s, %s)
			AND (a.course_code = %s OR %s = '')
			AND (a.instructor_names LIKE %s OR %s = '%%')
			AND (c.business_line_{0} = %s OR %s = '')
			{1}
		GROUP BY 1, 2, 3
		ORDER BY 4 DESC;
	""".format(lang, clients_only)
	results = query_mysql(query, (date_1, date_2, date_1, date_2, date_1, date_2, offering_status[0], offering_status[1],
								  offering_status[2], course_code, course_code, instructor_name,
								  instructor_name, business_line, business_line), dict_=True)
	# Cast any values of dtype 'Decimal' to float so can be JSONified
	results_processed = [_dict_decimal_to_float(my_dict) for my_dict in results]
	# Replace 'None' with empty string for consistency
	results_processed = [_dict_remove_none(my_dict) for my_dict in results]
	# Combine nearby cities to avoid clogging map e.g. Kanata, Vanier -> Ottawa
	results_processed = _combine_overlapping_cities_hashed(results_processed)
	return results_processed
