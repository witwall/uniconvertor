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
from uc2 import uc2const
from uc2 import cms
from uc2.formats.pdxf import const
from uc2.formats.pdxf import methods

from uc2 import utils
from uc2.formats.pdxf.methods import PDXF_Methods
from uc2.formats.pdxf.pdxf_config import PDXF_Config
from uc2.formats.pdxf.pdxf_filters import PDXF_Loader, PDXF_Saver
from uc2.formats.generic import TaggedModelPresenter

class PDXF_Presenter(TaggedModelPresenter):

	cid = uc2const.PDXF

	methods = None
	cms = None


	def __init__(self, appdata, cnf={}):
		self.config = PDXF_Config()
		config_file = os.path.join(appdata.app_config_dir, 'pdxf_config.xml')
		self.config.load(config_file)
		self.config.update(cnf)
		self.appdata = appdata
		self.doc_id = utils.generate_id()
		self.loader = PDXF_Loader()
		self.saver = PDXF_Saver()
		self.create_cache_structure()
		self.methods = PDXF_Methods(self)
		self.cms = cms.ColorManager()
		self.new()

	def create_cache_structure(self):
		doc_cache_dir = os.path.join(self.appdata.app_config_dir, 'docs_cache')
		self.doc_dir = os.path.join(doc_cache_dir, 'doc_' + self.doc_id)
		for dir in const.DOC_STRUCTURE:
			path = os.path.join(self.doc_dir, dir)
			os.makedirs(path)
		mime = open(os.path.join(self.doc_dir, 'mimetype') , 'wb')
		mime.write(const.DOC_MIME)
		mime.close()

	def new(self):
		self.model = methods.create_new_doc(self.config)
		self.methods.update()
		self.model.do_update()

	def merge(self):
		pass

	def update(self):
		TaggedModelPresenter.update(self)
		if not self.model is None:
			self.methods.update()
