import numpy
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


def det(a, b):
    return a[0] * b[1] - a[1] * b[0]


def collinear(p0, p1, p2):
    x1, y1 = p1[0] - p0[0], p1[1] - p0[1]
    x2, y2 = p2[0] - p0[0], p2[1] - p0[1]
    return abs(x1 * y2 - x2 * y1) < 1e-12
    

def main(gx, gy, gz, gz_2, path):
    step = gx[1] - gx[0]
    path_interp = []
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i+1]
        dx = x2 - x1
        dy = y2 - y1
        d = (dx**2+dy**2)**0.5
        ni = int(d / step + 0.5)
        for j in range(ni+1):
            xi = x1 + j / ni * dx
            yi = y1 + j / ni * dy
            path_interp.append([xi, yi])

    path_masked = []
    for i, point in enumerate(path_interp):
        x, y = point
        j = numpy.argmin(numpy.abs(gx - x))
        k = numpy.argmin(numpy.abs(gy - y))
        z = gz_2[k][j]
        if z:
            path_masked.append([x, y])

    new_path = []
    n_valid = len(path_masked) - 1
    for i in range(n_valid):
        x1, y1 = path_masked[i]
        x2, y2 = path_masked[i+1]
        if i == 0:
            new_path.append([x1, y1])
        if ((x2 - x1)**2+(y2 - y1)**2)**0.5 < step * 2**0.5:
            new_path.append([x2, y2])
            continue
        grid = Grid(matrix=gz_2)
        start = grid.node(numpy.argmin(numpy.abs(gx - x1)), numpy.argmin(numpy.abs(gy - y1)))
        end = grid.node(numpy.argmin(numpy.abs(gx - x2)), numpy.argmin(numpy.abs(gy - y2)))
        path, runs = AStarFinder(
            # diagonal_movement=DiagonalMovement.always
        ).find_path(start, end, grid)
        for j, node in enumerate(path[1:-1]):
            x = gx[node.x]
            y = gy[node.y]
            new_path.append([x, y])
        new_path.append([x2, y2])

    while len(new_path) >= 3:  # Remove aligned points
        stop = True
        for i in range(1, len(new_path)-1):
            p0 = new_path[i-1]
            p1 = new_path[i]
            p2 = new_path[i+1]
            if collinear(p0, p1, p2):
                stop = False
                new_path.pop(i)
                break
        if stop:
            break

    while len(new_path) >= 3:  # Remove useless points for obstacles avoidance
        stop = True
        for i in range(1, len(new_path)-1):
            x0, y0 = new_path[i-1]
            x2, y2 = new_path[i+1]
            dx = x2 - x0
            dy = y2 - y0
            ni = int((dx**2+dy**2)**0.5 / step + 0.5)
            valid = True
            for j in range(ni+1):
                xi = x0 + j / ni * dx
                yi = y0 + j / ni * dy
                ix = numpy.argmin(numpy.abs(gx - xi))
                iy = numpy.argmin(numpy.abs(gy - yi))
                z = gz[iy][ix]
                if not z:
                    valid = False
                    break
            if valid:
                node = new_path[i]
                if node not in path_masked:
                    new_path.pop(i)
                else:
                    continue
                stop = False
                break
        if stop:
            break

    while len(new_path) >= 3:  # Remove singles points on scan
        stop = True
        for i in range(1, len(new_path)-1):
            x0, y0 = new_path[i-1]
            x1, y1 = new_path[i]
            x2, y2 = new_path[i+1]

            is_in_previous = [x0, y0] in path_masked
            is_in_actual = [x1, y1] in path_masked
            is_in_next = [x2, y2] in path_masked

            if is_in_actual and not is_in_previous and not is_in_next:
                new_path.pop(i)
                stop = False
                break
        if stop:
            break

    while len(new_path) >= 3:  # Remove colinear waypionts
        stop = True
        for i in range(1, len(new_path)-1):
            x0, y0 = new_path[i-1]
            x1, y1 = new_path[i]
            x2, y2 = new_path[i+1]

            xdiff = (x0 - x1, x1 - x2)
            ydiff = (y0 - y1, y1 - y2)
            div = det(xdiff, ydiff)

            if abs(div) < 1e-10:
                new_path.pop(i)
                stop = False
                break
        if stop:
            break

    return numpy.array(new_path)
