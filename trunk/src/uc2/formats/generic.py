# -*- coding: utf-8 -*-
#
#	Copyright (C) 2012 by Igor E. Novikov
#	
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os

from uc2 import _, uc2const
from uc2 import events, msgconst
from uc2.utils import fs

class ModelObject:
	"""
	Abstract parent class for all model 
	objects. Provides common object properties.
	"""
	cid = 0
	parent = None
	config = None
	childs = []

	def destroy(self):
		for child in self.childs:
			child.destroy()
		fields = self.__dict__
		items = fields.keys()
		for item in items:
			fields[item] = None

	def update(self): pass

	def do_update(self):
		for child in self.childs:
			child.parent = self
			child.config = self.config
			child.do_update()
		self.update()

	def count(self):
		val = len(self.childs)
		for child in self.childs:
			val += child.count()
		return val

	def resolve(self):
		if self.childs: return (False, 'Node', '')
		return (True, 'Leaf', '')

class TextModelObject(ModelObject):

	string = ''

GENERIC_TAGS = ['cid', 'childs', 'parent', 'config', 'tag']
IDENT = '\t'

class TaggedModelObject(ModelObject):

	tag = ''

class BinaryModelObject(ModelObject):

	chunk = ''
	cache_fields = []



class ModelPresenter:
	"""
	Abstract parent class for all model 
	presenters. Provides common functionality.
	"""

	cid = 0
	model_type = uc2const.GENERIC_MODEL
	config = None
	doc_dir = ''
	doc_file = ''
	doc_id = ''
	model = None

	loader = None
	saver = None
	methods = None

	def new(self):pass

	def load(self, path):
		if path and os.path.lexists(path):
			try:
				msg = _('Parsing is started...')
				events.emit(events.FILTER_INFO, msg, 0.03)
				events.emit(events.MESSAGES, msgconst.INFO, msg)
				self.model = self.loader.load(self, path)
			except:
				self.close()
				raise IOError(_('Error while loading') + ' ' + path,
							sys.exc_info()[1], sys.exc_info()[2])

			msg = _('Document model is created')
			events.emit(events.MESSAGES, msgconst.OK, msg)

			self.doc_file = path
		else:
			msg = _('Error while loading:') + ' ' + _('file doesn\'t exist')
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(msg)
		self.update()

	def update(self):
		if not self.model is None:
			msg = _('%s model update...') % (uc2const.FORMAT_NAMES[self.cid])
			events.emit(events.FILTER_INFO, msg , 0.95)
			try:
				self.model.config = self.config
				self.model.do_update()
			except:
				print sys.exc_info()[1], sys.exc_info()[2]
				msg = _('Exception while document model update')
				events.emit(events.MESSAGES, msgconst.ERROR, msg)
				raise IOError(msg)

			msg = _('Document model is updated successfully')
			events.emit(events.FILTER_INFO, msg, 0.98)
			events.emit(events.MESSAGES, msgconst.OK, msg)

	def save(self, path):
		if path:
			self.doc_file = path
			try:
				msg = _('Saving is started...')
				events.emit(events.FILTER_INFO, msg, 0.03)
				events.emit(events.MESSAGES, msgconst.INFO, msg)
				self.saver.save(self, path)
			except:
				msg = _('Error while saving') + ' ' + path
				events.emit(events.MESSAGES, msgconst.ERROR, msg)
				raise IOError(msg, sys.exc_info()[1], sys.exc_info()[2])
		else:
			msg = _('Error while saving:') + ' ' + _('Empty file name')
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(msg)

		msg = _('Document model is saved successfully')
		events.emit(events.FILTER_INFO, msg, 0.95)
		events.emit(events.MESSAGES, msgconst.OK, msg)

	def close(self):
		file = self.doc_file
		self.doc_file = ''
		if not self.model is None:
			self.model.destroy()
		self.model = None

		msg = _('Document model is destroyed for') + ' %s' % (file)
		events.emit(events.MESSAGES, msgconst.OK, msg)

		if self.doc_dir and os.path.lexists(self.doc_dir):
			try:
				fs.xremove_dir(self.doc_dir)
				msg = _('Cache is cleared for') + ' %s' % (file)
				events.emit(events.MESSAGES, msgconst.OK, msg)
			except IOError:
				msg = _('Cache clearing is unsuccessful')
				events.emit(events.MESSAGES, msgconst.ERROR, msg)

class TextModelPresenter(ModelPresenter):

	model_type = uc2const.TEXT_MODEL

class TaggedModelPresenter(ModelPresenter):

	model_type = uc2const.TAGGED_MODEL

class BinaryModelPresenter(ModelPresenter):

	model_type = uc2const.BINARY_MODEL

