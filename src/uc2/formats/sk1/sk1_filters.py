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

from uc2 import _, events, msgconst, uc2const
from uc2.formats.pdxf import const
from uc2.formats.sk1.model import SK1Document, SK1Layout, SK1Grid, SK1Page, \
SK1Layer, SK1MasterLayer, SK1GuideLayer, SK1Guide, SK1Group, SK1MaskGroup, \
SK1Rectangle, SK1Ellipse, SK1Curve, SK1Text, SK1BitmapData, SK1Image

class SK1_Loader:
	name = 'SK1_Loader'
	presenter = None
	config = None
	paths = []
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
			self.file = open(path, 'rb')
		except:
			errtype, value, traceback = sys.exc_info()
			msg = _('Cannot open %s file for writing') % (path)
			events.emit(events.MESSAGES, msgconst.ERROR, msg)
			raise IOError(errtype, msg + '\n' + value, traceback)

		self.add_string(self.file.readline().rstrip('\r\n'))

		while True:
			self.line = self.file.readline()
			if not self.line: break
			self.line = self.line.rstrip('\r\n')
			position = float(self.file.tell()) / float(file_size) * 0.95
			if position - self.position > 0.01:
				self.position = position
				msg = _('Parsing in process...')
				events.emit(events.FILTER_INFO, msg, position)
			if self.line:
				try:
					code = compile('self.' + self.line, '<string>', 'exec')
					exec code
				except:print 'error>>', self.line

		self.file.close()
		self.position = 0
		return self.model

	def add_string(self, string):
		self.string += string + '\n'

	def add_object(self, obj, parent=''):
		if self.model is None:
			self.model = obj
		else:
			if not parent:
				if self.parent_stack:
					parent = self.parent_stack[-1]
				else:
					parent = self.active_layer
			obj.parent = parent
			parent.childs.append(obj)
		if self.line:
			self.add_string(self.line)
		obj.string = self.string
		self.string = ''


	#---PROPERTIES
	def gl(self, *args): self.add_string(self.line)
	def pe(self, *args): self.add_string(self.line)
	def ps(self, *args): self.add_string(self.line)
	def pgl(self, *args): self.add_string(self.line)
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
		self.add_object(SK1Document(self.config))

	def layout(self, *args):
		if len(args) > 2:
			format = args[0]
			size = args[1]
			orientation = args[2]
		else:
			if isinstance(args[0], str):
				format = args[0]
				orientation = args[1]
				if not format in uc2const.PAGE_FORMAT_NAMES: format = 'A4'
				size = uc2const.PAGE_FORMATS[format]
			else:
				format = ''
				size = args[0]
				orientation = args[1]
		obj = SK1Layout(self.config, format, size, orientation)
		self.add_object(obj, self.model)

	def grid(self, grid, visibility, grid_color, layer_name):
		obj = SK1Grid(self.config, grid, visibility, grid_color, layer_name)
		self.add_object(obj, self.model)

	def page(self, name, format, size, orientation):
		page = SK1Page(self.config, name, format, size, orientation)
		self.active_page = page
		self.active_layer = None
		self.parent_stack = []
		self.add_object(page, self.model)

	def layer(self, name, p1, p2, p3, p4, layer_color):
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
		properties = [p1, p2, p3, p4]
		layer = SK1Layer(self.config, name, properties, layer_color)
		self.active_layer = layer
		self.add_object(layer, self.active_page)

	def masterlayer(self, name, p1, p2, p3, p4, layer_color):
		properties = [p1, p2, p3, p4]
		mlayer = SK1MasterLayer(self.config, name, properties, layer_color)
		self.active_layer = mlayer
		self.add_object(mlayer, self.model)

	def guidelayer(self, name, p1, p2, p3, p4, layer_color):
		properties = [p1, p2, p3, p4]
		glayer = SK1GuideLayer(self.config, name, properties, layer_color)
		self.active_layer = glayer
		self.add_object(glayer, self.model)

	def guide(self, point, orientation):
		self.add_object(SK1Guide(self.config))

	#---GROUPS
	def G(self):
		group = SK1Group(self.config)
		self.add_object(group)
		self.parent_stack.append(group)

	def G_(self):
		self.parent_stack = self.parent_stack[:-1]

	def M(self):
		mgroup = SK1MaskGroup(self.config)
		self.add_object(mgroup)
		self.parent_stack.append(mgroup)

	def M_(self):
		self.parent_stack = self.parent_stack[:-1]

	def B(self):
		group = SK1Group(self.config)
		self.string = group.string
		self.line = ''
		self.add_object(group)
		self.parent_stack.append(group)

	def Bi(self, *args):self.string = ''

	def B_(self):
		self.parent_stack = self.parent_stack[:-1]

	def PT(self):
		group = SK1Group(self.config)
		self.string = group.string
		self.line = ''
		self.add_object(group)
		self.parent_stack.append(group)

	def pt(self, *args):self.string = ''

	def PT_(self):
		self.parent_stack = self.parent_stack[:-1]

	def PC(self, *args):
		group = SK1Group(self.config)
		self.string = group.string
		self.line = ''
		self.add_object(group)
		self.parent_stack.append(group)

	def PC_(self):
		self.parent_stack = self.parent_stack[:-1]

	#---PRIMITIVES
	def r(self, m11, m12, m21, m22, dx, dy, radius1=None, radius2=None):
		trafo = (m11, m12, m21, m22, dx, dy)
		self.add_object(SK1Rectangle(self.config, trafo, radius1, radius2))

	def e(self, m11, m12, m21, m22, dx, dy, start_angle=None, end_angle=None, arc_type=None):
		trafo = (m11, m12, m21, m22, dx, dy)
		self.add_object(SK1Ellipse(self.config, trafo, start_angle, end_angle, arc_type))

	def b(self):
		self.paths = [[None, [], const.CURVE_OPENED]]
		self.add_object(SK1Curve(self.config, self.paths))

	def bs(self, x, y, cont):
		point = [x, y]
		path = self.paths[-1]
		points = path[1]
		if path[0] is None:
			path[0] = point
		else:
			points.append(point)

	def bc(self, x1, y1, x2, y2, x3, y3, cont):
		point = [[x1, y1], [x2, y2], [x3, y3], cont]
		path = self.paths[-1]
		points = path[1]
		if path[0] is None:
			path[0] = point
		else:
			points.append(point)

	def bn(self):
		self.paths.append([None, [], const.CURVE_OPENED])

	def bC(self):
		self.paths[-1][2] = const.CURVE_CLOSED

	def txt(self, text, trafo, horiz_align, vert_align, chargap, wordgap, linegap):
		self.add_object(SK1Text(self.config, text, trafo, horiz_align, vert_align, chargap, wordgap, linegap))

	def bm(self, id):
		bmd_obj = SK1BitmapData(self.config, id)
		self.add_object(bmd_obj)
		try:
			bmd_obj.read_data(self.file)
		except:pass
		self.presenter.resources[id] = bmd_obj.raw_image

	def im(self, trafo, id):
		self.add_object(SK1Image(self.config, trafo, id))

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

		presenter.update()
		presenter.model.write_content(file)
		file.close()
