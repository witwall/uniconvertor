# -*- coding: utf-8 -*-
#
#	Copyright (C) 2013 by Igor E. Novikov
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

import sys, os

from uc2 import _, events, msgconst
from uc2.formats.sk1.model import SK1Document, SK1Layout, SK1Grid, SK1Page, \
SK1Layer, SK1MasterLayer, SK1GuideLayer, SK1Guide, SK1Group, SK1MaskGroup, \
SK1Rectangle, SK1Ellipse, SK1Curve, SK1Text

class SK1_Loader:
	name = 'SK1_Loader'
	presenter = None
	config = None
	path = None
	options = {}
	model = None

	string = ''
	line = ''
	active_page = None
	active_layer = None
	parent_stack = []

	position = 0

	def __init__(self):
		pass

	def load(self, presenter, path):
		self.presenter = presenter
		self.config = self.presenter.config

		file_size = os.path.getsize(path)
		try:
			file = open(path, 'rb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for writing') % (path)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)

		self.add_string(file.readline().rstrip('\r\n'))

		while True:
			self.line = file.readline()
			if not self.line: break
			self.line = self.line.rstrip('\r\n')
			position = float(file.tell()) / float(file_size) * 0.95
			if position - self.position > 0.01:
				self.position = position
				msg = _('Parsing in process...')
				events.emit(events.FILTER_INFO, msg, position)
			try:
				code = compile('self.' + self.line, '<string>', 'exec')
				exec code
			except:pass

		file.close()
		self.position = 0
		return self.model

	def add_string(self, string):
		self.string += string + '\n'

	def add_object(self, obj, parent=''):
		if not parent:
			if self.parent_stack:
				parent = self.parent_stack[-1]
			else:
				parent = self.active_layer
		if self.line:
			self.add_string(self.line)
		obj.parent = parent
		parent.childs.append(obj)
		obj.string = self.string
		self.string = ''


	#---PROPERTIES
	def gl(self, *args): self.add_string(self.line)
	def pe(self, *args): self.add_string(self.line)
	def ps(self, *args): self.add_string(self.line)
	def pgr(self, *args): self.add_string(self.line)
	def pgc(self, *args): self.add_string(self.line)
	def phs(self, *args): self.add_string(self.line)
	def pit(self, *args): self.add_string(self.line)
	def fp(self, *args): self.add_string(self.line)
	def fe(self, *args): self.add_string(self.line)
	def ft(self, *args): self.add_string(self.line)
	def lp(self, *args): self.add_string(self.line)
	def le(self, *args): self.add_string(self.line)
	def lw(self, *args): self.add_string(self.line)
	def lc(self, *args): self.add_string(self.line)
	def lj(self, *args): self.add_string(self.line)
	def ld(self, *args): self.add_string(self.line)
	def la1(self, *args): self.add_string(self.line)
	def la2(self, *args): self.add_string(self.line)
	def Fs(self, *args): self.add_string(self.line)
	def Fn(self, *args): self.add_string(self.line)
	def dstyle(self, *args): self.add_string(self.line)
	def style(self, *args): self.add_string(self.line)

	#---STRUCTURAL ELEMENTS
	def document(self, *args):
		self.add_string(self.line)
		self.model = SK1Document(self.config)
		self.model.string = self.string
		self.string = ''

	def layout(self, *args):
		self.add_object(SK1Layout(self.config), self.model)

	def grid(self, *args):
		self.add_object(SK1Grid(self.config), self.model)

	def page(self, *args):
		page = SK1Page(self.config)
		self.active_page = page
		self.active_layer = None
		self.parent_stack = []
		self.add_object(page, self.model)

	def layer(self, *args):
		if self.active_page is None:
			page = SK1Page(self.config)
			current_line = self.line
			self.line = ''
			self.string = page.string
			self.active_page = page
			self.active_layer = None
			self.parent_stack = []
			self.add_object(page, self.model)
			self.line = current_line
		layer = SK1Layer(self.config)
		self.active_layer = layer
		self.add_object(layer, self.active_page)

	def masterlayer(self, *args):
		mlayer = SK1MasterLayer(self.config)
		self.active_layer = mlayer
		self.add_object(mlayer, self.model)

	def guidelayer(self, *args):
		glayer = SK1GuideLayer(self.config)
		self.active_layer = glayer
		self.add_object(glayer, self.model)

	def guide(self, *args):
		self.add_object(SK1Guide(self.config))

	#---GROUPS
	def G(self, *args):
		group = SK1Group(self.config)
		self.add_object(group)
		self.parent_stack.append(group)

	def G_(self, *args):
		self.parent_stack = self.parent_stack[:-1]

	def M(self, *args):
		mgroup = SK1MaskGroup(self.config)
		self.add_object(mgroup)
		self.parent_stack.append(mgroup)

	def M_(self, *args):
		self.parent_stack = self.parent_stack[:-1]

	def B(self, *args):
		group = SK1Group(self.config)
		self.string = group.string
		self.line = ''
		self.add_object(group)
		self.parent_stack.append(group)

	def Bi(self, *args):self.string = ''

	def B_(self, *args):
		self.parent_stack = self.parent_stack[:-1]

	def PT(self, *args):
		group = SK1Group(self.config)
		self.string = group.string
		self.line = ''
		self.add_object(group)
		self.parent_stack.append(group)

	def pt(self, *args):self.string = ''

	def PT_(self, *args):
		self.parent_stack = self.parent_stack[:-1]

	def PC(self, *args):
		group = SK1Group(self.config)
		self.string = group.string
		self.line = ''
		self.add_object(group)
		self.parent_stack.append(group)

	def PC_(self, *args):
		self.parent_stack = self.parent_stack[:-1]

	#---PRIMITIVES
	def r(self, *args):
		self.add_object(SK1Rectangle(self.config))

	def e(self, *args):
		self.add_object(SK1Ellipse(self.config))

	def b(self, *args): self.add_string(self.line)
	def bs(self, *args): self.add_string(self.line)
	def bc(self, *args): self.add_string(self.line)
	def bn(self, *args): self.add_string(self.line)
	def bC(self, *args):
		self.add_object(SK1Curve(self.config))

	def txt(self, *args):
		self.add_object(SK1Text(self.config))

	def bm(self, *args):self.string = ''
	def im(self, *args):self.string = ''
	def eps(self, *args):self.string = ''



class SK1_Saver:

	name = 'SK1_Saver'

	def __init__(self):
		pass

	def save(self, presenter, path):

		try:
			file = open(path, 'wb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for writing') % (path)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)

		file.write(presenter.model.get_content())
		file.close()
