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

from uc2.utils.fs import expanduser_unicode
from uc2.utils.config import XmlConfigParser



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


class UCConfig(XmlConfigParser):

	#============== GENERIC SECTION ===================
	uc_version = '2.0'
	system_encoding = 'utf-8'	# default encoding (GUI uses utf-8 only)










