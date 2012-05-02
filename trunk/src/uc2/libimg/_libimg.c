/* cms - small module which provides binding to ImageMagick.
 *
 * Copyright (C) 2011-2012 by Igor E.Novikov
 *
 * 	This program is free software: you can redistribute it and/or modify
 *	it under the terms of the GNU General Public License as published by
 *	the Free Software Foundation, either version 3 of the License, or
 *	(at your option) any later version.
 *
 *	This program is distributed in the hope that it will be useful,
 *	but WITHOUT ANY WARRANTY; without even the implied warranty of
 *	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *	GNU General Public License for more details.
 *
 *	You should have received a copy of the GNU General Public License
 *	along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <Python.h>
#include <wand/MagickWand.h>


static PyObject *
im_LoadImage(PyObject *self, PyObject *args) {

	Py_INCREF(Py_None);
	return Py_None;
}

static
PyMethodDef im_methods[] = {
	{"loadImage", im_LoadImage, METH_VARARGS},
	{NULL, NULL}
};

void
init_cms(void)
{
    Py_InitModule("_libimg", im_methods);
}
