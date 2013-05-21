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

import os, shutil

from uc2 import uc2const
from uc2.utils.fs import expanduser_unicode
from uc2.utils.config import XmlConfigParser
from uc2.cms import CS, libcms



class UCData:

	app_name = 'UniConvertor'
	app_proc = 'uniconvertor'
	app_org = 'sK1 Project'
	app_domain = 'sk1project.org'
	app_icon = None
	doc_icon = None
	version = '2.0'

	app_config_dir = expanduser_unicode(os.path.join('~', '.config', 'uc2'))
	if not os.path.lexists(app_config_dir):
		os.makedirs(app_config_dir)
	app_config = expanduser_unicode(os.path.join('~', '.config',
												'uc2', 'preferences.cfg'))

	#Check color profiles directory	
	app_color_profile_dir = os.path.join(app_config_dir, 'profiles')
	if not os.path.lexists(app_color_profile_dir):
		os.makedirs(app_color_profile_dir)

	for item in CS:
		filename = 'built-in_%s.icm' % item
		path = os.path.join(app_color_profile_dir, filename)
		if not os.path.lexists(path):
			profile = libcms.cms_get_default_profile_resource(item)
			shutil.copy(profile.name, path)

class UCConfig(XmlConfigParser):

	#============== GENERIC SECTION ===================
	uc_version = '2.0'
	system_encoding = 'utf-8'	# default encoding (GUI uses utf-8 only)



	#============== COLOR PROFILES ================
	cms_use = True
	cms_display_profiles = {}
	cms_rgb_profiles = {}
	cms_cmyk_profiles = {}
	cms_lab_profiles = {}
	cms_gray_profiles = {}

	cms_display_profile = ''
	cms_rgb_intent = uc2const.INTENT_RELATIVE_COLORIMETRIC
	cms_cmyk_intent = uc2const.INTENT_PERCEPTUAL
	cms_flags = uc2const.cmsFLAGS_NOTPRECALC
	cms_proofing = False
	cms_gamutcheck = False
	cms_alarmcodes = [1.0, 0.0, 1.0]
	cms_proof_for_spot = False
	cms_bpc_flag = False
	cms_bpt_flag = False








