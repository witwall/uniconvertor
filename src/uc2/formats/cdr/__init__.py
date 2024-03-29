# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011-2012 by Igor E. Novikov
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

import sys

from uc2 import events, msgconst
from uc2.formats.cdr.presenter import CDR_Presenter
from uc2.formats.cdr import const
from uc2.formats.pdxf.presenter import PDXF_Presenter

def cdr_loader(appdata, filename, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	doc = CDR_Presenter(appdata, cnf)
	doc.load(filename)
	if translate:
		pdxf_doc = PDXF_Presenter(appdata, cnf)
		pdxf_doc.doc_file = filename
		doc.traslate_to_pdxf(pdxf_doc)
		doc.close()
		doc = pdxf_doc
	return doc

def cdr_saver(cdr_doc, filename, translate=True, cnf={}, **kw):
	if kw: cnf.update(kw)
	cdr_doc.save(filename)

def check_cdr(path):
	try:
		file = open(path, 'rb')
	except:
		errtype, value, traceback = sys.exc_info()
		msg = _('Cannot open %s file for reading') % (path)
		events.emit(events.MESSAGES, msgconst.ERROR, msg)
		raise IOError(errtype, msg + '\n' + value, traceback)

	header = file.read(12)
	file.close()
	if not header[:4] == 'RIFF':
		return False
	if header[8:] in const.CDR_VERSIONS:
		return True
	else:
		return False
