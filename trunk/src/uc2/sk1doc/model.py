# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011 by Igor E. Novikov
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

import cairo

import uc2
from uc2 import uc_conf
from uc2 import _

CTX = cairo.Context(cairo.ImageSurface(cairo.FORMAT_RGB24, 10, 10))

#Paths definition:
#[path0, path1, ...]

#Path definition:
#[start_point, points, end_marker]
#start_pont - [x,y]
#end_ marker - is closed [1] if not []

#Points definition:
#[point0, point1,...]
# line point - [x,y]
# curve point - [[x1,y1],[x2,y2],[x3,y3], marker]

def create_cairo_path(paths):
	CTX.new_path()
	for path in paths:
		start_point = path[0]
		points = path[1]
		end = path[2]
		x, y = start_point
		CTX.move_to(x, y)
		for point in points:
			if len(point) == 2:
				x, y = point
				CTX.line_to(x, y)
			else:
				p1, p2, p3, m = point
				x1, y1 = p1
				x2, y2 = p2
				x3, y3 = p3
				CTX.curve_to(x1, y1, x2, y2, x3, y3)
		if end:
			CTX.close_path()
	return CTX.copy_path()

# Document object enumeration
DOCUMENT = 1

METAINFO = 10
STYLES = 11
STYLE = 12
PROFILES = 13
PROFILE = 14
FONTS = 15
FONT = 16
IMAGES = 17
IMAGE = 18

STRUCTURAL_CLASS = 50
PAGES = 51
PAGE = 52
LAYER_GROUP = 53
MASTER_LAYERS = 54
LAYER = 55
GRID_LAYER = 57
GUIDE_LAYER = 58

SELECTABLE_CLASS = 100
COMPOUND_CLASS = 101
GROUP = 102
CLIP_GROUP = 103
TEXT_BLOCK = 104
TEXT_COLUMN = 105

BITMAP_CLASS = 150
PIXMAP = 151

PRIMITIVE_CLASS = 200
RECTANGLE = 201
CIRCLE = 202
POLYGON = 203
CURVE = 204
CHAR = 205

CID_TO_NAME = {
	DOCUMENT: _('Document'),

	METAINFO: _('Metainfo'), STYLES: _('Styles'), STYLE: _('Style'),
	PROFILES: _('Profiles'), PROFILE: _('Profile'), FONTS: _('Fonts'),
	FONT: _('Font'), IMAGES: _('Images'), IMAGE: _('Image'),

	PAGES: _('Pages'), PAGE: _('Page'), LAYER_GROUP: _('Layer group'),
	MASTER_LAYERS: _('Master layers'), LAYER: _('Layer'),
	GRID_LAYER: _('Grid layer'), GUIDE_LAYER: _('Guide layer'),

	GROUP: _('Group'), CLIP_GROUP: _('Clip group'),
	TEXT_BLOCK: _('Text block'), TEXT_COLUMN: _('Text column'),

	RECTANGLE: _('Rectangle'), CIRCLE: _('Ellipse'),
	POLYGON: _('Polygon'), CURVE: _('Curve'),
	CHAR: _('Char'), PIXMAP: _('Pixmap'),
	}


CID_TO_TAGNAME = {
	DOCUMENT: 'Document',

	METAINFO: 'Metainfo', STYLES: 'Styles', STYLE: 'Style',
	PROFILES: 'Profiles', PROFILE: 'Profile', FONTS: 'Fonts',
	FONT: 'Font', IMAGES: 'Images', IMAGE: 'Image',

	PAGES: 'Pages', PAGE: 'Page', LAYER_GROUP: 'LayerGroup',
	MASTER_LAYERS: 'MasterLayers', LAYER: 'Layer',
	GRID_LAYER: 'GridLayer', GUIDE_LAYER: 'GuideLayer',

	GROUP: 'Group', CLIP_GROUP: 'ClipGroup',
	TEXT_BLOCK: 'TextBlock', TEXT_COLUMN: 'TextColumn',

	RECTANGLE: 'Rectangle', CIRCLE: 'Ellipse',
	POLYGON: 'Polygon', CURVE: 'Curve',
	CHAR: 'Char', PIXMAP: 'Pixmap',
	}

class DocumentObject:
	"""
	Abstract parent class for all document 
	objects. Provides common object properties.
	"""
	cid = 0
	parent = None
	config = None
	childs = []


class Document(DocumentObject):
	"""
	Represents sK1 Document object.
	This is a root DOM instance.
	"""
	cid = DOCUMENT
	metainfo = None
	styles = {}
	profiles = []
	doc_origin = 1

	def __init__(self, config=uc2.config):
		self.cid = DOCUMENT
		self.childs = []
		self.metainfo = None
		self.config = config
		self.doc_origin = self.config.doc_origin
		self.styles = {}
		self.styles["Default Style"] = [self.config.default_fill,
									self.config.default_stroke,
									self.config.default_text,
									self.config.default_structural_style]



class Pages(DocumentObject):
	"""
	Container for pages.
	Page format: [format name, (width, height), orientation]
	"""
	cid = PAGES
	page_format = []
	page_counter = 0

	def __init__(self, config=uc2.config, parent=None):
		self.cid = PAGES
		self.childs = []
		self.page_counter = 0
		self.parent = parent
		self.config = config
		format = '' + self.config.page_format
		size = uc_conf.PAGE_FORMATS[format]
		orient = config.page_orientation
		self.page_format = [format, size, orient]



#================Structural Objects==================

class StructuralObject(DocumentObject):
	"""
	Abstract parent for structural objects.
	"""
	cid = STRUCTURAL_CLASS
	name = ''

class Page(StructuralObject):
	"""
	PAGE OBJECT
	All child layers are in childs list.
	Page format: [format name, (width, height), orientation]
	"""
	cid = PAGE
	page_format = []
	name = ''

	layer_counter = 0

	def __init__(self, config=uc2.config, parent=None , name=_('Page') + ' 1'):
		self.cid = PAGE
		self.childs = []
		self.layer_counter = 0
		self.parent = parent
		self.config = config
		self.name = name
		if parent is None:
			format = '' + self.config.page_format
			size = uc_conf.PAGE_FORMATS[format]
			orient = config.page_orientation
			self.page_format = [format, size, orient]
		else:
			self.page_format = deepcopy(parent.page_format)


class Layer(StructuralObject):
	cid = LAYER
	color = ''
	name = ''

	def __init__(self, config=uc2.config, parent=None, name=_('Layer') + ' 1'):
		self.cid = LAYER
		self.childs = []
		self.parent = parent
		self.config = config
		self.name = name
		self.color = '' + self.config.layer_color
		self.childs = []

class GuideLayer(Layer):
	cid = GUIDE_LAYER

	def __init__(self, config=uc2.config, parent=None, name=_('GuideLayer')):
		Layer.__init__(self, config, parent, name)
		self.cid = GUIDE_LAYER
		self.childs = []
		self.color = '' + self.config.guide_color

class GridLayer(Layer):
	cid = GRID_LAYER
	grid = []

	def __init__(self, config=uc2.config, parent=None, name=_('GridLayer')):
		Layer.__init__(self, config, parent, name)
		self.cid = GRID_LAYER
		self.childs = []
		self.color = '' + self.config.grid_color
		self.grid = [] + self.config.grid_geometry

class LayerGroup(StructuralObject):
	cid = LAYER_GROUP
	layer_counter = 0

	def __init__(self, config=uc2.config, parent=None):
		self.cid = LAYER_GROUP
		self.childs = []
		self.parent = parent
		self.config = config
		self.childs = []

class MasterLayers(LayerGroup):
	cid = MASTER_LAYERS

	def __init__(self, config=uc2.config, parent=None):
		LayerGroup.__init__(self, config, parent)
		self.cid = MASTER_LAYERS
		self.childs = []



#================Selectable Objects==================
class SelectableObject(DocumentObject):
	"""
	Abstract parent class for selectable objects. 
	Provides common selectable object properties.
	"""
	cid = SELECTABLE_CLASS
	trafo = []
	style = None


#---------------Compound objects---------------------
class Group(SelectableObject):pass
class ClipGroup(SelectableObject):pass
class TextBlock(SelectableObject):pass
class TextColumn(SelectableObject):pass

#---------------Bitmap objects-----------------------

class Pixmap(SelectableObject):pass

#---------------Primitives---------------------------
class Rectangle(SelectableObject):

	cid = RECTANGLE
	start = []
	width = 10
	height = 10
	corners = []
	style = []

	cache_paths = None
	cache_cairo_matrix = None
	cache_cairo_path = None

	def __init__(self, config=uc2.config, parent=None,
				rect=[0.0, 0.0, 10, 10]):
		self.cid = RECTANGLE
		self.parent = parent
		self.config = config
		self.start = [rect[0], rect[1]]
		self.width = rect[2]
		self.height = rect[3]
		self.trafo = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
		self.corners = [0.0, 0.0, 0.0, 0.0]
		self.style = [[], [], [], []]

	def copy(self):
		rect = Rectangle(self.config)
		rect.start = [self.start[0], self.start[1]]
		rect.width = self.width
		rect.height = self.height
		rect.trafo = [] + self.trafo
		rect.corners = [] + self.corners
		rect.style = deepcopy(self.style)
		return rect

	def _get_initial_paths(self):
		return [[
				[self.start[0], self.start[1]],
				[
				[self.start[0] + self.width, self.start[1]],
				[self.start[0] + self.width, self.start[1] + self.height],
				[self.start[0], self.start[1] + self.height],
				[self.start[0], self.start[1]]
				],
				[1]
			]]

	def update(self):
		self.cache_paths = self._get_initial_paths()
		self.cache_cairo_path = create_cairo_path(self.cache_paths)
		m11, m12, m21, m22, dx, dy = self.trafo
		self.cache_cairo_matrix = cairo.Matrix(m11, m12, m21, m22, dx, dy)



class Circle(SelectableObject):pass
class Polygon(SelectableObject):pass
class Curve(SelectableObject):pass
class Char(SelectableObject):pass



CID_TO_CLASS = {
	DOCUMENT: Document,

	METAINFO: None, STYLES: None, STYLE: None,
	PROFILES: None, PROFILE: None, FONTS: None,
	FONT: None, IMAGES: None, IMAGE: None,

	PAGES: Pages, PAGE: Page, LAYER_GROUP: LayerGroup,
	MASTER_LAYERS: MasterLayers, LAYER: Layer,
	GRID_LAYER: GridLayer, GUIDE_LAYER: GuideLayer,

	GROUP: Group, CLIP_GROUP: ClipGroup,
	TEXT_BLOCK: TextBlock, TEXT_COLUMN: TextColumn,

	RECTANGLE: Rectangle, CIRCLE: Circle,
	POLYGON: Polygon, CURVE: Curve,
	CHAR: Char, PIXMAP: Pixmap,
	}

CID_TO_PROPNAME = {}
