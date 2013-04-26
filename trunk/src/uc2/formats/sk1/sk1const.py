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

import math

from uc2 import uc2const
from uc2.formats.pdxf import const

RGB = uc2const.COLOR_RGB
CMYK = uc2const.COLOR_CMYK
SPOT = uc2const.COLOR_SPOT

fallback_color = [RGB, [0.0, 0.0, 0.0], 1.0, '']
fallback_sk1color = (RGB, 0.0, 0.0, 0.0)

default_grid = (0, 0, 2.83465, 2.83465)
default_grid_color = [RGB, [0.83, 0.87, 0.91], 1.0, '']

default_layer_properties = [1, 1, 0, 0]
default_layer_color = [RGB, [0.196, 0.314, 0.635], 1.0, '']

default_guidelayer_properties = [1, 0, 0, 1]
default_guidelayer_color = [RGB, [0.0, 0.3, 1.0], 1.0, '']


fill_style = []
default_stroke_rule = const.STROKE_MIDDLE
default_stroke_width = 0.0
default_stroke_color = [uc2const.COLOR_CMYK, [0.0, 0.0, 0.0, 1.0], 1.0, 'Black']
default_stroke_dash = []
default_stroke_cap = const.CAP_BUTT
default_stroke_join = const.JOIN_MITER
default_stroke_miter_angle = 45.0
default_stroke_miter_limit = 1.0 / math.sin(default_stroke_miter_angle / 2.0)
default_stroke_behind_flag = 0
default_stroke_scalable_flag = 0
default_stroke_markers = []

stroke_style = [
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
text_style = []
structural_style = []
default_style = [fill_style, stroke_style, text_style, structural_style]
