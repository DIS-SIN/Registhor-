from registhor_app.db import insert_mysql, query_mysql
from registhor_app.registrations_routes.queries.queries import load_course_codes, load_department_codes
from registhor_app.utils import _unpack_tuples


def add_mandatory_course(department_code, course_code):
	"""Insert entry into DB indicating a given department considers a
	given course as mandatory.
	"""
	# Ensure department_code is a valid active department before inserting into DB
	department_code_check = _validate_department_code(department_code)
	if not department_code_check:
		raise LookupError('The department code provided is not for an active department.')
	
	# Ensure course_code is a valid active course before inserting into DB
	course_code_check = _validate_course_code(course_code)
	if not course_code_check:
		raise LookupError('The course code provided is not for an active course.')
	
	statement = """
		INSERT INTO mandatory_courses (
			dept_code,
			course_code
		) VALUES (
			%s,
			%s
		);
	"""
	insert_mysql(statement, (department_code, course_code))


def remove_mandatory_course(department_code, course_code):
	"""Remove entry from DB if a given department no longer considers a
	given course as mandatory.
	"""
	statement = """
		DELETE FROM mandatory_courses
		WHERE
			dept_code = %s
		AND
			course_code = %s;
	"""
	insert_mysql(statement, (department_code, course_code))


def load_mandatory_courses(lang, department_code):
	"""Query all mandatory courses and indicate if the given department
	considers them mandatory for its employees.
	"""
	# Query list of all active courses
	active_courses = load_course_codes(lang)
	
	# Query list of courses marked mandatory by department
	department_courses = _load_mandatory(department_code)
	department_courses = set(_unpack_tuples(department_courses))
	
	# Add boolean field 'mandatory' to course dictionaries indicating if department
	# considers the course mandatory
	for dict_ in active_courses:
		dict_['mandatory'] = True if dict_['course_code'] in department_courses else False
	
	return active_courses


def _load_mandatory(department_code):
	"""Query list of department's mandatory courses."""
	query = """
		SELECT course_code
		FROM mandatory_courses
		WHERE dept_code = %s;
	"""
	results = query_mysql(query, (department_code,))
	return results


def _validate_course_code(course_code):
	"""Check if course_code exists in DB."""
	# Query list of all active courses
	active_courses = load_course_codes('en')
	
	# Convert to set
	active_course_codes = {dict_['course_code'] for dict_ in active_courses}
	
	return True if course_code in active_course_codes else False


def _validate_department_code(department_code):
	"""Check if department_code exists in DB."""
	# Query list of all active departments
	active_departments = load_department_codes('en')
	
	# Convert to set
	active_department_codes = {dict_['department_code'] for dict_ in active_departments}
	
	return True if department_code in active_department_codes else False
