import math
import numpy
from shapely.geometry import Point, Polygon


def dist_point(x, y, x1, y1):
    return ((x-x1)**2 + (y-y1)**2)**0.5
    

def main(path, obstacles_points=None, obstacles_lines=None, obstacles_polygons=None, step=0.1, radius=0.5):

    radius_2 = radius * math.tan(math.pi/6) * 2
    if obstacles_points is None:
        obstacles_points = []
    if obstacles_lines is None:
        obstacles_lines = []
    if obstacles_polygons is None:
        obstacles_polygons = []
        
    px, py = path.T
    min_x = numpy.min(px)
    max_x = numpy.max(px)
    min_y = numpy.min(py)
    max_y = numpy.max(py)
    
    for point in obstacles_points:
        xi, yi = point
        min_x = min(min_x, xi)
        max_x = max(max_x, xi)
        min_y = min(min_y, yi)
        max_y = max(max_y, yi)
    for line in obstacles_lines:
        for point in line:
            xi, yi = point
            min_x = min(min_x, xi)
            max_x = max(max_x, xi)
            min_y = min(min_y, yi)
            max_y = max(max_y, yi)
    for polygon in obstacles_polygons:
        for point in polygon:
            xi, yi = point
            min_x = min(min_x, xi)
            max_x = max(max_x, xi)
            min_y = min(min_y, yi)
            max_y = max(max_y, yi)
    
    min_x -= radius_2 + step * 2
    max_x += radius_2 + step * 2
    min_y -= radius_2 + step * 2
    max_y += radius_2 + step * 2
    
    lx = max_x - min_x
    nx = int(lx / step + 0.5)
    
    ly = max_y - min_y
    ny = int(ly / step + 0.5)
    
    gx = [min_x + i / nx * lx + step / 2 for i in range(nx)]
    gy = [min_y + j / ny * ly + step / 2 for j in range(ny)]
    gz = numpy.ones((ny, nx))
    gz_2 = numpy.ones((ny, nx))

    for i, x in enumerate(gx):
        for j, y in enumerate(gy):
            valid = True
            for k, point in enumerate(obstacles_points):
                ox, oy = point
                distance = dist_point(x, y, ox, oy)
                valid = distance > radius
                if not valid:
                    break
            if not valid:
                gz[j][i] = 0
                continue
            for k, line in enumerate(obstacles_lines):
                distance = float("inf")
                n_line = len(line) - 1
                for l in range(n_line):
                    x1, y1 = line[l]
                    x2, y2 = line[l+1]
                    dx = x2 - x1
                    dy = y2 - y1
                    dist = dist_point(x2, y2, x1, y1)
                    ni = int(dist / step + 0.5)
                    for m in range(ni+1):
                        x3 = x1 + m / ni * dx
                        y3 = y1 + m / ni * dy
                        distance = min(distance, dist_point(x, y, x3, y3))
                valid = distance > radius
                if not valid:
                    break
            if not valid:
                gz[j][i] = 0
                continue
            for k, polygon in enumerate(obstacles_polygons):
                n_poly = len(polygon)
                for l in range(n_poly):
                    x1, y1 = polygon[l]
                    x2, y2 = (polygon)[(l+1)%n_poly]
                    dx = x2 - x1
                    dy = y2 - y1
                    dist = dist_point(x2, y2, x1, y1)
                    ni = int(dist / step + 0.5)
                    for m in range(ni+1):
                        x3 = x1 + m / ni * dx
                        y3 = y1 + m / ni * dy
                        distance = min(distance, dist_point(x, y, x3, y3))
                valid_distance = distance > radius
                valid_inpoly = not Polygon(polygon).contains(Point(x, y))
                valid = valid_distance * valid_inpoly
                if not valid:
                    break      
            if not valid:
                gz[j][i] = 0
                continue

    return gx, gy, gz
