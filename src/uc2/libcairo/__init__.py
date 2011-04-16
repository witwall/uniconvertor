# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011 by Igor E. Novikov
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

import cairo
import _libcairo

CTX = cairo.Context(cairo.ImageSurface(cairo.FORMAT_RGB24, 100, 100))
DIRECT_MATRIX = cairo.Matrix()

def create_cpath(paths, cmatrix=None):
	CTX.set_matrix(DIRECT_MATRIX)
	CTX.new_path()
	for path in paths:
		start_point = path[0]
		points = path[1]
		end = path[2]
		x, y = start_point
		CTX.move_to(x, y)
		for point in points:
			if len(point) == 2:
				x, y = point
				CTX.line_to(x, y)
			else:
				p1, p2, p3, m = point
				x1, y1 = p1
				x2, y2 = p2
				x3, y3 = p3
				CTX.curve_to(x1, y1, x2, y2, x3, y3)
		if end:
			CTX.close_path()

	cairo_path = CTX.copy_path()
	if not cmatrix is None:
		cairo_path = apply_cmatrix(cairo_path, cmatrix)
	return cairo_path

def apply_cmatrix(cairo_path, cmatrix):
	trafo = get_trafo_from_matrix(cmatrix)
	return apply_trafo(cairo_path, trafo)

def copy_cpath(cairo_path):
	CTX.set_matrix(DIRECT_MATRIX)
	CTX.new_path()
	CTX.append_path(cairo_path)
	return CTX.copy_path()

def apply_trafo(cairo_path, trafo, copy=False):
	if copy:
		cairo_path = copy_cpath(cairo_path)
	m11, m12, m21, m22, dx, dy = trafo
	_libcairo.apply_trafo(cairo_path, m11, m12, m21, m22, dx, dy)
	return cairo_path

def multiply_trafo(trafo1, trafo2):
	matrix1 = get_matrix_from_trafo(trafo1)
	matrix2 = get_matrix_from_trafo(trafo2)
	matrix = matrix1 * matrix2
	return _libcairo.get_trafo(matrix)

def normalize_bbox(bbox):
	x0, y0, x1, y1 = bbox
	new_bbox = [0, 0, 0, 0]
	if x0 < x1:
		new_bbox[0] = x0
		new_bbox[2] = x1
	else:
		new_bbox[0] = x1
		new_bbox[2] = x0 - x1
	if y0 < y1:
		new_bbox[1] = y0
		new_bbox[3] = y1
	else:
		new_bbox[1] = y1
		new_bbox[3] = y0
	return new_bbox

def get_cpath_bbox(cpath):
	CTX.set_matrix(DIRECT_MATRIX)
	CTX.new_path()
	CTX.append_path(cpath)
	return normalize_bbox(CTX.path_extents())

def sum_bbox(bbox1, bbox2):
	x0, y0, x1, y1 = bbox1
	_x0, _y0, _x1, _y1 = bbox2
	new_x0 = min(x0, _x0, x1, _x1)
	new_x1 = max(x0, _x0, x1, _x1)
	new_y0 = min(y0, _y0, y1, _y1)
	new_y1 = max(y0, _y0, y1, _y1)
	return [new_x0, new_y0, new_x1, new_y1]

def is_bbox_in_rect(rect, bbox):
	x0, y0, x1, y1 = rect
	_x0, _y0, _x1, _y1 = bbox
	if x0 > _x0: return False
	if y0 > _y0: return False
	if x1 < _x1: return False
	if y1 < _y1: return False
	return True

def _get_trafo(cmatrix):
	result = []
	val = cmatrix.__str__()
	val = val.replace('cairo.Matrix(', '')
	val = val.replace(')', '')
	items = val.split(', ')
	for item in items:
		val = item.replace(',', '.')
		result.append(float(val))
	return result

def get_trafo_from_matrix(cmatrix):
	return _libcairo.get_trafo(cmatrix)

def reverse_trafo(trafo):
	m11, m12, m21, m22, dx, dy = trafo
	if m11: m11 = 1.0 / m11
	if m12: m12 = 1.0 / m12
	if m21: m21 = 1.0 / m21
	if m22: m22 = 1.0 / m22
	dx = -dx
	dy = -dy
	return [m11, m12, m21, m22, dx, dy]

def get_matrix_from_trafo(trafo):
	m11, m12, m21, m22, dx, dy = trafo
	return cairo.Matrix(m11, m21, m12, m22, dx, dy)

def reverse_matrix(cmatrix):
	return get_matrix_from_trafo(_get_trafo(cmatrix))

def apply_trafo_to_point(point, trafo):
	x0, y0 = point
	m11, m12, m21, m22, dx, dy = trafo
	x1 = m11 * x0 + m12 * y0 + dx
	y1 = m21 * x0 + m22 * y0 + dy
	return [x1, y1]

def apply_trafo_to_bbox(bbox, trafo):
	x0, y0, x1, y1 = bbox
	start = apply_trafo_to_point([x0, y0], trafo)
	end = apply_trafo_to_point([x1, y1], trafo)
	return start + end

def convert_bbox_to_cpath(bbox):
	x0, y0, x1, y1 = bbox
	CTX.set_matrix(DIRECT_MATRIX)
	CTX.new_path()
	CTX.move_to(x0, y0)
	CTX.line_to(x1, y0)
	CTX.line_to(x1, y1)
	CTX.line_to(x0, y1)
	CTX.line_to(x0, y0)
	CTX.close_path()
	return CTX.copy_path()

def _test():
	_get_trafo(DIRECT_MATRIX)
	print get_trafo_from_matrix(DIRECT_MATRIX)
	paths = [
			[[0.0, 0.0], [
						[100.0, 50.0], [200.0, 40.0], [400.0, 10.0]
						], []]
			]
	cpath = create_cpath(paths)
	trafo = [1.0, 0.0, 0.0, 2.0, 20.0, 30.0]
	print apply_cmatrix(cpath, get_matrix_from_trafo(trafo))

#	print reverse_trafo(trafo)
#	print get_matrix_from_trafo(trafo)



if __name__ == '__main__':
	_test()
