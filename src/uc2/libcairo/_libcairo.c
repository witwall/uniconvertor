/* _cairo - small package which provides extended binding to Cairo library.
 *
 * Copyright (C) 2011 by Igor E.Novikov
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <Python.h>
#include <pycairo.h>
#include <cairo.h>

static Pycairo_CAPI_t *Pycairo_CAPI;

static PyObject *
cairo_DrawRectangle (PyObject *self, PyObject *args) {

	double x, y, w, h;
	PycairoContext *context;
	cairo_t *ctx;

	if (!PyArg_ParseTuple(args, "Odddd", &context, &x, &y, &w, &h)) {
		return NULL;
	}

	ctx = context -> ctx;
	cairo_rectangle(ctx, x, y, w, h);

	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *
cairo_ApplyTrafoToPath (PyObject *self, PyObject *args) {

	double m11, m12, m21, m22, dx, dy, x, y;
    int i;
	PycairoPath *pypath;
    cairo_path_t *path;
    cairo_path_data_t *data;

	if (!PyArg_ParseTuple(args, "Odddddd",
			&pypath, &m11, &m12, &m21, &m22, &dx, &dy)) {
		return NULL;
	}

    path = pypath ->path;

    for (i=0; i < path->num_data; i += path->data[i].header.length) {
        data = &path->data[i];
		switch (data->header.type) {
			case CAIRO_PATH_MOVE_TO:
				x = data[1].point.x;
				y = data[1].point.y;
				data[1].point.x = m11 * x + m12 * y + dx;
				data[1].point.y = m21 * x + m22 * y + dy;
				break;
			case CAIRO_PATH_LINE_TO:
				x = data[1].point.x;
				y = data[1].point.y;
				data[1].point.x = m11 * x + m12 * y + dx;
				data[1].point.y = m21 * x + m22 * y + dy;
				break;
			case CAIRO_PATH_CURVE_TO:
				x = data[1].point.x;
				y = data[1].point.y;
				data[1].point.x = m11 * x + m12 * y + dx;
				data[1].point.y = m21 * x + m22 * y + dy;

				x = data[2].point.x;
				y = data[2].point.y;
				data[2].point.x = m11 * x + m12 * y + dx;
				data[2].point.y = m21 * x + m22 * y + dy;

				x = data[3].point.x;
				y = data[3].point.y;
				data[3].point.x = m11 * x + m12 * y + dx;
				data[3].point.y = m21 * x + m22 * y + dy;
				break;
			case CAIRO_PATH_CLOSE_PATH:
				break;
        }
    }

	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *
cairo_ConvertMatrixToTrafo (PyObject *self, PyObject *args) {

	double m11, m12, m21, m22, dx, dy;
	PycairoMatrix *py_matrix;
	cairo_matrix_t *matrix;

	if (!PyArg_ParseTuple(args, "O", &py_matrix)) {
		return NULL;
	}

	matrix = &(py_matrix -> matrix);
	m11 = matrix -> xx;
	m12 = matrix -> xy;
	m21 = matrix -> yx;
	m22 = matrix -> yy;
	dx = matrix -> x0;
	dy = matrix -> y0;

	return Py_BuildValue("[dddddd]", m11, m12, m21, m22, dx, dy);
}

static
PyMethodDef cairo_methods[] = {
	{"draw_rect", cairo_DrawRectangle, METH_VARARGS},
	{"get_trafo", cairo_ConvertMatrixToTrafo, METH_VARARGS},
	{"apply_trafo", cairo_ApplyTrafoToPath, METH_VARARGS},
	{NULL, NULL}
};

void
init_libcairo(void)
{
    Py_InitModule("_libcairo", cairo_methods);
    Pycairo_IMPORT;
}