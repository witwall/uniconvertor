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

from copy import deepcopy
import Image

from uc2 import _, uc2const
from uc2.formats.pdxf import const
from uc2.formats.sk1 import sk1const
from uc2.utils import Base64Encode, Base64Decode, SubFileDecode
from uc2.formats.generic import TextModelObject

from _sk1objs import Trafo, CreatePath, Point

# Document object enumeration
DOCUMENT = 1
LAYOUT = 2
GRID = 3
PAGES = 4
PAGE = 5
LAYER = 6
MASTERLAYER = 7
GUIDELAYER = 8
GUIDE = 9

GROUP = 20
MASKGROUP = 21

RECTANGLE = 30
ELLIPSE = 31
CURVE = 32
TEXT = 33
BITMAPDATA = 34
IMAGE = 35

CID_TO_NAME = {
	DOCUMENT: _('Document'), LAYOUT: _('Layout'), GRID: _('Grid'),
	PAGES: _('Pages'), PAGE: _('Page'), LAYER: _('Layer'), MASTERLAYER: _('MasterLayer'),
	GUIDELAYER: _('GuideLayer'), GUIDE: _('Guideline'), GUIDE: _('Guideline'),

	GROUP: _('Group'), MASKGROUP: _('MaskGroup'),

	RECTANGLE:_('Rectangle'), ELLIPSE:_('Ellipse'), CURVE:_('Curve'),
	TEXT:_('Text'), BITMAPDATA:_('BitmapData'), IMAGE:_('Image'),
	}

def get_pdxf_color(clr):
	if not clr: return deepcopy(sk1const.fallback_color)
	color_spec = clr[0]
	if color_spec == sk1const.RGB:
		result = [sk1const.RGB, [clr[1], clr[2], clr[3]], 1.0, '']
		if len(clr) == 5:result[2] = clr[4]
		return result
	elif color_spec == sk1const.CMYK:
		result = [sk1const.CMYK, [clr[1], clr[2], clr[3], clr[4]], 1.0, '']
		if len(clr) == 6:result[2] = clr[5]
		return result
	elif color_spec == sk1const.SPOT:
		result = [sk1const.SPOT, [[clr[3], clr[4], clr[5]],
					[clr[6], clr[7], clr[8], clr[9]], clr[1]], 1.0, clr[2]]
		if len(clr) == 11:result[2] = clr[10]
		return result
	else:
		return deepcopy(sk1const.fallback_color)

def get_sk1_color(clr):
	if not clr: return deepcopy(sk1const.fallback_sk1color)
	color_spec = clr[0]
	val = clr[1]
	alpha = clr[2]
	name = clr[3]
	if color_spec == sk1const.RGB:
		if clr[2] == 1.0:
			result = (sk1const.RGB, val[0], val[1], val[2])
		else:
			result = (sk1const.RGB, val[0], val[1], val[2], alpha)
		return result
	elif color_spec == sk1const.CMYK:
		if clr[2] == 1.0:
			result = (sk1const.CMYK, val[0], val[1], val[2], val[3])
		else:
			result = (sk1const.CMYK, val[0], val[1], val[2], val[3], alpha)
		return result
	elif color_spec == sk1const.SPOT:
		rgb = val[0]
		cmyk = val[1]
		pal = val[2]
		if clr[2] == 1.0:
			result = (sk1const.SPOT, pal, clr[3], rgb[0], rgb[1], rgb[2],
					cmyk[0], cmyk[1], cmyk[2], cmyk[3])
		else:
			result = (sk1const.SPOT, pal, name, rgb[0], rgb[1], rgb[2],
					cmyk[0], cmyk[1], cmyk[2], cmyk[3], alpha)
		return result
	else:
		return deepcopy(sk1const.fallback_sk1color)

class SK1ModelObject(TextModelObject):
	"""
	Abstract class for SK1 model objects.
	Defines common object functionality
	"""

	objects = []

	def __init__(self, config=None, string=''):
		self.config = config
		self.childs = []
		self.objects = self.childs
		if string:
			self.string = string

	def resolve(self):
		is_leaf = True
		if self.cid < RECTANGLE: is_leaf = False
		if self.cid == GUIDE or self.cid == LAYOUT: is_leaf = True
		name = CID_TO_NAME[self.cid]
		info = ''
		if not is_leaf: info = len(self.childs)
		return (is_leaf, name, info)

	def get_content(self):
		result = '' + self.string
		for child in self.childs:
			result += child.get_content()
		if self.end_string:
			result += self.end_string
		return result

	def write_content(self, file):
		file.write(self.string)
		for child in self.childs:
			child.write_content(file)
		if self.end_string:
			file.write(self.end_string)

#--- STRUCTURAL OBJECTS

class SK1Document(SK1ModelObject):
	"""
	Represents SK1 model root object.
	"""

	string = '##sK1 1 2\ndocument()\n'
	cid = DOCUMENT
	layout = None
	pages = None
	grid = None
	masterlayer = None
	guidelayer = None

	def __init__(self, config):
		SK1ModelObject.__init__(self, config)

class SK1Layout(SK1ModelObject):
	"""
	Represents Layout object.
	The object defines default page size as:
	(format_name,(width,height),orientation)
	"""

	string = "layout('A4',(595.276,841.89),0)\n"
	cid = LAYOUT
	format = 'A4'
	size = uc2const.PAGE_FORMATS['A4']
	orientation = uc2const.PORTRAIT

	def __init__(self, config, format='', size=(), orientation=uc2const.PORTRAIT):
		if format: self.format = format
		if size: self.size = size
		if orientation: self.orientation = orientation
		SK1ModelObject.__init__(self, config)

	def update(self):
		args = (self.format, self.size, self.orientation)
		self.string = 'layout' + args.__str__() + '\n'

class SK1Grid(SK1ModelObject):
	"""
	Represents Grid layer object.
	Grid values are defined as:
	(grid,visibility,grid_color,layer_name)
	where:
	grid=(start_x, start_y, dx, dy)
	grid_color=(colorspace,color values)
	"""
	string = 'grid((0,0,2.83465,2.83465),0,("RGB",0.83,0.87,0.91),\'Grid\')\n'
	cid = GRID
	grid = sk1const.default_grid
	visibility = 0
	grid_color = sk1const.default_grid_color
	layer_name = 'Grid'

	def __init__(self, config, grid=(), visibility=0, grid_color=(), layer_name=''):
		if grid:self.grid = grid
		if visibility:self.visibility = visibility
		if grid_color:self.grid_color = get_pdxf_color(grid_color)
		if layer_name:self.layer_name = layer_name
		SK1ModelObject.__init__(self, config)

	def update(self):
		color = get_sk1_color(self.grid_color)
		args = (self.grid, self.visibility, color, self.layer_name)
		self.string = 'grid' + args.__str__() + '\n'

class SK1Pages(SK1ModelObject):
	"""
	Represents container for Page objects.
	Has no any values and used to be a childs list holder.
	"""
	cid = PAGES

	def __init__(self):
		SK1ModelObject.__init__(self)

	def write_content(self, file):
		for child in self.childs:
			child.write_content(file)

class SK1Page(SK1ModelObject):
	"""
	Represents Page object.
	Page values are defined as:
	(page_name,format_name,(width,height),orientation)
	"""
	string = "page('','A4',(595.276,841.89),0)\n"
	cid = PAGE
	name = ''
	format = 'A4'
	size = uc2const.PAGE_FORMATS['A4']
	orientation = uc2const.PORTRAIT

	def __init__(self, config, name='', format='', size=(), orientation=uc2const.PORTRAIT):
		if name:self.name = name
		if format:self.format = format
		if size:self.size = size
		if orientation:self.orientation = orientation
		SK1ModelObject.__init__(self, config)

	def update(self):
		args = (self.name, self.format, self.size, self.orientation)
		self.string = 'page' + args.__str__() + '\n'

class SK1Layer(SK1ModelObject):
	"""
	Represents Layer object.
	Layer values are defined as:
	(layer_name,visible,printable,locked,outlined,layer_color)
	"""
	string = "layer('Layer 1',1,1,0,0,(\"RGB\",0.196,0.314,0.635))\n"
	cid = LAYER
	name = ''
	layer_properties = []
	layer_color = sk1const.default_layer_color

	def __init__(self, config, name='', properties=[], layer_color=()):
		if name:self.name = name
		if properties:
			self.layer_properties = properties
		else:
			self.layer_properties = [] + sk1const.default_layer_properties
		if layer_color: self.layer_color = get_pdxf_color(layer_color)
		SK1ModelObject.__init__(self, config)

	def update(self):
		color = get_sk1_color(self.layer_color)
		p1, p2, p3, p4 = self.layer_properties
		args = (self.name, p1, p2, p3, p4, color)
		self.string = 'layer' + args.__str__() + '\n'

class SK1MasterLayer(SK1ModelObject):
	"""
	Represents MasterLayer object.
	Layer values are defined as:
	(layer_name,visible,printable,locked,outlined,layer_color)
	"""
	string = "masterlayer('MasterLayer 1',1,1,0,0,(\"RGB\",0.196,0.314,0.635))\n"
	cid = MASTERLAYER
	name = ''
	layer_properties = []
	layer_color = sk1const.default_layer_color

	def __init__(self, config, name='', properties=[], layer_color=()):
		if name:self.name = name
		if properties:
			self.layer_properties = properties
		else:
			self.layer_properties = [] + sk1const.default_layer_properties
		if layer_color: self.layer_color = get_pdxf_color(layer_color)
		SK1ModelObject.__init__(self, config)

	def update(self):
		color = get_sk1_color(self.layer_color)
		p1, p2, p3, p4 = self.layer_properties
		args = (self.name, p1, p2, p3, p4, color)
		self.string = 'masterlayer' + args.__str__() + '\n'

class SK1GuideLayer(SK1ModelObject):
	"""
	Represents GuideLayer object.
	Layer values are defined as:
	(layer_name,visible,printable,locked,outlined,layer_color)
	"""
	string = "guidelayer('Guide Lines',1,0,0,1,(\"RGB\",0.0,0.3,1.0))\n"
	cid = GUIDELAYER
	name = 'Guides'
	layer_properties = []
	layer_color = sk1const.default_guidelayer_color

	def __init__(self, config, name='', properties=[], layer_color=()):
		if name:self.name = name
		if properties:
			self.layer_properties = properties
		else:
			self.layer_properties = [] + sk1const.default_guidelayer_properties
		if layer_color: self.layer_color = get_pdxf_color(layer_color)
		SK1ModelObject.__init__(self, config)

	def update(self):
		color = get_sk1_color(self.layer_color)
		p1, p2, p3, p4 = self.layer_properties
		args = (self.name, p1, p2, p3, p4, color)
		self.string = 'guidelayer' + args.__str__() + '\n'

class SK1Guide(SK1ModelObject):
	"""
	Represents Guideline object.
	Guideline values are defined as:
	(point,orientation)
	"""
	string = "guide((0.0,0.0),0)\n"
	cid = GUIDE
	position = 0
	orientation = uc2const.HORIZONTAL

	def __init__(self, config, point=(), orientation=uc2const.HORIZONTAL):
		if point:
			if orientation == uc2const.VERTICAL:
				self.position = point[0]
			else:
				self.position = point[1]
		self.orientation = orientation
		SK1ModelObject.__init__(self, config)

	def update(self):
		if self.orientation == uc2const.VERTICAL:
			point = (self.position, 0.0)
		else:
			point = (0.0, self.position)
		args = (point, self.orientation)
		self.string = 'guide' + args.__str__() + '\n'

#--- SELECTABLE OBJECTS

class SK1Group(SK1ModelObject):
	"""
	Represents Group object.
	All nested objects are in childs list.
	"""
	string = 'G()\n'
	end_string = 'G_()\n'
	cid = GROUP

	def __init__(self, config):
		SK1ModelObject.__init__(self, config)

class SK1MaskGroup(SK1ModelObject):
	"""
	Represents MaskGroup object.
	All nested objects are in childs list.
	The first object in childs list is the mask.
	"""
	string = 'M()\n'
	end_string = 'M_()\n'
	cid = MASKGROUP

	def __init__(self, config):
		SK1ModelObject.__init__(self, config)

#BlendGroup
#TextOnPath
#CompoundObject

#--- Primitive objects

class Rectangle(SK1ModelObject):
	"""
	Represents Rectangle object.
	r(TRAFO [, RADIUS1, RADIUS2])
	"""
	string = ''
	cid = RECTANGLE
	style = []
	properties = None
	trafo = None
	radius1 = 0
	radius2 = 0

	is_Rectangle = 1

	def __init__(self, trafo=None, radius1=0, radius2=0,
					properties=None, duplicate=None):

		if trafo is not None and trafo.m11 == trafo.m21 == trafo.m12 == trafo.m22 == 0:
			trafo = Trafo(1, 0, 0, -1, trafo.v1, trafo.v2)
		self.trafo = trafo
		self.radius1 = radius1
		self.radius2 = radius2
		self.properties = properties
		SK1ModelObject.__init__(self)

	def update(self):
		if self.radius1 == self.radius2 == 0:
			args = self.trafo.coeff()
			self.string = 'r' + args.__str__() + '\n'
		else:
			args = self.trafo.coeff() + (self.radius1, self.radius2)
			self.string = 'r' + args.__str__() + '\n'

class Ellipse(SK1ModelObject):
	"""
	Represents Ellipse object.
	e(TRAFO, [start_angle, end_angle, arc_type])
	"""
	string = ''
	cid = ELLIPSE
	style = []
	properties = None
	trafo = None
	start_angle = 0.0
	end_angle = 0.0
	arc_type = sk1const.ArcPieSlice

	is_Ellipse = 1

	def __init__(self, trafo=None, start_angle=0.0, end_angle=0.0,
					arc_type=sk1const.ArcPieSlice, properties=None,
					duplicate=None):

		if trafo is not None and trafo.m11 == trafo.m21 == trafo.m12 == trafo.m22 == 0:
			trafo = Trafo(1, 0, 0, -1, trafo.v1, trafo.v2)
		self.trafo = trafo
		self.start_angle = start_angle
		self.end_angle = end_angle
		self.arc_type = arc_type
		self.properties = properties
		SK1ModelObject.__init__(self)

	def update(self):
		if self.start_angle == self.end_angle:
			args = self.trafo.coeff()
			self.string = 'e' + args.__str__() + '\n'
		else:
			args = self.trafo.coeff() + (self.start_angle, self.end_angle, self.arc_type)
			self.string = 'e' + args.__str__() + '\n'

class PolyBezier(SK1ModelObject):
	"""
	Represents Bezier curve object.
	b()             start a bezier obj
	bs(X, Y, CONT)  append a line segment
	bc(X1, Y1, X2, Y2, X3, Y3, CONT)  append a bezier segment
	bn()	        start a new path
	bC()            close path
	"""
	string = ''
	cid = CURVE
	style = []
	properties = None
	paths = ()

	is_Bezier	 = 1

	def __init__(self, paths=None, properties=None, duplicate=None, paths_list=[]):
		if paths:
			if isinstance(paths, tuple):
				self.paths = paths
			elif isinstance(paths, list):
				self.paths = tuple(paths)
			else:
				self.paths = (CreatePath(),)
		else:
			self.paths = None
		self.properties = properties
		self.paths_list = paths_list
		SK1ModelObject.__init__(self)

	def set_paths_from_list(self):
		paths = []
		for path in self.paths_list:
			p = CreatePath()
			p.AppendLine(Point(*path[0]))
			points = path[1]
			for point in points:
				if len(point) == 2:
					p.AppendLine(Point(*point))
				else:
					point0 = Point(*point[0])
					point1 = Point(*point[1])
					point2 = Point(*point[2])
					p.AppendBezier(point0, point1, point2, point[3])
			if path[2]:
				p.ClosePath()
			paths.append(p)
		self.paths = tuple(paths)

	def get_line_point(self, x, y, arg):
		return [x, y]

	def get_segment_point(self, x0, y0, x1, y1, x2, y2, cont):
		return [[x0, y0], [x1, y1], [x2, y2], cont]

	def set_list_from_paths(self):
		self.paths_list = []
		for path in self.paths:
			path_list = [None, [], const.CURVE_OPENED]
			list = path.get_save()
			points = path_list[1]
			start = True
			for item in list:
				if len(item) == 3:
					point = self.get_line_point(*item)
					if start:
						start = False
						path_list[0] = point
					else:
						points.append(point)
				elif len(item) == 7:
					points.append(self.get_segment_point(*item))
			if path.closed:path_list[2] = const.CURVE_CLOSED
			self.paths_list.append(path_list)

	def add_line(self, point):
		x, y = point
		self.string += 'bs' + (x, y, 0).__str__() + '\n'

	def add_segment(self, point):
		point0, point1, point2, cont = point
		args = (point0[0], point0[1], point1[0], point1[1], point2[0], point2[1], cont)
		self.string += 'bc' + args.__str__() + '\n'

	def update_from_list(self):
		self.string = 'b()\n'
		start = True
		for path in self.paths:
			if start:
				start = False
			else:
				self.string += 'bn()\n'
			self.add_line(path[0])
			for point in path[1]:
				if len(point) == 2:
					self.add_line(point)
				else:
					self.add_segment(point)
			if path[2] == const.CURVE_CLOSED:
				self.string += 'bC()\n'

	def update(self):
		if self.paths and not self.paths_list:
			self.set_list_from_paths()
		if self.paths_list and not self.paths:
			self.set_paths_from_list()
		self.update_from_list()


class SK1Curve(SK1ModelObject):
	"""
	Represents Bezier curve object.
	b()             start a bezier obj
	bs(X, Y, CONT)  append a line segment
	bc(X1, Y1, X2, Y2, X3, Y3, CONT)  append a bezier segment
	bn()	        start a new path
	bC()            close path
	"""
	string = ''
	cid = CURVE
	style = []
	paths = []

	def __init__(self, config, paths):
		self.paths = paths
		SK1ModelObject.__init__(self, config)

	def add_line(self, point):
		x, y = point
		self.string += 'bs' + (x, y, 0).__str__() + '\n'

	def add_segment(self, point):
		point0, point1, point2, cont = point
		args = (point0[0], point0[1], point1[0], point1[1], point2[0], point2[1], cont)
		self.string += 'bc' + args.__str__() + '\n'

	def update(self):
		self.string = 'b()\n'
		start = True
		for path in self.paths:
			if start:
				start = False
			else:
				self.string += 'bn()\n'
			self.add_line(path[0])
			for point in path[1]:
				if len(point) == 2:
					self.add_line(point)
				else:
					self.add_segment(point)
			if path[2] == const.CURVE_CLOSED:
				self.string += 'bC()\n'

class SK1Text(SK1ModelObject):
	"""
	Represents Text object.
	txt(TEXT, TRAFO[, HORIZ_ALIGN, VERT_ALIGN])
	"""
	string = ''
	cid = TEXT
	style = []
	text = ''
	trafo = ()
	horiz_align = None
	vert_align = None
	chargap = None
	wordgap = None
	linegap = None

	def __init__(self, config, text, trafo, horiz_align, vert_align, chargap, wordgap, linegap):
		self.text = text
		self.trafo = trafo
		self.horiz_align = horiz_align
		self.vert_align = vert_align
		self.chargap = chargap
		self.wordgap = wordgap
		self.linegap = linegap
		SK1ModelObject.__init__(self, config)

	def update(self):
		args = (self.text, self.trafo, self.horiz_align, self.vert_align,
			self.chargap, self.wordgap, self.linegap)
		self.string = 'txt' + args.__str__() + '\n'


class SK1BitmapData(SK1ModelObject):
	"""
	Bitmap image data. Object is defined as:
	
	bm(ID)	
	
	The bitmap data follows as a base64 encoded JPEG file.
	"""
	string = ''
	cid = BITMAPDATA
	raw_image = None
	id = ''

	def __init__(self, config, id=''):
		if id: self.id = id
		SK1ModelObject.__init__(self, config)

	def read_data(self, file):
		decoder = Base64Decode(SubFileDecode(file, '-'))
		self.raw_image = Image.open(decoder)
		self.raw_image.load()

	def update(self):
		self.string = 'bm(%i)\n' % (self.id)
		self.end_string = '-\n'

	def write_content(self, file):
		file.write(self.string)
		vfile = Base64Encode(file)
		if self.raw_image.mode == "CMYK":
			self.raw_image.save(vfile, 'JPEG', quality=100)
		else:
			self.raw_image.save(vfile, 'PNG')
		vfile.close()
		file.write(self.end_string)


class SK1Image(SK1ModelObject):
	"""
	Image object. ID has to be the id of a previously defined
	bitmap data object (defined by bm). The object is defined as:
	im(TRAFO, ID)
	"""
	string = ''
	cid = IMAGE
	trafo = ()
	id = ''
	image = None

	def __init__(self, trafo=None, id='', image=None):
		self.trafo = trafo
		self.id = id
		self.image = image
		SK1ModelObject.__init__(self)

	def update(self):
		if self.image and not self.id:
			self.id = id(self.image)
		self.string = 'im' + (self.trafo.coeff(), self.id).__str__() + '\n'

	def write_content(self, file):
		if self.image:
			file.write('bm(%i)\n' % (self.id))
			vfile = Base64Encode(file)
			if self.raw_image.mode == "CMYK":
				self.raw_image.save(vfile, 'JPEG', quality=100)
			else:
				self.raw_image.save(vfile, 'PNG')
			vfile.close()
			file.write('-\n')
			file.write(self.string)
