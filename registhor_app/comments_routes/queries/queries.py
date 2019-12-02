import pandas as pd
from registhor_app.db import query_mysql
from registhor_app.utils import _unpack_tuples


def load_course_codes(short_question, fiscal_year, department_code):
	"""Return list of course codes that match criteria."""
	query = """
		SELECT DISTINCT course_code
		FROM comments
		WHERE
			short_question = %s
		AND
			(fiscal_year = %s OR %s = '')
		AND
			(learner_dept_code = %s OR %s = '')
		ORDER BY 1 ASC;
	"""
	results = query_mysql(query, (short_question, fiscal_year, fiscal_year, department_code, department_code))
	results_processed = _unpack_tuples(results)
	return results_processed


def load_counts(short_question, course_code, fiscal_year, department_code):
	"""Return number of comments by star for a given short question, course code,
	and fiscal year.
	"""
	query = """
		SELECT stars, COUNT(survey_id)
		FROM comments
		WHERE
			short_question = %s
		AND
			(course_code = %s OR %s = '')
		AND
			(fiscal_year = %s OR %s = '')
		AND
			(learner_dept_code = %s OR %s = '')
		GROUP BY 1;
	"""
	results = query_mysql(query, (short_question, course_code, course_code, fiscal_year, fiscal_year, department_code, department_code))
	results = dict(results)
	# Ensure all stars from 1-5 present in dict
	stars = range(1, 6)
	results_processed = {star: results.get(star, 0) for star in stars}
	return results_processed


def load_comments(short_question, course_code, lang, fiscal_year, department_code, stars, limit, offset):
	"""Return all comments of a given type (e.g. general comments) for a
	given course code.
	"""
	field_name = 'offering_city_{0}'.format(lang)
	query = """
		SELECT text_answer, course_code, learner_classif, {0}, fiscal_year, quarter, overall_satisfaction, stars, magnitude, nanos
		FROM comments
		WHERE
			short_question = %s
		AND
			(course_code = %s OR %s = '')
		AND
			(fiscal_year = %s OR %s = '')
		AND
			(learner_dept_code = %s OR %s = '')
		AND
			(stars = %s OR %s = '')
		ORDER BY 5 DESC, 6 DESC
		LIMIT %s OFFSET %s;
	""".format(field_name)
	results = query_mysql(query, (short_question, course_code, course_code, fiscal_year,
								  fiscal_year, department_code, department_code, stars,
								  stars, int(limit), int(offset)))
	# Munge raw data with Pandas
	results_processed = _munge_comments(results, lang)
	return results_processed


def _munge_comments(raw, lang):
	"""Munge raw data with Pandas and process into form required for API. Return
	False if course has received no comments.
	"""
	# Load raw data into DataFrame
	results = pd.DataFrame(raw, columns=['text_answer', 'course_code', 'learner_classif',
										 'offering_city', 'fiscal_year', 'quarter',
										 'overall_satisfaction', 'stars', 'magnitude', 'nanos'])
	
	# Return False if course has received no feedback
	if results.empty:
		return False
	
	# Account null values in 'overall_satisfaction' and 'stars'
	results['overall_satisfaction'].fillna(0, inplace=True)
	results['stars'].fillna(0, inplace=True)
	
	results_processed = []
	# Unpack tuple as some fields require customization
	for row in results.itertuples(index=False):
		text_answer = row[0]
		course_code = row[1].upper()
		# Account for 'Unknown' being 'Inconnu' in FR
		learner_classif = row[2]
		learner_classif = learner_classif.replace(' - Unknown', '')
		learner_classif = learner_classif.replace('Unknown', 'Inconnu') if lang == 'fr' else learner_classif
		# Account for English vs French title formatting
		offering_city = row[3]
		offering_city = _format_city(offering_city, lang)
		fiscal_year = row[4]
		# Account for e.g. 'Q2' being 'T2' in FR
		quarter = row[5]
		quarter = quarter.replace('Q', 'T') if lang == 'fr' else quarter
		overall_satisfaction = int(row[6])
		stars = int(row[7])
		magnitude = float(row[8])
		nanos = row[9]
		# Reassemble and append
		tup = (text_answer, course_code, learner_classif, offering_city, fiscal_year, quarter,
			   overall_satisfaction, stars, magnitude, nanos)
		results_processed.append(tup)
	return results_processed


def _format_city(my_string, lang):
	"""Correct English and French formatting edge cases."""
	if lang == 'fr':
		s = my_string.title()
		s = s.replace('Région De La Capitale Nationale (Rcn)', 'Région de la capitale nationale (RCN)')
		s = s.replace("En Ligne", "En ligne")
		s = s.replace("'S", "'s")
		return s
	else:
		s = my_string.title()
		s = s.replace('(Ncr)', '(NCR)').replace("'S", "'s")
		return s
