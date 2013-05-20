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
from uc2.uc2const import COLOR_RGB, COLOR_CMYK, COLOR_LAB, COLOR_GRAY, \
COLOR_SPOT, COLOR_DISPLAY

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

CS = [COLOR_RGB, COLOR_CMYK, COLOR_LAB, COLOR_GRAY]

class ColorManager:
	"""
	The class provides abstract color manager.
	On CM object instantiation default built-in profiles
	are used to create internal stuff.
	"""

	handles = {}
	transforms = {}
	proof_transforms = {}

	use_display_profile = False
	proofing = False

	rgb_intent = uc2const.INTENT_RELATIVE_COLORIMETRIC
	cmyk_intent = uc2const.INTENT_PERCEPTUAL
	flags = uc2const.cmsFLAGS_NOTPRECALC

	def __init__(self):
		self.update()

	def update(self):
		"""
		Sets color profile handles using built-in profiles
		"""
		self.handles = {}
		self.clear_transforms()
		for item in CS:
			self.handles[item] = libcms.cms_create_default_profile(item)

	def clear_transforms(self):
		self.transforms = {}
		self.proof_transforms = {}

	def get_transform(self, cs_in, cs_out):
		"""
		Returns requested color transform using self.transforms dict.
		If requested transform is not initialized yet, creates it.
		"""
		tr_type = cs_in + cs_out
		intent = self.rgb_intent
		if cs_out == COLOR_CMYK:intent = self.cmyk_intent
		if not self.transforms.has_key(tr_type):
			handle_in = self.handles[cs_in]
			handle_out = self.handles[cs_out]
			if cs_out == COLOR_DISPLAY: cs_out = COLOR_RGB
			tr = libcms.cms_create_transform(handle_in, cs_in,
										handle_out, cs_out,
										intent, self.flags)
			self.transforms[tr_type] = tr
		return self.transforms[tr_type]


	def get_proof_transform(self, cs_in):
		"""
		Returns requested proof transform using self.proof_transforms dict.
		If requested transform is not initialized yet, creates it.
		"""
		tr_type = cs_in
		if not self.proof_transforms.has_key(tr_type):
			handle_in = self.handles[cs_in]
			if self.use_display_profile and self.handles.has_key(COLOR_DISPLAY):
				handle_out = self.handles[COLOR_DISPLAY]
			else:
				handle_out = self.handles[COLOR_RGB]
			handle_proof = self.handles[COLOR_CMYK]
			tr = libcms.cms_create_proofing_transform(handle_in, cs_in,
										handle_out, COLOR_RGB,
										handle_proof,
										self.cmyk_intent,
										self.rgb_intent, self.flags)
			self.proof_transforms[tr_type] = tr
		return self.proof_transforms[tr_type]

	def do_transform(self, color, cs_in, cs_out):
		"""
		Converts color between colorspaces.
		Return list of color values.
		"""
		in_color = colorb(color)
		out_color = colorb()
		transform = self.get_transform(cs_in, cs_out)
		libcms.cms_do_transform(transform, in_color, out_color)
		return decode_colorb(out_color, cs_out)

	def do_proof_transform(self, color, cs_in):
		"""
		Does color proof transform.
		Return list of color values.
		"""
		in_color = colorb(color)
		out_color = colorb()
		transform = self.get_proof_transform(cs_in)
		libcms.cms_do_transform(transform, in_color, out_color)
		return decode_colorb(out_color, COLOR_RGB)

	#Color management API
	def get_rgb_color(self, color):
		"""
		Convert color into RGB color.
		Stores alpha channel and color name.
		"""
		if color[0] == COLOR_RGB: return deepcopy(color)
		if color == COLOR_SPOT:
			return [COLOR_RGB, [] + color[1][0], color[2], '' + color[3]]
		res = self.do_transform(color, color[0], COLOR_RGB)
		return [COLOR_RGB, res, color[2], '' + color[3]]

	def get_cmyk_color(self, color):
		"""
		Convert color into CMYK color.
		Stores alpha channel and color name.
		"""
		if color[0] == COLOR_CMYK: return deepcopy(color)
		if color == COLOR_SPOT:
			return [COLOR_CMYK, [] + color[1][1], color[2], '' + color[3]]
		res = self.do_transform(color, color[0], COLOR_CMYK)
		return [COLOR_CMYK, res, color[2], '' + color[3]]

	def get_lab_color(self, color):
		"""
		Convert color into L*a*b* color.
		Stores alpha channel and color name.
		"""
		if color[0] == COLOR_LAB: return deepcopy(color)
		if color == COLOR_SPOT:
			color = [COLOR_RGB, [] + color[1][0], color[2], '' + color[3]]
		res = self.do_transform(color, color[0], COLOR_LAB)
		return [COLOR_LAB, res, color[2], '' + color[3]]

	def get_grayscale_color(self, color):
		"""
		Convert color into Grayscale color.
		Stores alpha channel and color name.
		"""
		if color[0] == COLOR_GRAY: return deepcopy(color)
		if color == COLOR_SPOT:
			color = [COLOR_RGB, [] + color[1][0], color[2], '' + color[3]]
		res = self.do_transform(color, color[0], COLOR_GRAY)
		return [COLOR_GRAY, res, color[2], '' + color[3]]

	def get_display_color(self, color):
		"""
		Calcs display color representation.
		Returns list of RGB values.
		"""
		cs_in = color[0]
		cs_out = COLOR_RGB
		if self.use_display_profile and self.handles.has_key(COLOR_DISPLAY):
			cs_out = COLOR_DISPLAY
		if self.proofing:
			if cs_in == COLOR_CMYK:
				ret = self.do_transform(color, cs_in, cs_out)
			else:
				ret = self.do_proof_transform(color, cs_in)
		else:
			if cs_in == cs_out:
				ret = color[1]
			else:
				ret = self.do_transform(color, cs_in, cs_out)
		return ret


