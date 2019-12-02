from registhor_app.db import query_mysql
from registhor_app.utils import _unpack_tuples
from registhor_app.evalhalla_routes.utils import fields


def load_cities(lang):
	"""Return all cities inputted by learners."""
	query = """
		SELECT a.learner_city_{0} AS learner_city, a.learner_province_{0} AS learner_province
		FROM (
			SELECT DISTINCT learner_city_{0}, learner_province_{0}
			FROM lsr_this_year
			UNION
			SELECT DISTINCT learner_city_{0}, learner_province_{0}
			FROM lsr_last_year
		) AS a;
	""".format(lang)
	results = query_mysql(query)
	results_processed = _concatenate_city_and_province(results)
	results_processed = _clean_cities(results_processed)
	results_processed = _remove_duplicates_and_sort(results_processed)
	return results_processed


def load_classifications():
	"""Return all classifications inputted by learners."""
	query = """
		SELECT a.learner_classif
		FROM (
			SELECT DISTINCT learner_classif
			FROM lsr_this_year
			UNION
			SELECT DISTINCT learner_classif
			FROM lsr_last_year
		) AS a;
	"""
	results = query_mysql(query)
	results_processed = _unpack_tuples(results)
	results_processed = _remove_duplicates_and_sort(results_processed)
	return results_processed


def load_departments(lang):
	"""Return all departments inputted by learners."""
	query = """
		SELECT a.billing_dept_name_{0}
		FROM (
			SELECT DISTINCT billing_dept_name_{0}
			FROM lsr_this_year
			UNION
			SELECT DISTINCT billing_dept_name_{0}
			FROM lsr_last_year
		) AS a;
	""".format(lang)
	results = query_mysql(query)
	results_processed = _unpack_tuples(results)
	results_processed = _clean_departments(results_processed)
	results_processed = _remove_duplicates_and_sort(results_processed)
	return results_processed


def _clean_cities(my_list):
	"""Remove junk entries."""
	results_processed = [city for city in my_list if city not in fields.JUNK_CITIES]
	return results_processed


def _clean_departments(my_list):
	"""Remove junk entries and internal annotations."""
	# Store in a set to remove duplicates
	results_processed = []
	for str_ in my_list:
		if str_ not in fields.JUNK_DEPTS:
			str_ = str_.replace('_archive_', '')
			str_ = str_.replace('_obsolete_', '')
			str_ = str_.replace('_Obsolete_', '')
			str_ = str_.replace('Obsolete_', '')
			results_processed.append(str_)
	return results_processed


def _concatenate_city_and_province(my_list):
	"""Concatenate city name and province name into a single string."""
	results_processed = []
	for tup in my_list:
		val = '{0}, {1}'.format(tup[0], tup[1])
		val = val.replace(', Outside Canada', '').replace(', Hors du Canada', '').replace(', Unknown', '').replace(', Iconnu', '')
		results_processed.append(val)
	return results_processed


def _remove_duplicates_and_sort(my_list):
	"""Return sorted array of unique values."""
	# Casting to set removes duplicates
	# Sorting set also casts it back to a list
	return sorted(set(my_list))
