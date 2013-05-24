#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# Setup utils module
#
# Copyright (C) 2013 Igor E. Novikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA
#

import os, sys

############################################################
#
# File system routines
#
############################################################

def get_dirs(path='.'):
	"""
	Return directory list for provided path
	"""
	list = []
	if path:
		if os.path.isdir(path):
			try:
				names = os.listdir(path)
			except os.error:
				return []
		names.sort()
		for name in names:
			if os.path.isdir(os.path.join(path, name)):
				list.append(name)
		return list

def get_dirs_withpath(path='.'):
	"""
	Return full  directory names list for provided path
	"""
	list = []
	names = []
	if os.path.isdir(path):
		try:
			names = os.listdir(path)
		except os.error:
			return names
	names.sort()
	for name in names:
		if os.path.isdir(os.path.join(path, name)) and not name == '.svn':
			list.append(os.path.join(path, name))
	return list

def get_files(path='.', ext='*'):
	"""
	Returns file list for provided path
	"""
	list = []
	if path:
		if os.path.isdir(path):
			try:
				names = os.listdir(path)
			except os.error:
				return []
		names.sort()
		for name in names:
			if not os.path.isdir(os.path.join(path, name)):
				if ext == '*':
					list.append(name)
				elif '.' + ext == name[-1 * (len(ext) + 1):]:
					list.append(name)
	return list

def get_files_withpath(path='.', ext='*'):
	"""
	Returns full file names list for provided path
	"""
	import glob
	list = glob.glob(os.path.join(path, "*." + ext))
	list.sort()
	result = []
	for file in list:
		if os.path.isfile(file):
			result.append(file)
	return result

def get_dirs_tree(path='.'):
	"""
	Returns recursive directories list for provided path
	"""
	tree = get_dirs_withpath(path)
	res = [] + tree
	for node in tree:
		subtree = get_dirs_tree(node)
		res += subtree
	return res

def get_files_tree(path='.', ext='*'):
	"""
	Returns recursive files list for provided path
	"""
	tree = []
	dirs = [path, ]
	dirs += get_dirs_tree(path)
	for dir in dirs:
		list = get_files_withpath(dir, ext)
		list.sort()
		tree += list
	return tree

def generate_locales():
	"""
	Generates *.mo files Resources/Messages
	"""
	print 'LOCALES BUILD'
	files = get_files('po', 'po')
	if len(files):
		for file in files:
			lang = file.split('.')[0]
			po_file = os.path.join('po', file)
			mo_file = os.path.join('src', 'Resources', 'Messages', lang, 'LC_MESSAGES', 'skencil.mo')
			if not os.path.lexists(os.path.join('src', 'Resources', 'Messages', lang, 'LC_MESSAGES')):
				os.makedirs(os.path.join('src', 'share', 'Messages', lang, 'LC_MESSAGES'))
			print po_file, '==>', mo_file
			os.system('msgfmt -o ' + mo_file + ' ' + po_file)

############################################################
#
# Routines for setup build
#
############################################################

def clear_build():
	"""
	Clears build result.
	"""
	os.system('rm -f MANIFEST')
	os.system('rm -rf build')

def make_source_list(path, file_list=[]):
	"""
	Returns list of paths for provided file list.
	"""
	ret = []
	for item in file_list:
		ret.append(os.path.join(path, item))
	return ret

INIT_FILE = '__init__.py'

def is_package(dir):
	"""
	Checks is provided directory a python package.
	"""
	if os.path.isdir(dir):
		marker = os.path.join(dir, INIT_FILE)
		if os.path.isfile(marker): return True
	return False

def get_packages(path):
	"""
	Collects recursively python packages.
	"""
	packages = []
	items = []
	if os.path.isdir(path):
		try:
			items = os.listdir(path)
		except:pass
		for item in items:
			if item == '.svn':continue
			dir = os.path.join(path, item)
			if is_package(dir):
				packages.append(dir)
				packages += get_packages(dir)
	packages.sort()
	return packages

def get_package_dirs(path='src'):
	"""
	Collects root packages.
	"""
	dirs = {}
	items = []
	if os.path.isdir(path):
		try:
			items = os.listdir(path)
		except:pass
		for item in items:
			if item == '.svn':continue
			dir = os.path.join(path, item)
			if is_package(dir):
				dirs[item] = dir
	return dirs


def get_source_structure(path='src'):
	"""
	Returns recursive list of python packages. 
	"""
	pkgs = []
	for item in get_packages(path):
		res = item.replace('\\', '.').replace('/', '.').replace(path + '.', '')
		pkgs.append(res)
	return pkgs

def compile_sources():
	"""
	Compiles python sources in build/ directory.
	"""
	import compileall
	compileall.compile_dir('build')


def copy_modules(modules):
	"""
	Copies native modules into src/
	The routine implements build_update command
	functionality and executed after "setup.py build" command.
	Works on Linux only.
	"""
	import string, platform, shutil

	version = (string.split(sys.version)[0])[0:3]
	machine = platform.machine()
	prefix = 'build/lib.linux-' + machine + '-' + version
	for item in modules:
		path = os.path.join(*item.name.split('.')) + '.so'
		src = os.path.join(prefix, path)
		dst = os.path.join('src', path)
		shutil.copy(src, dst)
		print '>>>Module %s has been copied to src/ directory' % path
	clear_build()


############################################################
#
# DEB package builder
#
############################################################

def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

RM_CODE = 'REMOVING'
MK_CODE = 'CREATING'
CP_CODE = 'COPYING '
ER_CODE = 'ERROR'
INFO_CODE = ''

class DEB_Builder:
	"""
	Represents deb package build object.
	The object implements "setup.py bdist_deb" command.
	Works after regular "setup.py build" command and 
	constructs deb package using build result in build/ directory.
	Arguments:
	
	name - package names
	version - package version
	pkg_dirs - list of root python packages
	scripts - list of executable scripts
	"""

	name = None
	version = None
	pkg_dirs = []
	scripts = []
	data_files = []

	package_name = ''
	installed_size = 0
	py_version = ''
	arch = ''
	machine = ''
	build_dir = 'build/deb-root'
	src = ''
	dst = ''
	bin_dir = ''
	pixmaps_dir = ''
	apps_dir = ''

	def __init__(self, name='', version='', pkg_dirs=[], scripts=[],
				data_files=[]):
		self.name = name
		self.version = version
		self.pkg_dirs = pkg_dirs
		self.scripts = scripts
		self.data_files = data_files

		import string, platform
		self.py_version = (string.split(sys.version)[0])[0:3]

		arch, bin = platform.architecture()
		if arch == '64bit':
			self.arch = 'amd64'
		else:
			self.arch = 'i386'

		self.machine = platform.machine()

		self.src = 'build/lib.linux-%s-%s' % (self.machine, self.py_version)

		self.dst = '%s/usr/lib/python%s/dist-packages' % (self.build_dir, self.py_version)
		self.bin_dir = '%s/usr/bin' % self.build_dir

		self.package_name = 'python-%s-%s_%s.deb' % (self.name, self.version, self.arch)

	def info(self, msg, code=''):
		if code == ER_CODE: ret = '%s>>> %s' % (code, msg)
		elif not code: ret = msg
		else: ret = '%s: %s' % (code, msg)
		print ret

	def _make_dir(self, path):
		self.info('%s directory.' % path, MK_CODE)
		try: os.makedirs(path)
		except: raise IOError('Error while creating %s directory.') % path

	def clear_build(self):
		if os.path.lexists(self.build_dir):
			self.info('%s directory.' % self.build_dir, RM_CODE)
			if os.system('rm -rf ' + self.build_dir):
				raise IOError('Error while removing %s directory.' % self.build_dir)
		if os.path.lexists('dist'):
			self.info('Cleaning dist/ directory.', RM_CODE)
			if os.system('rm -rf dist/*.deb'):
				raise IOError('Error while cleaning dist/ directory.')
		else:
			self._make_dir('dist')

	def write_control(self):
		deb_folder = 'build/deb-root/DEBIAN'
		self._make_dir(deb_folder)
		cmd = 'cat debian/control'
		cmd += "|sed 's/<PLATFORM>/" + self.arch + "/g'"
		cmd += "|sed 's/<VERSION>/" + self.version + "/g'"
		cmd += "|sed 's/<SIZE>/" + self.installed_size + "/g'"
		cmd += "> build/deb-root/DEBIAN/control"
		self.info('Writing Debian control file.', CP_CODE)
		if os.system(cmd):
			raise IOError('Error while writing Debian control file.')
		files = ['debian/postinst', 'debian/postrm',
				'debian/preinst', 'debian/prerm']
		for file in files:
			if os.path.isfile(file):
				self.info('%s -> %s' % (file, deb_folder), CP_CODE)
				if os.system('cp %s %s' % (file, deb_folder)):
					raise IOError('Error while copying %s -> %s' % (file, deb_folder))

	def copy_build(self):
		for dir in self.pkg_dirs:
			src = self.src + '/' + dir
			self.info('%s -> %s' % (src, self.dst), CP_CODE)
			if os.system('cp -R %s %s' % (src, self.dst)):
				raise IOError('Error while copying %s -> %s' % (src, self.dst))

	def copy_scripts(self):
		if self.scripts: self._make_dir(self.bin_dir)
		else:return
		for item in self.scripts:
			self.info('%s -> %s' % (item, self.bin_dir), CP_CODE)
			if os.system('cp %s %s' % (item, self.bin_dir)):
				raise IOError('Cannot copying %s -> %s' % (item, self.bin_dir))
			filename = os.path.basename(item)
			path = os.path.join(self.bin_dir, filename)
			if os.path.isfile(path):
				self.info('%s as executable' % path, MK_CODE)
				if os.system('chmod +x %s' % path):
					raise IOError('Cannot set executable flag for %s' % path)

	def copy_files(self, path, files):
		if files and not os.path.isdir(path): self._make_dir(path)
		if not files:return
		for item in files:
			self.info('%s -> %s' % (item, path), CP_CODE)
			if os.system('cp %s %s' % (item, path)):
				raise IOError('Cannot copying %s -> %s' % (item, path))

	def copy_data_files(self):
		for item in self.data_files:
			path, files = item
			self.copy_files(self.build_dir + path, files)

	def make_package(self):
		self.info('%s package.' % self.package_name, MK_CODE)
		if os.system('dpkg --build %s/ dist/%s' % (self.build_dir, self.package_name)):
			raise IOError('Cannot create package %s' % self.package_name)

	def build(self):
		line = '=' * 30
		self.info(line + '\n' + 'DEB PACKAGE BUILD' + '\n' + line)
		try:
			if not os.path.isdir('build'):
				raise IOError('There is no project build! '
							'Run "setup.py build" and try again.')
			self.clear_build()
			self._make_dir(self.dst)
			self.copy_build()
			self.copy_scripts()
			self.copy_data_files()
			self.installed_size = str(int(get_size(self.build_dir) / 1024))
			self.write_control()
			self.make_package()
		except IOError as e:
			self.info(e, ER_CODE)
			self.info(line + '\n' + 'BUILD FAILED!')
			return 1
		self.info(line + '\n' + 'BUILD SUCCESSFUL!')
		return 0

if __name__ == '__main__':
	packages = get_package_dirs()
	print packages
