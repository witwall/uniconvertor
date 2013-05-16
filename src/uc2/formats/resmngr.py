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

import os, shutil

from uc2.utils import generate_id
from uc2.utils.system import WINDOWS, get_os_family
from uc2.formats.pdxf import const

OS_FAMILY = get_os_family()

def convert_resource_path(path):
	if OS_FAMILY == WINDOWS:
		path = path.replace('/', '\\')
	return path

class ResourceManager:

	def __init__(self, presenter):
		self.presenter = presenter
		self.doc_dir = presenter.doc_dir

	def get_resource_path(self, id):
		ret = None
		res_dict = self.presenter.model.resources
		if id in res_dict.keys():
			respath = convert_resource_path(res_dict[id])
			path = os.path.join(self.doc_dir, respath)
			if os.path.isfile(path):
				ret = path
		return ret

	def get_resource(self, id):
		ret = None
		res_dict = self.presenter.model.resources
		if id in res_dict.keys():
			ret = res_dict[id]
		return ret

	def copy_resources(self, rm, resources=[]):
		for id in resources:
			self.copy_resource(rm, id)

	def copy_resource(self, rm, id):
		filepath = rm.get_resource_path(id)
		if not filepath is None and os.path.isfile(filepath):
			place = rm.get_resource(id).split('/')[0]
			self.registry_file(filepath, place, id)

	def delete_resources(self, resources=[], rmfile=False):
		for id in resources:
			self.delete_resource(id, rmfile)

	def delete_resource(self, id, rmfile=False):
		res_dict = self.presenter.model.resources
		filepath = self.get_resource_path(id)
		if id in res_dict.keys():
			res_dict.pop(id)
			if rmfile and not filepath is None:
				try:
					os.remove(filepath)
				except:pass

	def registry_file(self, filepath, place, id):
		ret = None
		if os.path.isfile(filepath):
			if id is None:
				id = generate_id()
			filename = os.path.basename(filepath)
			ext = os.path.splitext(filename)[1]
			dst_filename = id + ext
			dst_dir = os.path.join(self.doc_dir, place)
			dst = os.path.join(dst_dir, dst_filename)
			try:
				shutil.copyfile(filepath, dst)
				res_dict = self.presenter.model.resources
				res_dict[id] = place + '/' + dst_filename
				ret = id
			except: pass
		return ret

	def registry_profile(self, filepath, id=None):
		return self.registry_file(filepath, const.DOC_PROFILE_DIR, id)

	def registry_image(self, filepath, id=None):
		return self.registry_file(filepath, const.DOC_IMAGE_DIR, id)

	def registry_preview(self, filepath, id=None):
		return self.registry_file(filepath, const.DOC_PREVIEW_DIR, id)

if __name__ == '__main__':
	print OS_FAMILY
	print convert_resource_path('Image/test.png')
