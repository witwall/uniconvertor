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
# Routines for build procedures
#
############################################################

#Return directory list for provided path
def get_dirs(path='.'):
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

#Return full  directory names list for provided path	
def get_dirs_withpath(path='.'):
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

#Return file list for provided path
def get_files(path='.', ext='*'):
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

#Return full file names list for provided path
def get_files_withpath(path='.', ext='*'):
	import glob
	list = glob.glob(os.path.join(path, "*." + ext))
	list.sort()
	result = []
	for file in list:
		if os.path.isfile(file):
			result.append(file)
	return result

#Return recursive directories list for provided path
def get_dirs_tree(path='.'):
	tree = get_dirs_withpath(path)
	res = [] + tree
	for node in tree:
		subtree = get_dirs_tree(node)
		res += subtree
	return res

#Return recursive files list for provided path
def get_files_tree(path='.', ext='*'):
	tree = []
	dirs = [path, ]
	dirs += get_dirs_tree(path)
	for dir in dirs:
		list = get_files_withpath(dir, ext)
		list.sort()
		tree += list
	return tree

#Generates *.mo files Resources/Messages
def generate_locales():
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
	os.system('rm -f MANIFEST')
	os.system('rm -rf build')

def make_source_list(path, file_list=[]):
	ret = []
	for item in file_list:
		ret.append(os.path.join(path, item))
	return ret

INIT_FILE = '__init__.py'

def is_package(dir):
	if os.path.isdir(dir):
		marker = os.path.join(dir, INIT_FILE)
		if os.path.isfile(marker): return True
	return False

def get_packages(path):
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
	pkgs = []
	for item in get_packages(path):
		res = item.replace('\\', '.').replace('/', '.').replace(path + '.', '')
		pkgs.append(res)
	return pkgs

def compile_sources():
	import compileall
	compileall.compile_dir('build')


def copy_modules(modules):
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

class DEB_Builder:

	name = None
	version = None
	pkg_dirs = []
	scripts = []

	py_version = ''
	arch = ''
	machine = ''
	build_dir = 'build/deb-root'
	src = ''
	dst = ''
	bin_dir = ''
	pixmaps_dir = ''
	package_name = ''

	def __init__(self, name, version, pkg_dirs, scripts=[]):
		self.name = name
		self.version = version
		self.pkg_dirs = pkg_dirs
		self.scripts = scripts

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

	def clear_build(self):
		if os.path.lexists(self.build_dir):
			os.system('rm -rf ' + self.build_dir)
		if os.path.lexists('dist'):
			os.system('rm -rf dist/*.deb')
		else:
			os.makedirs('dist')

	def write_control(self):
		cmd = 'cat debian/control'
		cmd += "|sed 's/<PLATFORM>/" + self.arch + "/g'"
		cmd += "|sed 's/<VERSION>/" + self.version + "/g'"
		cmd += "> build/deb-root/DEBIAN/control"
		os.system(cmd)

	def copy_build(self):
		for dir in self.pkg_dirs:
			os.system('cp -R %s %s' % (self.src + '/' + dir, self.dst))

	def copy_scripts(self):
		if self.scripts: os.makedirs(self.bin_dir)
		for item in self.scripts:
			os.system('cp %s %s' % (item, self.bin_dir))

	def make_package(self):
		os.system('dpkg --build %s/ dist/%s' % (self.build_dir, self.package_name))

	def build(self):
		if not os.path.isdir('build'):
			print 'There is no project build! Run "setup.py build" and try again.'
			return False
		self.clear_build()
		os.makedirs('build/deb-root/DEBIAN')
		self.write_control()
		os.makedirs(self.dst)
		self.copy_build()
		self.copy_scripts()
		self.make_package()
		return True


if __name__ == '__main__':
	packages = get_source_structure()
	for item in packages:
		print item