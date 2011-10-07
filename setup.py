#!/usr/bin/env python
#
# Setup script for UniConvertor
#
# Copyright (C) 2011 Igor E. Novikov
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

# Usage: 
# --------------------------------------------------------------------------
#  to build package:   python setup.py build
#  to install package:   python setup.py install
# --------------------------------------------------------------------------
#  to create source distribution:   python setup.py sdist
# --------------------------------------------------------------------------
#  to create binary RPM distribution:  python setup.py bdist_rpm
# --------------------------------------------------------------------------
#  to create localization .mo files: python setup.py build_locales (Linux only)
# --------------------------------------------------------------------------
#
#  help on available distribution formats: python setup.py bdist --help-formats
#

import os, sys


COPY = False
DEBIAN = False
VERSION = '1.0alpha'

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
# Main build procedure
#
############################################################

if __name__ == "__main__":

	if len(sys.argv) > 1 and sys.argv[1] == 'build&copy':
		COPY = True
		sys.argv[1] = 'build'

	if len(sys.argv) > 1 and sys.argv[1] == 'bdist_deb':
		DEBIAN = True
		sys.argv[1] = 'build'


	from distutils.core import setup, Extension

	src_path = 'src/'

	cairo_src = src_path + 'uc2/libcairo/'
	cairo_include_dirs = ['/usr/include/cairo', '/usr/include/pycairo']
	cairo_module = Extension('uc2.libcairo._libcairo',
			define_macros=[('MAJOR_VERSION', '1'),
						('MINOR_VERSION', '0')],
			sources=[cairo_src + '_libcairo.c', ],
			include_dirs=cairo_include_dirs,
			libraries=['cairo'])


	setup (name='uniconvertor',
			version=VERSION,
			description='Universal vector graphics translator',
			author='Igor E. Novikov',
			author_email='igor.e.novikov@gmail.com',
			maintainer='Igor E. Novikov',
			maintainer_email='igor.e.novikov@gmail.com',
			license='GPL v3',
			url='http://sk1project.org',
			download_url='http://sk1project.org/modules.php?name=Products&product=uniconvertor',
			long_description='''
UniConvertor is a multiplatform universal vector graphics translator.
It uses sK1 model to convert one format to another.

sK1 Team (http://sk1project.org),
Copyright (C) 2007-2011 by Igor E. Novikov
------------------------------------------------------------------------------------

Import filters: 
    * CorelDRAW ver.7-X3,X4 (CDR/CDT/CCX/CDRX/CMX)
    * Adobe Illustrator up to 9 ver. (AI postscript based)
    * Postscript (PS)
    * Encapsulated Postscript (EPS)
    * Computer Graphics Metafile (CGM)
    * Windows Metafile (WMF)
    * XFIG
    * Scalable Vector Graphics (SVG)
    * Skencil/Sketch/sK1 (SK and SK1)
    * Acorn Draw (AFF)
    * HPGL for cutting plotter files (PLT)
    * Autocad Drawing Exchange Format (DXF)
    * Design format (Tajima) (DST)
    * Embroidery file format (Brother) (PES)
    * Embroidery file format (Melco) (EXP)
    * Design format (Pfaff home) (PCS)
------------------------------------------------------------------------------------

Export filters: 
    * AI - Postscript based Adobe Illustrator 5.0 format
    * SVG - Scalable Vector Graphics
    * SK - Sketch/Skencil format
    * SK1 - sK1 format
    * CGM - Computer Graphics Metafile
    * WMF - Windows Metafile
    * PDF - Portable Document Format
    * PS  - PostScript
    * PLT - HPGL for cutting plotter files
    
------------------------------------------------------------------------------------
			''',
		classifiers=[
			'Development Status :: 6 - Mature',
			'Environment :: Console',
			'Intended Audience :: End Users/Desktop',
			'License :: OSI Approved :: LGPL v2',
			'License :: OSI Approved :: GPL v2',
			'Operating System :: POSIX',
			'Operating System :: MacOS :: MacOS X',
			'Programming Language :: Python',
			'Programming Language :: C',
			"Topic :: Multimedia :: Graphics :: Graphics Conversion",
			],

			packages=['uc2',
				'uc2.libcairo',
				'uc2.cms',
				'uc2.formats',
				'uc2.sk1doc',
				'uc2.utils',
			],

			package_dir={'uc2': 'src/uc2',
			},

			scripts=['src/uniconvertor'],

			ext_modules=[cairo_module, ])

#################################################
# .py source compiling
#################################################
if sys.argv[1] == 'build':
	import compileall
	compileall.compile_dir('build/')


##############################################
# This section for developing purpose only
# Command 'python setup.py build&copy' allows
# automating build and native extension copying
# into package directory
##############################################	

if COPY:
	import string, platform, shutil
	version = (string.split(sys.version)[0])[0:3]

	shutil.copy('build/lib.linux-' + platform.machine() + '-' + version + '/uc2/libcairo/_libcairo.so', 'src/uc2/libcairo/')
	print '\n _libcairo.so has been copied to src/ directory'

	os.system('rm -rf build')


#################################################
# Implementation of bdist_deb command
#################################################

if DEBIAN:
	print '\nDEBIAN PACKAGE BUILD'
	print '===================='
	import string, platform
	version = (string.split(sys.version)[0])[0:3]

	arch, bin = platform.architecture()
	if arch == '64bit':
		arch = 'amd64'
	else:
		arch = 'i386'

	target = 'build/deb-root/usr/lib/python' + version + '/dist-packages'

	if os.path.lexists(os.path.join('build', 'deb-root')):
		os.system('rm -rf build/deb-root')
	os.makedirs(os.path.join('build', 'deb-root', 'DEBIAN'))

	os.system("cat DEBIAN/control |sed 's/<PLATFORM>/" + arch + "/g'|sed 's/<VERSION>/" + VERSION + "/g'> build/deb-root/DEBIAN/control")

	os.makedirs(target)
	os.makedirs('build/deb-root/usr/bin')
	os.makedirs('build/deb-root/usr/share/applications')
	os.makedirs('build/deb-root/usr/share/pixmaps')

	os.system('cp -R build/lib.linux-' + platform.machine() + '-' + version + '/skencil ' + target)
	os.system('cp src/skencil.desktop build/deb-root/usr/share/applications')
	os.system('cp src/skencil.png build/deb-root/usr/share/pixmaps')
	os.system('cp src/skencil.xpm build/deb-root/usr/share/pixmaps')
	os.system('cp src/skencil build/deb-root/usr/bin')
	os.system('chmod +x build/deb-root/usr/bin/skencil')

	if os.path.lexists('dist'):
		os.system('rm -rf dist/*.deb')
	else:
		os.makedirs('dist')

	os.system('dpkg --build build/deb-root/ dist/python-skencil-' + VERSION + '_' + arch + '.deb')
