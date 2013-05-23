#!/usr/bin/env python
#
# Setup script for UniConvertor 2.x
#
# Copyright (C) 2011, 2012 Igor E. Novikov
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
#  to build against LCMS2 use flag --with-lcms2. For example:
#  python setup.py bdist_rpm --with-lcms2
# --------------------------------------------------------------------------
#
#  help on available distribution formats: python setup.py bdist --help-formats
#

import os, sys

import libutils
from libutils import make_source_list

UPDATE_MODULES = False
DEBIAN = False
LCMS2 = False
VERSION = '2.0'

############################################################
#
# Main build procedure
#
############################################################

if __name__ == "__main__":

	if len(sys.argv) > 1 and sys.argv[1] == 'build_update':
		UPDATE_MODULES = True
		sys.argv[1] = 'build'

	if len(sys.argv) > 1 and sys.argv[1] == 'bdist_deb':
		DEBIAN = True
		sys.argv[1] = 'build'

	if len(sys.argv) > 2 and sys.argv[2] == '--with-lcms2':
		sys.argv.remove('--with-lcms2')
		LCMS2 = True

	from distutils.core import setup, Extension

	src_path = 'src'
	include_path = '/usr/include'
	modules = []
	scripts = ['src/uniconvertor', ]

	filter_src = os.path.join(src_path, 'uc2', 'utils', 'streamfilter')
	files = ['streamfilter.c', 'filterobj.c', 'linefilter.c',
			'subfilefilter.c', 'base64filter.c', 'nullfilter.c',
			'stringfilter.c', 'binfile.c', 'hexfilter.c']
	files = make_source_list(filter_src, files)
	filter_module = Extension('uc2.utils.streamfilter',
			define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
			sources=files)
	modules.append(filter_module)

 	sk1objs_src = os.path.join(src_path, 'uc2', 'formats', 'sk1', 'sk1objs')
 	files = ['_sketchmodule.c', 'skpoint.c', 'skcolor.c', 'sktrafo.c',
			'skrect.c', 'skfm.c', 'curvefunc.c', 'curveobject.c', 'curvelow.c',
			'curvemisc.c', 'skaux.c', 'skimage.c', ]
 	files = make_source_list(sk1objs_src, files)
	sk1objs_module = Extension('uc2.formats.sk1._sk1objs',
			define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
			sources=files)
	modules.append(sk1objs_module)

	cairo_src = os.path.join(src_path, 'uc2', 'libcairo')
	files = make_source_list(cairo_src, ['_libcairo.c', ])
	include_dirs = make_source_list(include_path, ['cairo', 'pycairo'])
	cairo_module = Extension('uc2.libcairo._libcairo',
			define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
			sources=files, include_dirs=include_dirs,
			libraries=['cairo'])
	modules.append(cairo_module)

	libimg_src = os.path.join(src_path, 'uc2', 'libimg')
	files = make_source_list(libimg_src, ['_libimg.c', ])
	include_dirs = make_source_list(include_path, ['ImageMagick', ])
	libimg_module = Extension('uc2.libimg._libimg',
			define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
			sources=files, include_dirs=include_dirs,
			libraries=['MagickWand'])
	modules.append(libimg_module)

 	if LCMS2:
	 	pycms_src = os.path.join(src_path, 'uc2', 'cms')
	 	files = make_source_list(pycms_src, ['_cms2.c', ])
		pycms_module = Extension('uc2.cms._cms',
				define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
				sources=files,
				libraries=['lcms2'],
				extra_compile_args=["-Wall"])
		modules.append(pycms_module)
 	else:
	 	pycms_src = os.path.join(src_path, 'uc2', 'cms')
	 	files = make_source_list(pycms_src, ['_cms.c', ])
		pycms_module = Extension('uc2.cms._cms',
				define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
				sources=files,
				libraries=['lcms'],
				extra_compile_args=["-Wall"])
		modules.append(pycms_module)


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

sK1 Project (http://sk1project.org),
Copyright (C) 2007-2013 by Igor E. Novikov
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

			packages=libutils.get_source_structure(),

			package_dir=libutils.get_package_dirs(),

			scripts=scripts,

			ext_modules=modules)

#################################################
# .py source compiling
#################################################
libutils.compile_sources()


##############################################
# This section for developing purpose only
# Command 'python setup.py build&copy' allows
# automating build and native extension copying
# into package directory
##############################################	

if UPDATE_MODULES: libutils.copy_modules(modules)


#################################################
# Implementation of bdist_deb command
#################################################

if DEBIAN:
	print '\n'
	print 'DEBIAN PACKAGE BUILD'
	print '===================='
	builder = libutils.DEB_Builder('uniconvertor',
								VERSION,
								['uc2', ],
								scripts)
	if builder.build():
		print 'Deb package is created successfully'
	else:
		print 'BUILD FAILED!'
