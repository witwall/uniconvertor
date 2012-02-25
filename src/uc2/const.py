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


"""
The package provides generic application constants
"""


#Color management constants

INTENT_PERCEPTUAL = 0
INTENT_RELATIVE_COLORIMETRIC = 1
INTENT_SATURATION = 2
INTENT_ABSOLUTE_COLORIMETRIC = 3

COLOR_GRAY = 'GRAY'
COLOR_RGB = 'RGB'
COLOR_CMYK = 'CMYK'
COLOR_LAB = 'LAB'
COLOR_SPOT = 'SPOT'

TYPE_RGB_8 = "RGB"
TYPE_RGBA_8 = "RGBA"
TYPE_CMYK_8 = "CMYK"
TYPE_GRAY_8 = "L"
TYPE_YCbCr_8 = "YCCA"

cmsFLAGS_NOTPRECALC = 0x0100
cmsFLAGS_GAMUTCHECK = 0x1000
cmsFLAGS_SOFTPROOFING = 0x4000
cmsFLAGS_BLACKPOINTCOMPENSATION = 0x2000
cmsFLAGS_PRESERVEBLACK = 0x8000
cmsFLAGS_NULLTRANSFORM = 0x0200
cmsFLAGS_HIGHRESPRECALC = 0x0400
cmsFLAGS_LOWRESPRECALC = 0x0800
