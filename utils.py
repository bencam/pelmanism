#!/usr/bin/env python

"""
The utils.py file provides a function which is used in pelmanism_api.py
to retrieve game information.

"""


import logging
from google.appengine.ext import ndb
import endpoints


def get_by_urlsafe(urlsafe, model):
	"""Returns the ndb.model entity that is connected to the urlsafe key;
	checks to ensure that the type of entity returned is of the correct
	kind; raises an error if the key string is (a) incorrect or (b)
	of the wrong kind
	
	Args:
		urlsafe: a urlsafe key string
		model: the expected entity kind
	Returns:
		The entity that is connected to the urlsafe key OR None if
		an entity does not exist
	Raises:
		ValueError"""
	try:
		key = ndb.Key(urlsafe=urlsafe)
	except TypeError:
		raise endpoints.BadRequestException('Invalid Key')
	except Exception, e:
		if e.__class__.__name__ == 'ProtocolBufferDecodeError':
			raise endpoints.BadRequestException('Invalid Key')
		else:
			raise

	entity = key.get()
	if not entity:
		return None
	if not isinstance(entity, model):
		raise ValueError('Incorrect Kind')
	return entity
