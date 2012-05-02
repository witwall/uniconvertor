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

from uc2 import uc2const
from uc2.formats.riff.utils import double2py_float, dword2py_int, long2py_float
from uc2.formats.cdr.const import cdrunit_to_pt

def parse_matrix(data):
	"""
	Parses CDR affine transformation matrix and 
	returns matrix as a list.
	"""
	m11 = double2py_float(data[0:8])
	m12 = double2py_float(data[8:16])
	dx = double2py_float(data[16:24]) * cdrunit_to_pt
	m21 = double2py_float(data[24:32])
	m22 = double2py_float(data[32:40])
	dy = double2py_float(data[40:48]) * cdrunit_to_pt
	return [m11, m21, m12, m22, dx, dy]

def parse_cmyk(data):
	"""
	Parses CMYK color bytes and	returns fill style list.
	"""
	c = ord(data[0]) / 100.0
	m = ord(data[1]) / 100.0
	y = ord(data[2]) / 100.0
	k = ord(data[3]) / 100.0
	return [uc2const.COLOR_CMYK, [c, m, y, k], 1.0, '']

def parse_cmyk255(data):
	"""
	Parses CMYK255 color bytes and returns fill style list.
	"""
	c = ord(data[0]) / 255.0
	m = ord(data[1]) / 255.0
	y = ord(data[2]) / 255.0
	k = ord(data[3]) / 255.0
	return [uc2const.COLOR_CMYK, [c, m, y, k], 1.0, '']

def parse_cmy(data):
	"""
	Parses CMY color bytes and returns fill style list.
	"""
	c = ord(data[0]) / 255.0
	m = ord(data[1]) / 255.0
	y = ord(data[2]) / 255.0
	k = 0.0
	return [uc2const.COLOR_CMYK, [c, m, y, k], 1.0, '']

def parse_bgr(data):
	"""
	Parses BGR color bytes and returns fill style list.
	"""
	b = ord(data[0]) / 255.0
	g = ord(data[1]) / 255.0
	r = ord(data[2]) / 255.0
	return [uc2const.COLOR_RGB, [r, g, b], 1.0, '']

def parse_lab(data):
	"""
	Parses Lab color bytes and returns fill style list.
	"""
	l = ord(data[0]) / 255.0
	a = ord(data[1]) / 255.0
	b = ord(data[2]) / 255.0
	return [uc2const.COLOR_LAB, [l, a, b], 1.0, '']

def parse_grayscale(data):
	"""
	Parses Grayscale color byte and returns fill style list.
	"""
	l = 1.0 - ord(data[0]) / 255.0
	return [uc2const.COLOR_GRAY, [l, ], 1.0, '']

def parse_reg_color(data=''):
	"""
	Returns Registration color fill style list.
	"""
	return [uc2const.COLOR_SPOT, [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0, 1.0] ], 1.0, 'All']

def parse_size_value(data):
	"""
	Convert 4-bytes string to value in points.
	"""
	return long2py_float(data) * cdrunit_to_pt
