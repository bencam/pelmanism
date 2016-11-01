#!/usr/bin/python

import logging
from google.appengine.ext import ndb
import endpoints

def get_by_urlsafe(urlsafe, model):
	"""Add docstring"""
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
