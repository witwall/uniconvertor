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

import math

from uc2.utils.config import XmlConfigParser
from uc2.formats.pdxf import const
from uc2 import uc2const

class PDXF_Config(XmlConfigParser):

	system_encoding = 'utf-8'

	#============== DOCUMENT SECTION ==================

	# 0 - page center
	# 1 - lower-left page corner
	# 2 - upper-left page corner 
	doc_origin = 1

	page_format = 'A4'
	page_orientation = uc2const.PORTRAIT

	layer_color = [uc2const.COLOR_RGB, [0.196, 0.329, 0.635], 1.0, ''] #'#3252A2'
	guide_color = '#0051FF'
	grid_color = '#D3DEE8'
	master_layer_color = [uc2const.COLOR_RGB, [0.0, 0.0, 0.0], 1.0, '']#'#000000'

	grid_geometry = [0, 0, 2.83465, 2.83465]

	default_polygon_num = 5
	default_text = "TEXT text"

	default_fill = []
	default_fill_rule = const.FILL_EVENODD


	default_stroke_rule = const.STROKE_MIDDLE
	default_stroke_width = 0.1 * uc2const.mm_to_pt
	default_stroke_color = [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, 'Black']
	default_stroke_dash = []
	default_stroke_cap = const.CAP_BUTT
	default_stroke_join = const.JOIN_MITER
	default_stroke_miter_angle = 45.0
	default_stroke_miter_limit = 1 / math.sin(default_stroke_miter_angle / 2.0)
	default_stroke_behind_flag = 0
	default_stroke_scalable_flag = 0
	default_stroke_markers = []

	default_stroke = [
					default_stroke_rule,
					default_stroke_width,
					default_stroke_color,
					default_stroke_dash,
					default_stroke_cap,
					default_stroke_join,
					default_stroke_miter_limit,
					default_stroke_behind_flag,
					default_stroke_scalable_flag,
					default_stroke_markers,
					]

	default_text_style = []
	default_structural_style = []
