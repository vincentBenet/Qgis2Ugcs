import math
import numpy


def det(a, b):
    return a[0] * b[1] - a[1] * b[0]


def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])
    div = det(xdiff, ydiff)
    if div == 0:
        return float("inf"), float("inf")
    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


def main(path, width, side):
    n_side = int(width / side)
    n_segment = len(path) - 1
    paths = []
    dists = numpy.linspace(-width/2, width/2, n_side)
    for j, dist in enumerate(dists):
        path_add = []
        for i in range(n_segment):
            x1, y1 = path[i]
            x2, y2 = path[i+1]
            dx = x2 - x1
            dy = y2 - y1
            azimuth = math.atan2(dx, dy)
            xi = x1 - dist * math.cos(azimuth)
            yi = y1 + dist * math.sin(azimuth)
            path_add.append([xi, yi])
            xi = x2 - dist * math.cos(azimuth)
            yi = y2 + dist * math.sin(azimuth)
            path_add.append([xi, yi])
        paths.append(path_add)

    crossings = []
    intersects = []
    for i in range(len(paths)):
        crossings.append([])
        intersects.append([])
        path_add = paths[i]
        n_segment = len(path_add) - 3
        for j in range(n_segment):
            x1, y1 = path_add[j]
            x2, y2 = path_add[j + 1]
            x3, y3 = path_add[j + 2]
            x4, y4 = path_add[j + 3]
            xi, yi = line_intersection([[x1, y1], [x2, y2]], [[x3, y3], [x4, y4]])
            is_inside_1_x1i = x1 <= xi or abs(xi - x1) < 0.1
            is_inside_1_xi2 = xi <= x2 or abs(x2 - xi) < 0.1
            is_inside_1_1x = is_inside_1_x1i and is_inside_1_xi2
            is_inside_1_x2i = x2 <= xi or abs(xi - x2) < 0.1
            is_inside_1_xi1 = xi <= x1 or abs(x1 - xi) < 0.1
            is_inside_1_2x = is_inside_1_x2i and is_inside_1_xi1
            is_inside_1_x = is_inside_1_1x or is_inside_1_2x
            is_inside_2_x3i = x3 <= xi or abs(xi - x3) < 0.1
            is_inside_2_xi4 = xi <= x4 or abs(x4 - xi) < 0.1
            is_inside_2_1x = is_inside_2_x3i and is_inside_2_xi4
            is_inside_2_x4i = x4 <= xi or abs(xi - x4) < 0.1
            is_inside_2_xi3 = xi <= x3 or abs(x3 - xi) < 0.1
            is_inside_2_2x = is_inside_2_x4i and is_inside_2_xi3
            is_inside_2_x = is_inside_2_1x or is_inside_2_2x
            is_inside_1_y1i = y1 <= yi or abs(yi - y1) < 0.1
            is_inside_1_yi2 = yi <= y2 or abs(y2 - yi) < 0.1
            is_inside_1_1y = is_inside_1_y1i and is_inside_1_yi2
            is_inside_1_y2i = y2 <= yi or abs(yi - y2) < 0.1
            is_inside_1_yi1 = yi <= y1 or abs(y1 - yi) < 0.1
            is_inside_1_2y = is_inside_1_y2i and is_inside_1_yi1
            is_inside_1_y = is_inside_1_1y or is_inside_1_2y
            is_inside_2_y3i = y3 <= yi or abs(yi - y3) < 0.1
            is_inside_2_yi4 = yi <= y4 or abs(y4 - yi) < 0.1
            is_inside_2_1y = is_inside_2_y3i and is_inside_2_yi4
            is_inside_2_y4i = y4 <= yi or abs(yi - y4) < 0.1
            is_inside_2_yi3 = yi <= y3 or abs(y3 - yi) < 0.1
            is_inside_2_2y = is_inside_2_y4i and is_inside_2_yi3
            is_inside_2_y = is_inside_2_1y or is_inside_2_2y
            is_inside_1 = is_inside_1_x and is_inside_1_y
            is_inside_2 = is_inside_2_x and is_inside_2_y
            is_intersect = is_inside_1 and is_inside_2
            crossings[i].append(is_intersect)
            intersects[i].append([xi, yi])

    paths_new = []
    for i in range(len(crossings)):
        paths_new.append([])
        nj = len(crossings[i])
        continue_next = -1
        paths_new[i].append(paths[i][0])
        for j in range(nj):
            if continue_next > 0:
                continue_next -= 1
                continue

            if crossings[i][j]:
                paths_new[i].append(intersects[i][j])
                continue_next = 1
            else:
                paths_new[i].append(paths[i][j+1])
                if j == nj - 1:
                    paths_new[i].append(paths[i][-2])
        paths_new[i].append(paths[i][-1])

    path_new = []
    for i in range(len(paths_new)):
        path_to_add = paths_new[i]
        if i % 2 == 1:
            path_to_add.reverse()
        for point in path_to_add:
            path_new.append(point)

    return numpy.array(path_new)
