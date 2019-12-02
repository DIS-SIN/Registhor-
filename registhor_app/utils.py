import datetime
import decimal
import os
from functools import wraps
from flask import jsonify, request


def check_api_key(f):
	"""Check if API key passed, else return error."""
	@wraps(f)
	def decorated(*args, **kwargs):
		key = request.args.get('key', None)
		if key:
			if key == os.environ.get('REGISTHOR_API_KEY'):
				return f(*args, **kwargs)
			return _invalid_key()
		return _missing_key()
	return decorated


def _invalid_key():
	"""If API key invalid, return error and empty array."""
	results = {
		"error_message": "The provided API key is invalid.",
		"results": [],
		"status": "REQUEST_DENIED"
	}
	return jsonify(results), 403


def _missing_key():
	"""If API key not passed, return error and empty array."""
	results = {
		"error_message": "You must use an API key to authenticate each request to Registhor.",
		"results": [],
		"status": "REQUEST_DENIED"
	}
	return jsonify(results), 403


def _invalid_args(message):
	"""If required arguments invalid, return error and empty array."""
	results = {
		"error_message": "Error: {0}".format(message),
		"results": [],
		"status": "INVALID_REQUEST"
	}
	return jsonify(results), 406


def _missing_args(missing):
	"""If required arguments not passed, return error and empty array."""
	results = {
		"error_message": "Invalid request. Missing one or more arguments: {0}".format(str(missing)),
		"results": [],
		"status": "INVALID_REQUEST"
	}
	return jsonify(results), 400


def _valid_delete():
	"""If DELETE ran successfully, return status 'OK'."""
	results_processed = {
		"status": "OK"
	}
	return jsonify(results_processed), 200


def _valid_get(results):
	"""If query ran successfully, return results."""
	results_processed = {
		"results": results,
		"status": "OK"
	}
	return jsonify(results_processed), 200


def _valid_post():
	"""If POST ran successfully, return status 'OK'."""
	results_processed = {
		"status": "OK"
	}
	return jsonify(results_processed), 200


def _invalid_delete():
	"""If DELETE ran unsuccessfully, return status 'UNPROCESSABLE ENTITY'."""
	results_processed = {
		"status": "UNPROCESSABLE ENTITY"
	}
	return jsonify(results_processed), 422


def _invalid_get():
	"""If GET ran unsuccessfully, return status 'NOT_FOUND'."""
	results_processed = {
		"status": "NOT FOUND"
	}
	return jsonify(results_processed), 404


def _invalid_post():
	"""If POST ran unsuccessfully, return status 'UNPROCESSABLE ENTITY'."""
	results_processed = {
		"status": "UNPROCESSABLE ENTITY"
	}
	return jsonify(results_processed), 422


def _dict_decimal_to_float(my_dict):
	"""If any values in dictionary are of dtype 'Decimal', cast
	to float so can be JSONified.
	"""
	for key, val in my_dict.items():
		if isinstance(val, decimal.Decimal):
			my_dict[key] = float(val)
	return my_dict


def _dict_remove_none(my_dict):
	"""If any values in dictionary are of dtype 'None', replace with
	an empty string. Used for consistency in results: don't want to have a mix
	of empty strings (e.g. from empty string in DB) and 'None' (e.g. from a LEFT OUTER JOIN).
	"""
	for key, val in my_dict.items():
		if val is None:
			my_dict[key] = ''
	return my_dict


def _dict_fix_dates(my_dict):
	"""Convert values of keys 'start_date' and 'end_date' to proper ISO
	date format."""
	for key, val in my_dict.items():
		if key in ['start_date', 'end_date']:
			my_dict[key] = val.isoformat()
	return my_dict


# If offering has more than n confirmed registrations, it will remain
# on the books and not be cancelled
# Current rule-of-thumb is 10; decided by Programs team at Asticou
CONFIRMED_COUNT_THRESHOLD = 10
COLOR_DICT = {
	'GREEN': '#d4edda',
	'GREY': '#ddd',
	'ORANGE': '#fff3cd',
	'RED': '#f8d7da'
}


def _assign_background_color(start_date, end_date, confirmed_count, offering_status):
	"""Assign offerings a background colour given their start date, number of
	confirmed registrations, and status.
	"""
	# Use date, rather than datetime, objects for easy comparison and no issues
	# with timezones
	start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
	end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
	current_date = datetime.date.today()
	thirty_days_from_now = current_date + datetime.timedelta(days=30)
	# If offering has been cancelled, red
	# Place this before date check to properly display past offerings that were cancelled
	if offering_status == 'Cancelled - Normal':
		return COLOR_DICT['RED']
	# If offering has already taken place, grey
	if end_date < current_date:
		return COLOR_DICT['GREY']
	# If offering more than a month away or has more than 10 confirmed registrations, green
	if (start_date >= thirty_days_from_now) or (confirmed_count >= CONFIRMED_COUNT_THRESHOLD):
		return COLOR_DICT['GREEN']
	# Else, orange
	return COLOR_DICT['ORANGE']


def _dict_assign_background_color(my_dict):
	"""Add background colour to dict."""
	background_color = _assign_background_color(my_dict['start_date'], my_dict['end_date'], my_dict['confirmed_count'], my_dict['offering_status'])
	my_dict['background_color'] = background_color
	return my_dict


def _dict_fix_lang(my_dict, lang):
	"""Fix French edge cases."""
	BUSINESS_TYPE_MAP = {
		'Events': 'Événement',
		'Instructor-Led': 'Salle de classe'
	}
	OFFERING_LANGUAGE_MAP = {
		'Bilingual': 'Bilingue',
		'English': 'Anglais',
		'French': 'Français'
	}
	OFFERING_STATUS_MAP = {
		'Cancelled - Normal': 'Annulée',
		'Delivered - Normal': 'Livrée',
		'Open - Normal': 'Ouverte'
	}
	if lang == 'fr':
		my_dict['business_type'] = BUSINESS_TYPE_MAP[my_dict['business_type']]
		my_dict['offering_language'] = OFFERING_LANGUAGE_MAP[my_dict['offering_language']]
		my_dict['offering_status'] = OFFERING_STATUS_MAP[my_dict['offering_status']]
	return my_dict


def _unpack_tuples(my_list):
	"""Convert from a list of tuples containing one string each to
	simply a list of strings.
	"""
	results_processed = [tup[0] for tup in my_list]
	return results_processed


def _combine_overlapping_cities_hashed(my_list):
		"""If two cities' markers overlap, combine them into a single entry.
		
		Explanation: Use latitude and longitude rounded to N_DIGITS to create
		a PKEY for each city. Rounding will cause nearby cities to have the
		same PKEY.
		
		Largest city chosen: As SQL queries make use of 'ORDER BY COUNT() DESC',
		the largest cities appear and be logged first. This means that e.g. 2
		occurrences of Kanata will be merged into Ottawa's 30 occurrences.
		"""
		N_DIGITS = 1
		merge_dict = {}
		for dict_ in my_list:
			city_name = dict_['offering_city']
			count = dict_['count']
			# Python's 'round' internal func uses technique 'round half to even'
			# https://en.wikipedia.org/wiki/Rounding#Round_half_to_even
			lat = round(dict_['offering_lat'], N_DIGITS) if dict_['offering_lat'] != '' else ''
			lng = round(dict_['offering_lng'], N_DIGITS) if dict_['offering_lng'] != '' else ''
			pkey = str(lat) + str(lng)
			# If the city lacks lat, lng values (e.g. a webcast), use the city name as its pkey
			pkey = pkey if pkey != '' else city_name
			# Log first occurrence
			if pkey not in merge_dict:
				# Log non-rounded values for maximum accuracy
				merge_dict[pkey] = dict_
			# If lat/lng already logged, combine cities
			else:
				merge_dict[pkey]['count'] += count
		# Return merge_dict's values in list
		results = [value for value in merge_dict.values()]
		return results
