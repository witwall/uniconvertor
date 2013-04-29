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

import os

from uc2 import uc2const
from uc2.formats.generic import TextModelPresenter
from uc2.formats.sk1.sk1_config import SK1_Config
from uc2.formats.sk1 import model
from uc2.formats.sk1.sk1_filters import SK1_Loader, SK1_Saver
from uc2.formats.sk1.sk1_translators import PDXF_to_SK1_Translator
from uc2.formats.sk1.sk1_translators import SK1_to_PDXF_Translator

class SK1_Presenter(TextModelPresenter):

	cid = uc2const.SK1

	config = None
	doc_file = ''
	resources = None

	def __init__(self, appdata, cnf={}):
		self.config = SK1_Config()
		config_file = os.path.join(appdata.app_config_dir, 'sk1_config.xml')
		self.config.load(config_file)
		self.config.update(cnf)
		self.appdata = appdata
		self.loader = SK1_Loader()
		self.saver = SK1_Saver()
		self.resources = {}
		self.new()

	def new(self):
		self.model = model.SK1Document(self.config)
		layout = model.SK1Layout()
		self.model.childs.append(layout)
		self.model.layout = layout
		grid = model.SK1Grid()
		self.model.childs.append(grid)
		self.model.grid = grid
		pages = model.SK1Pages()
		self.model.childs.append(pages)
		self.model.pages = pages
		page = model.SK1Page()
		pages.childs.append(page)
		page.childs.append(model.SK1Layer())
		mlayer = model.SK1MasterLayer()
		self.model.childs.append(mlayer)
		self.model.masterlayer = mlayer
		glayer = model.SK1GuideLayer()
		self.model.childs.append(glayer)
		self.model.guidelayer = glayer
		self.update()

	def traslate_from_pdxf(self, pdxf_doc):
		translator = PDXF_to_SK1_Translator()
		model = pdxf_doc.model
		objs = [] + model.childs[0].childs[0].childs + model.childs[1].childs
		translator.translate(objs, self)

	def traslate_to_pdxf(self, pdxf_doc):
		translator = SK1_to_PDXF_Translator()
		translator.translate(self, pdxf_doc)
