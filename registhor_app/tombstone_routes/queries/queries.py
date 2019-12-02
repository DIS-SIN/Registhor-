from registhor_app.db import query_mysql


def load_attr(course_attr, course_code):
	"""Return tombstone information for a given course code."""
	query = """
		SELECT {0}
		FROM product_info
		WHERE course_code = %s
		LIMIT 1;
	""".format(course_attr)
	results = query_mysql(query, (course_code,))
	# String returned inside a tuple inside a list
	if not results or not results[0][0]:
		return ''
	return results[0][0]


def load_all_attrs(course_code):
	"""Return all tombstone information for a given course code."""
	query = """
		SELECT *
		FROM product_info
		WHERE course_code = %s
		LIMIT 1;
	"""
	results = query_mysql(query, (course_code,), dict_=True)
	return results[0]
