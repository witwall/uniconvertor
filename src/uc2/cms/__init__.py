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

import os

from copy import deepcopy

import libcms
from uc2 import uc2const

def rgb_to_hexcolor(color):
	"""
	Converts list of RGB float values to hex color string.
	For example: [1.0, 0.0, 1.0] => #ff00ff
	"""
	r, g, b = color
	return '#%02x%02x%02x' % (int(255 * r), int(255 * g), int(255 * b))

def rgba_to_hexcolor(color):
	"""
	Converts list of RGBA float values to hex color string.
	For example: [1.0, 0.0, 1.0, 1.0] => #ff00ffff
	"""
	r, g, b, a = color
	return '#%02x%02x%02x%02x' % (int(255 * r), int(255 * g),
								int(255 * b), int(65535 * a))

def hexcolor_to_rgb(hexcolor):
	"""
	Converts hex color string as a list of float values.
	For example: #ff00ff => [1.0, 0.0, 1.0]
	"""
	r = int(hexcolor[1:3], 0x10) / 255.0
	g = int(hexcolor[3:5], 0x10) / 255.0
	b = int(hexcolor[5:], 0x10) / 255.0
	return [r, g, b]

def hexcolor_to_rgba(hexcolor):
	"""
	Converts hex color string as a list of float values.
	For example: #ff00ff => [1.0, 0.0, 1.0, 1.0]
	"""
	if len(hexcolor) == 7:
		r = int(hexcolor[1:3], 0x10) / 255.0
		g = int(hexcolor[3:5], 0x10) / 255.0
		b = int(hexcolor[5:], 0x10) / 255.0
		return [r, g, b, 1.0]
	elif len(hexcolor) == 9:
		r = int(hexcolor[1:3], 0x10) / 255.0
		g = int(hexcolor[3:5], 0x10) / 255.0
		b = int(hexcolor[5:7], 0x10) / 255.0
		a = int(hexcolor[7:], 0x10) / 255.0
		return [r, g, b, a]
	else:
		return [0.0, 0.0, 0.0, 1.0]

def gdk_hexcolor_to_rgb(hexcolor):
	"""
	Converts hex color string as a list of float values.
	For example: #ffff0000ffff => [1.0, 0.0, 1.0]
	"""
	r = int(hexcolor[1:5], 0x10) / 65535.0
	g = int(hexcolor[5:9], 0x10) / 65535.0
	b = int(hexcolor[9:], 0x10) / 65535.0
	return [r, g, b]

def cmyk_to_rgb(color):
	"""
	Converts list of CMYK values to RGB.
	"""
	c, m, y, k = color
	r = round(1.0 - min(1.0, c + k), 3)
	g = round(1.0 - min(1.0, m + k), 3)
	b = round(1.0 - min(1.0, y + k), 3)
	return [r, g, b]

def rgb_to_cmyk(color):
	"""
	Converts list of RGB values to CMYK.
	"""
	r, g, b = color
	c = 1.0 - r
	m = 1.0 - g
	y = 1.0 - b
	k = min(c, m, y)
	return [c - k, m - k, y - k, k]

def colorb(color=None, cmyk=False):
	"""
	Emulates COLORB object from python-lcms.
	Actually function returns regular 4-member list.
	"""
	if color is None:
		return [0, 0, 0, 0]
	if color[0] == uc2const.COLOR_SPOT:
		if cmyk: values = color[1][1]
		else: values = color[1][0]
	else:
		values = color[1]
	result = []
	for value in values:
		result.append(int(round(value, 3) * 255))
	if len(result) == 1:
		result += [0, 0, 0]
	elif len(result) == 3:
		result += [0]
	return result

def decode_colorb(colorb, color_type):
	"""
	Decodes colorb list into generic color values.
	"""
	result = []
	if color_type == uc2const.COLOR_CMYK:
		values = colorb
	elif color_type == uc2const.COLOR_GRAY:
		values = [colorb[0], ]
	else:
		values = colorb[:3]
	for value in values:
		result.append(round(value / 255.0, 3))
	return result

def get_profile_name(filepath):
	"""
	Returns profile name.
	If file is not suitable profile or doesn't exist
	returns None. 
	"""
	ret = None
	try:
		profile = libcms.cms_open_profile_from_file(filepath)
		ret = libcms.cms_get_profile_name(profile)
	except:pass
	return ret

def get_profile_info(filepath):
	"""
	Returns profile info.
	If file is not suitable profile or doesn't exist
	returns None. 
	"""
	ret = None
	try:
		profile = libcms.cms_open_profile_from_file(filepath)
		ret = libcms.cms_get_profile_info(profile)
	except:pass
	return ret

class ColorManager:
	"""
	The class provides color manager (CM) object.
	On CM object instantiation custom profiles could be defined as a 
	5-member list of paths to files:
	
	[rgb_profile, cmyk_profile, lab_profile, grayscale_profile, display_profile]
	
	if some profile or all profiles are not provided default built-in profiles
	will be used.
	"""
	default_cms = False
	use_cms = False
	softproof = False
	handles = {}
	transforms = {}

	def __init__(self, profiles=[], default_cms=False):
		self.default_cms = default_cms
		self.set_handles(profiles)

	def set_handles(self, profiles=[]):

		if profiles and len(profiles) == 5:
			self.handles = {}
			self.transforms = {}
			self.load_rgb_profile(profiles[0])
			self.load_cmyk_profile(profiles[1])
			self.load_lab_profile(profiles[2])
			self.load_grayscale_profile(profiles[3])
			self.load_display_profile(profiles[4])
		else:
			if self.default_cms:
				self.set_default_handles()

	def set_default_handles(self):
		self.load_rgb_profile()
		self.load_cmyk_profile()
		self.load_lab_profile()
		self.load_grayscale_profile()
		self.load_display_profile()

	def load_rgb_profile(self, path=''):
		if path and os.path.lexists(path):
			self.handles[uc2const.COLOR_RGB] = libcms.cms_open_profile_from_file(path)
		else:
			self.handles[uc2const.COLOR_RGB] = libcms.cms_create_srgb_profile()

	def load_cmyk_profile(self, path=''):
		if path and os.path.lexists(path):
			self.handles[uc2const.COLOR_CMYK] = libcms.cms_open_profile_from_file(path)
		else:
			self.handles[uc2const.COLOR_CMYK] = libcms.cms_create_cmyk_profile()

	def load_lab_profile(self, path=''):
		if path and os.path.lexists(path):
			self.handles[uc2const.COLOR_LAB] = libcms.cms_open_profile_from_file(path)
		else:
			self.handles[uc2const.COLOR_LAB] = libcms.cms_create_lab_profile()

	def load_grayscale_profile(self, path=''):
		if path and os.path.lexists(path):
			self.handles[uc2const.COLOR_GRAY] = libcms.cms_open_profile_from_file(path)
		else:
			self.handles[uc2const.COLOR_GRAY] = libcms.cms_create_gray_profile()

	def load_display_profile(self, path=''):
		if path and os.path.lexists(path):
			self.handles[uc2const.COLOR_DISPLAY] = libcms.cms_open_profile_from_file(path)
		else:
			self.handles[uc2const.COLOR_DISPLAY] = libcms.cms_create_display_profile()

	def create_transform(self, handle_in, type_in, handle_out, type_out):
		return libcms.cms_create_transform(handle_in, type_in, handle_out, type_out)

	#Color management API
	def get_rgb_color(self, color):
		if color[0] == uc2const.COLOR_RGB:
			return deepcopy(color)
		if color == uc2const.COLOR_SPOT:
			return [uc2const.COLOR_RGB, [] + color[1][0], color[2], '' + color[3]]

		tr_type = color[0] + uc2const.COLOR_RGB
		if not self.transforms.has_key(tr_type):
			self.transforms[tr_type] = self.create_transform(self.handles[color[0]],
															color[0],
															self.handles[uc2const.COLOR_RGB],
															uc2const.COLOR_RGB)
		in_color = colorb(color)
		out_color = colorb()
		libcms.cms_do_transform(self.transforms[tr_type], in_color, out_color)
		res = decode_colorb(out_color, uc2const.COLOR_RGB)
		return [uc2const.COLOR_RGB, res, color[2], '' + color[3]]

	def get_cmyk_color(self, color):
		if color[0] == uc2const.COLOR_CMYK:
			return deepcopy(color)
		if color == uc2const.COLOR_SPOT:
			return [uc2const.COLOR_CMYK, [] + color[1][1], color[2], '' + color[3]]

		tr_type = color[0] + uc2const.COLOR_CMYK
		if not self.transforms.has_key(tr_type):
			self.transforms[tr_type] = self.create_transform(self.handles[color[0]],
															color[0],
															self.handles[uc2const.COLOR_CMYK],
															uc2const.COLOR_CMYK)
		in_color = colorb(color)
		out_color = colorb()
		libcms.cms_do_transform(self.transforms[tr_type], in_color, out_color)
		res = decode_colorb(out_color, uc2const.COLOR_CMYK)
		return [uc2const.COLOR_CMYK, res, color[2], '' + color[3]]

	def get_lab_color(self, color):
		if color[0] == uc2const.COLOR_LAB:
			return deepcopy(color)
		if color == uc2const.COLOR_SPOT:
			color = [uc2const.COLOR_RGB, [] + color[1][0], color[2], '' + color[3]]

		tr_type = color[0] + uc2const.COLOR_LAB
		if not self.transforms.has_key(tr_type):
			self.transforms[tr_type] = self.create_transform(self.handles[color[0]],
															color[0],
															self.handles[uc2const.COLOR_LAB],
															uc2const.COLOR_LAB)
		in_color = colorb(color)
		out_color = colorb()
		libcms.cms_do_transform(self.transforms[tr_type], in_color, out_color)
		res = decode_colorb(out_color, uc2const.COLOR_LAB)
		return [uc2const.COLOR_LAB, res, color[2], '' + color[3]]

	def get_grayscale_color(self, color):
		if color[0] == uc2const.COLOR_GRAY:
			return deepcopy(color)
		if color == uc2const.COLOR_SPOT:
			color = [uc2const.COLOR_RGB, [] + color[1][0], color[2], '' + color[3]]

		tr_type = color[0] + uc2const.COLOR_GRAY
		if not self.transforms.has_key(tr_type):
			self.transforms[tr_type] = self.create_transform(self.handles[color[0]],
															color[0],
															self.handles[uc2const.COLOR_GRAY],
															uc2const.COLOR_GRAY)
		in_color = colorb(color)
		out_color = colorb()
		libcms.cms_do_transform(self.transforms[tr_type], in_color, out_color)
		res = decode_colorb(out_color, uc2const.COLOR_GRAY)
		return [uc2const.COLOR_GRAY, res, color[2], '' + color[3]]


	def get_display_color(self, color):
		color = self.get_rgb_color(color)
		tr_type = color[0] + uc2const.COLOR_DISPLAY
		if not self.transforms.has_key(tr_type):
			self.transforms[tr_type] = self.create_transform(self.handles[color[0]],
															color[0],
															self.handles[uc2const.COLOR_DISPLAY],
															uc2const.COLOR_RGB)
		in_color = colorb(color)
		out_color = colorb()
		libcms.cms_do_transform(self.transforms[tr_type], in_color, out_color)
		return decode_colorb(out_color, uc2const.COLOR_RGB)




