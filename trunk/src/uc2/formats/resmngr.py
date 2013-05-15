# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011-2013 by Igor E. Novikov
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

class ResourceManager:

	def __init__(self, presenter):
		self.presenter = presenter
		self.doc_dir = presenter.doc_dir

	def get_resource(self, id):
		ret = None
		res_dict = self.presenter.model.resources
		if id in res_dict.keys():
			path = os.path.join(self.doc_dir, res_dict[id])
			if os.path.isfile(path):
				ret = path
		return ret

	def copy_resources(self, rm, resources=[]):
		for id in resources:
			self.copy_resource(rm, id)

	def copy_resource(self, rm, id):pass

	def delete_resources(self, resources=[], rmfile=False):
		for id in resources:
			self.delete_resource(id, rmfile)

	def delete_resource(self, id, rmfile=False):pass
	def registry_profile(self, filepath):pass
	def registry_image(self, filepath):pass
