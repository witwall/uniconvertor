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
from copy import deepcopy

from uc2 import _, events, msgconst, uc2const
from uc2.formats.pdxf import const
from uc2.formats.sk1 import sk1const
from uc2.formats.sk1.model import SK1Document, SK1Layout, SK1Grid, SK1Page, \
SK1Layer, SK1MasterLayer, SK1GuideLayer, SK1Guide, SK1Group, SK1MaskGroup, \
SK1Rectangle, SK1Ellipse, SK1Curve, SK1Text, SK1BitmapData, SK1Image, \
get_pdxf_color

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
	obj_style = []

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

		header = self.file.readline()
		self.reset_style()

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
				except:
					print 'error>>', self.line
					errtype, value, traceback = sys.exc_info()
					print errtype, value, traceback

		self.file.close()
		self.position = 0
		return self.model

	def reset_style(self):
		self.obj_style = deepcopy(sk1const.default_style)

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

	def check_stroke(self):
		if not self.obj_style[1]:
			self.obj_style[1] = deepcopy(sk1const.stroke_style)

	#---PROPERTIES
	def gl(self, *args): pass
	def pe(self, *args): pass
	def ps(self, *args): pass
	def pgl(self, *args): pass
	def pgr(self, *args): pass
	def pgc(self, *args): pass
	def phs(self, *args): pass
	def pit(self, *args): pass

	def fp(self, color):
		if not self.obj_style[0] or not self.obj_style[0][1] == const.FILL_SOLID:
			self.obj_style[0] = deepcopy(sk1const.solid_fill)
		fill_style = self.obj_style[0]
		fill_style[2] = get_pdxf_color(color)

	def fe(self):
		self.obj_style[0] = []

	def ft(self, *args): pass
	def lp(self, color):
		self.check_stroke()
		line_style = self.obj_style[1]
		line_style[1] = get_pdxf_color(color)

	def le(self):
		self.obj_style[1] = []

	def lw(self, width):
		self.check_stroke()
		line_style = self.obj_style[1]
		line_style[1] = width

	def lc(self, cap):
		self.check_stroke()
		line_style = self.obj_style[1]
		line_style[4] = cap

	def lj(self, join):
		self.check_stroke()
		line_style = self.obj_style[1]
		line_style[5] = join

	def ld(self, dashes):
		self.check_stroke()
		result = []
		if dashes:
			for item in dashes:
				result.append(item)
		line_style = self.obj_style[1]
		line_style[3] = result

	def la1(self, *args): pass
	def la2(self, *args): pass

	def Fs(self, *args): pass
	def Fn(self, *args): pass
	def dstyle(self, *args): pass
	def style(self, *args): pass

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

	def page(self, name='', format='', size='', orientation=0):
		page = SK1Page(self.config, name, format, size, orientation)
		self.active_page = page
		self.active_layer = None
		self.parent_stack = []
		self.add_object(page, self.model)

	def layer(self, name, p1, p2, p3, p4, layer_color):
		if self.active_page is None:
			self.page()
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
		obj = SK1Rectangle(self.config, trafo, radius1, radius2)
		obj.style = self.obj_style
		self.reset_style()
		self.add_object(obj)

	def e(self, m11, m12, m21, m22, dx, dy, start_angle=None, end_angle=None, arc_type=None):
		trafo = (m11, m12, m21, m22, dx, dy)
		obj = SK1Ellipse(self.config, trafo, start_angle, end_angle, arc_type)
		obj.style = self.obj_style
		self.reset_style()
		self.add_object(obj)

	def b(self):
		self.paths = [[None, [], const.CURVE_OPENED]]
		obj = SK1Curve(self.config, self.paths)
		obj.style = self.obj_style
		self.reset_style()
		self.add_object(obj)

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
		obj = SK1Text(self.config, text, trafo, horiz_align, vert_align, chargap, wordgap, linegap)
		obj.style = self.obj_style
		self.reset_style()
		self.add_object(obj)

	def bm(self, id):
		bmd_obj = SK1BitmapData(self.config, id)
		self.reset_style()
		self.add_object(bmd_obj)
		try:
			bmd_obj.read_data(self.file)
		except:pass
		self.presenter.resources[id] = bmd_obj.raw_image

	def im(self, trafo, id):
		self.reset_style()
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
