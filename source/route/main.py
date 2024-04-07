import math

import numpy
from matplotlib import pyplot as plt

import convolution_obstacles
import pathfinding_obstacles
import segments_to_scan


def plot(pipe, path, new_path, gx, gy, gz, obstacles_points, obstacles_lines, obstacles_polygons):
    min_x, max_x, min_y, max_y = gx[0], gx[-1], gy[0], gy[-1]
    plt.imshow(gz, extent=(min_x, max_x, min_y, max_y), origin="lower")
    for line in obstacles_lines:
        plt.scatter(*line.T, color="white")
        plt.plot(*line.T, color="gray", label="Lines Obstacles")
    for polygon in obstacles_polygons:
        for point in polygon:
            plt.scatter(*point.T, color="green")
        plt.plot(*numpy.array(polygon.tolist() + [polygon[0]]).T, color="green", label="Polygon Obstacles")

    plt.scatter(*obstacles_points.T, label="Obstacles")
    plt.plot(*path.T, color="black", label="Scan")

    plt.plot(*new_path.T, color="red", label="Waypoints")
    plt.scatter(*new_path.T, color="red")
    plt.plot(*pipe.T, color="green", label="Pipeline")
    plt.axis("equal")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    pipe = numpy.array([
        [2, 0],
        [4, 5],
        [6, 6],
        [10, 9]
    ])
    obstacles_points = numpy.array([
        [1, 1],
        [3, 2],
        [4, 4],
        [8, 8],
        [10, -1]
    ])
    obstacles_lines = numpy.array([
        [
            [5, 0],
            [6, 6],
            [2, 6],
        ],
    ])
    obstacles_polygons = numpy.array([
        [
            [2, 9],
            [0, 6],
            [0, 15],
            [5, 14],
        ],
    ])
    step = 0.05
    radius = 0.5
    width = 3
    side = 0.5

    waypoints = segments_to_scan.main(path=pipe, width=width, side=side)

    gx, gy, gz = convolution_obstacles.main(
        path=waypoints,
        step=step,
        radius=radius,
        obstacles_points=obstacles_points,
        obstacles_lines=obstacles_lines,
        obstacles_polygons=obstacles_polygons,
    )

    _, _, gz_2 = convolution_obstacles.main(
        path=waypoints,
        step=step,
        radius=radius * math.tan(math.pi / 6) * 2,
        obstacles_points=obstacles_points,
        obstacles_lines=obstacles_lines,
        obstacles_polygons=obstacles_polygons,
    )

    trajectory = pathfinding_obstacles.main(gx, gy, gz, gz_2, waypoints)

    plot(pipe, waypoints, trajectory, gx, gy, gz, obstacles_points, obstacles_lines, obstacles_polygons)

