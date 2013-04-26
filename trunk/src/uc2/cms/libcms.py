# -*- coding: utf-8 -*-
#
#	cms - module which provides binding
#	to LittleCMS library.
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

import os
import types
import _cms

from uc2 import uc2const


class CmsError(Exception):
	pass

def COLORB():
	"""
	Emulates COLORB object from python-lcms.
	Actually function returns regular 4-member list.
	"""
	return [0, 0, 0, 0]

def cms_set_alarm_codes(r, g, b):
	"""
	Used to define gamut check marker.
	r,g,b are expected to be integers in range 0..255
	"""
	if r in range(0, 256) and g in range(0, 256) and b in range(0, 256):
		_cms.setAlarmCodes(r, g, b)
	else:
		raise CmsError, "r,g,b are expected to be integers in range 0..255"

def cms_open_profile_from_file(profileFilename, mode=None):
	"""	
	Returns a handle to lcms profile wrapped as a Python object. 
	The handle doesn't require to be closed after usage because
	on object delete operation Python calls native cms_close_profile()
	function automatically  

	profileFilename - a valid filename path to the ICC profile
	mode - stub parameter for python-lcms compatibility
	"""
	if not os.path.isfile(profileFilename):
		raise CmsError, "Invalid profile path provided: %s" % profileFilename

	result = _cms.openProfile(profileFilename)

	if result is None:
		raise CmsError, "It seems provided profile is invalid: %s" % profileFilename

	return result

def cms_create_srgb_profile():
	"""	
	Artificial functionality. The function emulates built-in sRGB
	profile reading profile resource attached to the package.
	Returns a handle to lcms built-in sRGB profile wrapped as a Python object. 
	The handle doesn't require to be closed after usage because
	on object delete operation Python calls native cms_close_profile()
	function automatically
	"""
	import srgb_profile_rc
	profile = srgb_profile_rc.get_resource(True)
	return cms_open_profile_from_file(profile.name)

def get_srgb_profile_resource():
	"""
	Returns named temporary file object of built-in sRGB profile.
	"""
	import srgb_profile_rc
	return srgb_profile_rc.get_resource(True)

def cms_create_cmyk_profile():
	"""	
	Artificial functionality. The function emulates built-in CMYK
	profile reading profile resource attached to the package.
	Returns a handle to lcms built-in CMYK profile wrapped as a Python object. 
	The handle doesn't require to be closed after usage because
	on object delete operation Python calls native cms_close_profile()
	function automatically
	"""
	import cmyk_profile_rc
	profile = cmyk_profile_rc.get_resource(True)
	return cms_open_profile_from_file(profile.name)

def get_cmyk_profile_resource():
	"""
	Returns named temporary file object of built-in CMYK profile.
	"""
	import cmyk_profile_rc
	return cmyk_profile_rc.get_resource(True)

def cms_create_display_profile():
	"""	
	Artificial functionality. The function emulates built-in display
	profile reading sRGB profile resource attached to the package.
	Returns a handle to lcms built-in display profile wrapped as a Python object. 
	The handle doesn't require to be closed after usage because
	on object delete operation Python calls native cms_close_profile()
	function automatically
	"""
	import srgb_profile_rc
	profile = srgb_profile_rc.get_resource(True)
	return cms_open_profile_from_file(profile.name)

def cms_create_lab_profile():
	"""	
	Artificial functionality. The function emulates built-in Lab
	profile reading profile resource attached to the package.
	Returns a handle to lcms built-in Lab profile wrapped as a Python object. 
	The handle doesn't require to be closed after usage because
	on object delete operation Python calls native cms_close_profile()
	function automatically
	"""
	import lab_profile_rc
	profile = lab_profile_rc.get_resource(True)
	return cms_open_profile_from_file(profile.name)

def get_lab_profile_resource():
	"""
	Returns named temporary file object of built-in Lab profile.
	"""
	import lab_profile_rc
	return lab_profile_rc.get_resource(True)

def cms_create_gray_profile():
	"""	
	Artificial functionality. The function emulates built-in Gray
	profile reading profile resource attached to the package.
	Returns a handle to lcms built-in Gray profile wrapped as a Python object. 
	The handle doesn't require to be closed after usage because
	on object delete operation Python calls native cms_close_profile()
	function automatically
	"""
	import gray_profile_rc
	profile = gray_profile_rc.get_resource(True)
	return cms_open_profile_from_file(profile.name)

def get_gray_profile_resource():
	"""
	Returns named temporary file object of built-in Gray profile.
	"""
	import gray_profile_rc
	return gray_profile_rc.get_resource(True)

def cms_create_transform(inputProfile, inMode,
					outputProfile, outMode,
					renderingIntent=uc2const.INTENT_PERCEPTUAL,
					flags=uc2const.cmsFLAGS_NOTPRECALC):
	"""
	Returns a handle to lcms transformation wrapped as a Python object.

	inputProfile - a valid lcms profile handle
	outputProfile - a valid lcms profile handle
	inMode - predefined string constant (i.e. TYPE_RGB_8, TYPE_RGBA_8, TYPE_CMYK_8, etc.) or valid PIL mode		
	outMode - predefined string constant (i.e. TYPE_RGB_8, TYPE_RGBA_8, TYPE_CMYK_8, etc.) or valid PIL mode		
	renderingIntent - integer constant (0-3) specifying rendering intent for the transform
	flags - a set of predefined lcms flags
	"""

	if renderingIntent not in (0, 1, 2, 3):
		raise CmsError, "renderingIntent must be an integer between 0 and 3"

	result = _cms.buildTransform(inputProfile, inMode, outputProfile, outMode, renderingIntent, flags)

	if result is None:
		raise CmsError, "Cannot create requested transform: %s %s" % (inMode, outMode)

	return result

def cms_create_proofing_transform(inputProfile, inMode,
							outputProfile, outMode,
							proofingProfile,
							renderingIntent=uc2const.INTENT_PERCEPTUAL,
							proofingIntent=uc2const.INTENT_RELATIVE_COLORIMETRIC,
							flags=uc2const.cmsFLAGS_SOFTPROOFING):
	"""
	Returns a handle to lcms transformation wrapped as a Python object.

	inputProfile - a valid lcms profile handle
	outputProfile - a valid lcms profile handle
	proofingProfile - a valid lcms profile handle 
	inMode - predefined string constant (i.e. TYPE_RGB_8, TYPE_RGBA_8, TYPE_CMYK_8, etc.) or valid PIL mode		
	outMode - predefined string constant (i.e. TYPE_RGB_8, TYPE_RGBA_8, TYPE_CMYK_8, etc.) or valid PIL mode		
	renderingIntent - integer constant (0-3) specifying rendering intent for the transform
	proofingIntent - integer constant (0-3) specifying proofing intent for the transform
	flags - a set of predefined lcms flags
	"""

	if renderingIntent not in (0, 1, 2, 3):
		raise CmsError, "renderingIntent must be an integer between 0 and 3"

	if proofingIntent not in (0, 1, 2, 3):
		raise CmsError, "proofingIntent must be an integer between 0 and 3"

	result = _cms.buildProofingTransform(inputProfile, inMode, outputProfile, outMode,
										proofingProfile, renderingIntent, proofingIntent, flags)

	if result is None:
		raise CmsError, "Cannot create requested proofing transform: %s %s" % (inMode, outMode)

	return result

def cms_do_transform(hTransform, inputBuffer, outputBuffer, buffersSizeInPixels=None):
	"""
	Transform color values from inputBuffer to outputBuffer using provided lcms transform handle.
	
	hTransform - a valid lcms transformation handle
	inputBuffer - 4-member list object. The members must be an integer between 0 and 255
	outputBuffer - 4-member list object with any values for recording transformation results.
	             Can be [0,0,0,0].
	buffersSizeInPixels - parameter for python-lcms compatibility. Can be skipped.               
	"""

	if type(inputBuffer) is types.ListType and type(outputBuffer) is types.ListType:

		outputBuffer[0], outputBuffer[1], outputBuffer[2], outputBuffer[3] = _cms.transformPixel(hTransform,
																									inputBuffer[0],
																									inputBuffer[1],
																									inputBuffer[2],
																									inputBuffer[3])
		return

	else:
		raise CmsError, "inputBuffer and outputBuffer must be Python 4-member list objects"



def cms_get_profile_name(profile):
	"""
	This function is given mainly for building user interfaces.
	
	profile - a valid lcms profile handle
	Returns profile name as a string value.	
	"""
	return _cms.getProfileName(profile)

def cms_get_profile_info(profile):
	"""
	This function is given mainly for building user interfaces.
	
	profile - a valid lcms profile handle
	Returns profile description info as a string value.	
	"""
	return _cms.getProfileInfo(profile)

def cms_do_transform2(hTransform, channel1, channel2, channel3, channel4=0):
	"""
	Accelerated variant of cms_do_transform. Adapted for PrintDesign color management.
	Not presented in python-lcms API.
	
	hTransform - a valid lcms transformation handle
	channel1, channel2, channel3, channel4 - color channel values. Must be float between 0 and 1.
	
	Returns 4-member tuple of converted color values (i.e. CMYK or RGBA) as a float between 0 and 1.
	"""
	return _cms.transformPixel2(hTransform, channel1, channel2, channel3, channel4)

def cms_delete_transform(transform):
	"""
	This is a function stub for python-lcms compatibility.
	Transform handle will be released automatically.
	"""
	pass

def cms_close_profile(profile):
	"""
	This is a function stub for python-lcms compatibility.
	Profile handle will be released automatically.
	"""
	pass

#==========================UNREFACTORED=========================================
#==========================UNREFACTORED=========================================
#==========================UNREFACTORED=========================================



#def cmsDoBitmapTransform(hTransform, inImage, inMode, outMode):
#	"""
#	The method provides PIL images support for color management.
#	
#	hTransform - a valid lcms transformation handle
#	inImage - a valid PIL image object
#	inMode, outMode -  - predefined string constant (i.e. TYPE_RGB_8, TYPE_RGBA_8, TYPE_CMYK_8) or valid PIL mode
#	Currently supports RGB, RGBA and CMYK modes only.
#	Returns new PIL image object in outMode colorspace.
#	"""
#	if not inImage.mode == inMode:
#		raise CmsError, "incorrect inMode"
#	
#	if not inImage.mode in [TYPE_RGB_8, TYPE_RGBA_8, TYPE_CMYK_8]: 
#		raise CmsError, "unsupported image type: %s"%inImage.mode
#	
#	if not inMode in [TYPE_RGB_8, TYPE_RGBA_8, TYPE_CMYK_8]: 
#		raise CmsError, "unsupported inMode type: %s"%inMode
#	
#	if not outMode in [TYPE_RGB_8, TYPE_RGBA_8, TYPE_CMYK_8]: 
#		raise CmsError, "unsupported outMode type: %s"%outMode
#	
#	w, h = inImage.size
#	inImage.load()
#	outImage=Image.new(outMode, (w, h))
#	
#	_cms.transformBitmap(hTransform, inImage.im, outImage.im, w, h)
#	
#	return outImage

##############################################################
#              Pixels API
##############################################################
#  Best color management performance can be achieved for plane 
#  pixel arrays (i.e. for unsigned char* on native side)
#  Also pixel arrays can be used for Cairo and ImageMagick 
#  integration.
##############################################################

#def getPixelsFromImage(image):
#	"""
#	Creates pixel array using provided image. Accepts any valid PIL image.
#	
#	image - any valid PIL image.
#	Returns pixel array handle wrapped as a python object.
#	"""
#	image.load()
#	width,height = image.size
#	pixel = image.getpixel((0,0))
#	bytes_per_pixel = 1
#	if type(pixel) is types.TupleType:
#		bytes_per_pixel = len(pixel)
#	if image.mode == TYPE_RGB_8:
#		bytes_per_pixel = 4
#	return _cms.getPixelsFromImage(image.im, width, height, bytes_per_pixel)
#
#def getImageFromPixels(pixels, mode, width, height):
#	"""
#	Creates new image using provided pixel array.
#	
#	pixels - pixel array wrapped as a python object.
#	mode - pixel array appropriate PIL mode.
#	width, height - pixel array appropriate image size.
#	Returns new PIL image object.
#	"""
#	image=Image.new(mode,(width,height))
#	pixel = image.getpixel((0,0))
#	bytes_per_pixel = 1
#	if type(pixel) is types.TupleType:
#		bytes_per_pixel = len(pixel)
#	if image.mode == TYPE_RGB_8:
#		bytes_per_pixel = 4
#	_cms.setImagePixels(pixels, image.im, width, height, bytes_per_pixel)
#	return image
#
#def cmsDoPixelsTransform(hTransform, pixels, width):
#	"""
#	Transforms pixel array using provided lcms transform handle.
#	Supports TYPE_RGB_8, TYPE_RGBA_8, and TYPE_CMYK_8 transforms only.
#	
#	hTransform - valid lcms transform handle
#	pixels - pixel array wrapped as a python object.
#	width - pixel array width.
#	Returns handle to new pixel array.
#	"""
#	return _cms.transformPixels(hTransform, pixels, width)