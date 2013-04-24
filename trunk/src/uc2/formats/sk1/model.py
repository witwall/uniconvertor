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

from uc2 import _
from uc2.formats.generic import TextModelObject

# Document object enumeration
DOCUMENT = 1
LAYOUT = 2
GRID = 3
PAGE = 4
LAYER = 5
MASTERLAYER = 6
GUIDELAYER = 7
GUIDE = 8

GROUP = 9
MASKGROUP = 10

RECTANGLE = 30
ELLIPSE = 31
CURVE = 32
TEXT = 33


CID_TO_NAME = {
	DOCUMENT: _('Document'), LAYOUT: _('Layout'), GRID: _('Grid'),
	PAGE: _('Page'), LAYER: _('Layer'), MASTERLAYER: _('MasterLayer'),
	GUIDELAYER: _('GuideLayer'), GUIDE: _('Guideline'), GUIDE: _('Guideline'),

	GROUP: _('Group'), MASKGROUP: _('MaskGroup'),

	RECTANGLE:_('Rectangle'), ELLIPSE:_('Ellipse'), CURVE:_('Curve'), TEXT:_('Text'),
	}

class SK1ModelObject(TextModelObject):
	"""
	Abstract class for SK1 model objects.
	Defines common object functionality
	"""

	def __init__(self, config, string=''):
		self.config = config
		self.childs = []
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
		return result

#--- STRUCTURAL OBJECTS

class SK1Document(SK1ModelObject):
	"""
	Represents SK1 model root object.
	"""

	string = '##sK1 1 2\ndocument()'
	cid = DOCUMENT

	def __init__(self, config):
		SK1ModelObject.__init__(self, config)

class SK1Layout(SK1ModelObject):
	"""
	Represents Layout object.
	The object defines default page size as:
	(format_name,(width,height),orientation)
	"""

	string = "layout('A4',(595.276,841.89),0)"
	cid = LAYOUT

	def __init__(self, config, string=''):
		SK1ModelObject.__init__(self, config, string)

class SK1Grid(SK1ModelObject):
	"""
	Represents Grid layer object.
	Grid values are defined as:
	(grid,visibility,grid_color,layer_name)
	where:
	grid=(start_x, start_y, dx, dy)
	grid_color=(colorspace,color values)
	"""
	string = 'grid((0,0,2.83465,2.83465),0,("RGB",0.83,0.87,0.91),\'Grid\')'
	cid = GRID

	def __init__(self, config, string=''):
		SK1ModelObject.__init__(self, config, string)

class SK1Page(SK1ModelObject):
	"""
	Represents Page object.
	Page values are defined as:
	(page_name,format_name,(width,height),orientation)
	"""
	string = "page('','A4',(595.276,841.89),0)"
	cid = PAGE

	def __init__(self, config, string=''):
		SK1ModelObject.__init__(self, config, string)

class SK1Layer(SK1ModelObject):
	"""
	Represents Layer object.
	Layer values are defined as:
	(layer_name,visible,printable,locked,outlined,layer_color)
	"""
	string = "layer('Layer 1',1,1,0,0,(\"RGB\",0.196,0.314,0.635))"
	cid = LAYER

	def __init__(self, config, string=''):
		SK1ModelObject.__init__(self, config, string)

class SK1MasterLayer(SK1ModelObject):
	"""
	Represents MasterLayer object.
	Layer values are defined as:
	(layer_name,visible,printable,locked,outlined,layer_color)
	"""
	string = "masterlayer('MasterLayer 1',1,1,0,0,(\"RGB\",0.196,0.314,0.635))"
	cid = MASTERLAYER

	def __init__(self, config, string=''):
		SK1ModelObject.__init__(self, config, string)

class SK1GuideLayer(SK1ModelObject):
	"""
	Represents GuideLayer object.
	Layer values are defined as:
	(layer_name,visible,printable,locked,outlined,layer_color)
	"""
	string = "guidelayer('Guide Lines',1,0,0,1,(\"RGB\",0.0,0.3,1.0))"
	cid = GUIDELAYER

	def __init__(self, config, string=''):
		SK1ModelObject.__init__(self, config, string)

class SK1Guide(SK1ModelObject):
	"""
	Represents Guideline object.
	Guideline values are defined as:
	(point,orientation)
	"""
	string = "guide((0.0,0.0),0)"
	cid = GUIDE

	def __init__(self, config, string=''):
		SK1ModelObject.__init__(self, config, string)

#--- SELECTABLE OBJECTS

class SK1Group(SK1ModelObject):
	"""
	Represents Group object.
	All nested objects are in childs list.
	"""
	string = 'G()'
	end_string = 'G_()'
	cid = GROUP

	def __init__(self, config):
		SK1ModelObject.__init__(self, config)

class SK1MaskGroup(SK1ModelObject):
	"""
	Represents MaskGroup object.
	All nested objects are in childs list.
	The first object in childs list is the mask.
	"""
	string = 'M()'
	end_string = 'M_()'
	cid = MASKGROUP

	def __init__(self, config):
		SK1ModelObject.__init__(self, config)

#BlendGroup
#TextOnPath
#CompoundObject

#--- Primitive objects

class SK1Rectangle(SK1ModelObject):
	"""
	Represents Rectangle object.
	r(TRAFO [, RADIUS1, RADIUS2])
	"""
	string = ''
	cid = RECTANGLE

	def __init__(self, config):
		SK1ModelObject.__init__(self, config)

class SK1Ellipse(SK1ModelObject):
	"""
	Represents Ellipse object.
	e(TRAFO, [start_angle, end_angle, arc_type])
	"""
	string = ''
	cid = ELLIPSE

	def __init__(self, config):
		SK1ModelObject.__init__(self, config)

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

	def __init__(self, config):
		SK1ModelObject.__init__(self, config)

class SK1Text(SK1ModelObject):
	"""
	Represents Text object.
	txt(TEXT, TRAFO[, HORIZ_ALIGN, VERT_ALIGN])
	"""
	string = ''
	cid = TEXT

	def __init__(self, config):
		SK1ModelObject.__init__(self, config)
