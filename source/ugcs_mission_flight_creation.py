import pyproj
import yaml
import json
import math
import os
import numpy
import geopandas
import pandas as pd
from qgis.core import QgsVectorLayer


DEFAULT_HEIGHT = 10
DEFAULT_SPEED = 3
DEFAULT_SIDE = 2.5
DEFAULT_WIDTH = 17.5
DEFAULT_EPSG = 3857


def get_mission_template(path_template_mission):
    with open(path_template_mission, 'r') as file:
        mission_yaml = yaml.safe_load(file)
    return mission_yaml


def get_routes(mission):
    return mission["mission"]["routes"]


def get_route_template(path_template_mission):
    return get_routes(get_mission_template(path_template_mission))[0]


def get_segments(route):
    return route["segments"]


def get_segment_template(path_template_mission):
    return get_segments(get_route_template(path_template_mission))[0]


def get_points(segment):
    return segment["polygon"]["points"]


def get_point_template(path_template_mission):
    return get_points(get_segment_template(path_template_mission))[0]


def add_route(mission, route):
    mission["routes"].append(route)
    return mission


def add_segment(route, segment):
    route["segments"].append(segment)
    return route


def add_waypoint(route, first_segment):
    point = first_segment["polygon"]["points"][0]
    return {
        "type" : "Waypoint",
        "actions" : [ ],
        "point" : {
          "latitude" : point["latitude"],
          "longitude" : point["longitude"],
          "altitude" : DEFAULT_HEIGHT,
          "altitudeType" : "AGL"},
        "parameters" : {
          "avoidObstacles" : True,
          "avoidTerrain" : True,
          "speed" : DEFAULT_SPEED + 0.1,
          "wpTurnType" : "STOP_AND_TURN",
          "altitudeType" : "AGL",
          "cornerRadius" : None}
    }


def add_point(segment, point):
    segment["polygon"]["points"].append(point)
    return segment


def create_point(x, y, path_template_mission, z=0):
    point = get_point_template(path_template_mission)
    point["latitude"] = x * math.pi / 180
    point["longitude"] = y * math.pi / 180
    point["altitude"] = z
    return point


def create_segment(points, azimuth, speed, height, side, path_template_mission):
    if speed is None or pd.isnull(speed):
        speed = DEFAULT_SPEED
    if height is None or pd.isnull(height):
        height = DEFAULT_HEIGHT
    if side is None or pd.isnull(side):
        side = DEFAULT_SIDE
    segment = get_segment_template(path_template_mission)
    segment["polygon"]["points"] = points
    segment["parameters"]["directionAngle"] = azimuth
    segment["parameters"]["speed"] = speed
    segment["parameters"]["height"] = height
    segment["parameters"]["sideDistance"] = side
    return segment


def create_route(segments, name, path_template_mission):
    route = get_route_template(path_template_mission)
    route["name"] = name
    route["segments"] = [add_waypoint(route, segments[0])] + segments
    return route


def create_mission(routes, path_template_mission):
    mission = get_mission_template(path_template_mission)
    mission["mission"]["routes"] = routes
    return mission


def create_polygon(point_start, point_end, width, elbow_start, elbow_end, epsg_projection):
    if width is None or pd.isnull(width):
        width = DEFAULT_WIDTH
    x1, y1 = point_start
    x2, y2 = point_end

    # Azimuth in UGCS are calculated using pseudo mercator projection
    xa1, ya1 = reproject(x1, y1, epsg_projection, DEFAULT_EPSG)
    xa2, ya2 = reproject(x2, y2, epsg_projection, DEFAULT_EPSG)
    dx = xa2 - xa1
    dy = ya2 - ya1
    angle = math.atan2(dy, dx)

    azimuth = -angle * 180 / math.pi + 90
    
    cos = width * math.cos(angle) / 2
    sin = width * math.sin(angle) / 2

    x_1 = x1 - sin
    y_1 = y1 + cos
    x_2 = x2 - sin
    y_2 = y2 + cos
    x_3 = x2 + sin
    y_3 = y2 - cos
    x_4 = x1 + sin
    y_4 = y1 - cos

    if elbow_start:
        x_1 += - cos
        y_1 += - sin
        x_4 += - cos
        y_4 += - sin

    if elbow_end:
        x_2 += cos
        y_2 += sin
        x_3 += cos
        y_3 += sin

    lon_1, lat_1 = unproject(x_1, y_1, epsg_projection)
    lon_2, lat_2 = unproject(x_2, y_2, epsg_projection)
    lon_3, lat_3 = unproject(x_3, y_3, epsg_projection)
    lon_4, lat_4 = unproject(x_4, y_4, epsg_projection)

    polygon = [
        [lon_1, lat_1],
        [lon_2, lat_2],
        [lon_3, lat_3],
        [lon_4, lat_4],
        [lon_1, lat_1],
    ]

    return polygon, azimuth


def reproject(x, y, epsg_1, epsg_2):
    xo, yo = pyproj.transform(
        pyproj.Proj(f"EPSG:{epsg_1}"),
        pyproj.Proj(f"EPSG:{epsg_2}"),
        x, y
    )
    return xo, yo


def unproject(x, y, epsg_projection):
    lon, lat = pyproj.transform(
        pyproj.Proj(f"EPSG:{epsg_projection}"),
        pyproj.Proj("EPSG:4326"),
        x, y
    )
    return lon, lat


def export_mission(mission, path_export_mission):
    with open(path_export_mission, 'w') as file:
        txt = json.dumps(mission, indent=2)
        file.write(txt)


def main(path_export_mission, path_gpkg, path_template_mission, width=None, speed=None, height=None, side=None):
    routes, epsg_projection, attributes = gpkg_to_route(path_gpkg)
    mission_routes = []
    for j, segments in enumerate(routes):
        mission_segments = []
        for i in range(len(segments)-1):
            polygon, azimuth = create_polygon(
                segments[i], segments[i+1],
                epsg_projection=epsg_projection,
                elbow_start=i > 0,
                elbow_end=i < len(segments)-2,
                width=attributes.get("width")[j] if "width" in attributes else width,
            )
            mission_segments.append(
                create_segment(
                    [create_point(x, y, path_template_mission) for x, y in polygon],
                    azimuth,
                    attributes.get("speed")[j] if "speed" in attributes else speed,
                    attributes.get("height")[j] if "height" in attributes else height,
                    attributes.get("side")[j] if "side" in attributes else side,
                    path_template_mission
                )
            )
        mission_routes.append(
            create_route(
                mission_segments,
                f"z{attributes.get('fid')[j]}.1",
                path_template_mission
            )
        )
    mission = create_mission(mission_routes, path_template_mission)
    export_mission(mission, path_export_mission)


def gpkg_to_route(path_gpkg):
    data = geopandas.read_file(path_gpkg)
    epsg_from = str(data.geometry.crs)
    unit = data.crs.axis_info[0].unit_name
    if unit not in ["meter", "metre"]:
        raise Exception(f"Only projected EPSG in meters, not {unit} from {epsg_from}")
    routes = []
    for i, line in enumerate(data.geometry):
        print(i, line)
        if line is None:
            continue
        x, y = line.xy
        route = numpy.array([x, y]).T
        routes.append(route)
    attributes = {}
    for col in data.columns.drop('geometry'):
        attributes[col] = list(data[col])
    attributes["fid"] = [feature["fid"] for feature in QgsVectorLayer(path_gpkg).getFeatures()]
    return routes, int(epsg_from[len("EPSG:"):]), attributes


# main(
    # path_export_mission=
        # os.path.join(os.path.dirname(__file__), "mission_ugcs.json")
    # ,
    # path_gpkg=
        # os.path.join(os.path.dirname(__file__), "ugcs_mission_flight_creation.gpkg")
    # ,
    # path_template_mission=os.path.join(os.path.dirname(__file__), "template_ugcs_mission_4.20.json")
# )
