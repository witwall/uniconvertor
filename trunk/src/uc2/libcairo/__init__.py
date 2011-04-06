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

CTX = cairo.Context(cairo.ImageSurface(cairo.FORMAT_RGB24, 10, 10))
DIRECT_MATRIX = cairo.Matrix(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

#Paths definition:
#[path0, path1, ...]

#Path definition:
#[start_point, points, end_marker]
#start_pont - [x,y]
#end_ marker - is closed [1] if not []

#Points definition:
#[point0, point1,...]
# line point - [x,y]
# curve point - [[x1,y1],[x2,y2],[x3,y3], marker]

def create_cpath(paths, matrix):
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
	return CTX.copy_path()

def apply_cmatrix(cairo_path, cmatrix):
	CTX.set_matrix(DIRECT_MATRIX)
	CTX.new_path()
	CTX.append_path(cairo_path)
	CTX.transform(cmatrix)
	return CTX.copy_path()

def get_cpath_bbox(cpath):
	CTX.set_matrix(DIRECT_MATRIX)
	CTX.new_path()
	CTX.append_path(cpath)
	return CTX.path_extents()

def get_trafo_from_matrix(cmatrix):
	return []
