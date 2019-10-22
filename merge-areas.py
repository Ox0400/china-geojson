#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zhipeng
# @Email: zhipeng.py@gmail.com
# @Date:   2019-10-21 17:55:00
# @Last Modified by:   zhipeng
# @Last Modified time: 2019-10-22 12:26:51

"""[summary]

[description]
"""


# merge geojson areas
import json

from shapely.geometry import Polygon
from shapely.geometry import mapping as polygon2geojson
from shapely.ops import cascaded_union


def merge_polygon(*coordinates):
    pgs = [Polygon(i) for i in coordinates]
    _pg = cascaded_union(pgs)
    return polygon2geojson(_pg)


def merge_areas(source_map, base, *areas_id):
    if not source_map or not base or not areas_id:
        return {}
    areas_id = list(set(areas_id))
    areas_points = find_area(source_map, *([base] + areas_id))
    merged_points = merge_polygon(*areas_points.values()).get("coordinates")[0]
    print(merged_points)
    areas_points[base] *= 0
    areas_points[base].extend(merged_points)
    # source_map["features"][areas_points[base]["index"]]["geometry"]["coordinates"] = [merged_points]
    for _id in areas_id:
        # clean area points. keep area use the base area one point * 4. like: [[0,0], [0,0], [0,0], [0,0]]
        areas_points[_id] *= 0
        areas_points[_id].extend([merged_points[0]] * 4)
        # source_map["features"][areas_points[_id]["index"]]["geometry"]["coordinates"] = []
    return None


def find_area(source_map, *areas_id):
    base_exists = False
    areas_points = {}
    for feature in source_map['features']:
        _properties = feature.get("properties")
        _type = feature.get("type")
        _geometry = feature.get("geometry")
        if _type != "Feature":
            continue
        if _geometry.get("type") != "Polygon":
            continue
        _coordinates = _geometry.get("coordinates", [[]])[0]
        _property_values = [_properties.get("id"), _properties.get("NAME")]
        for i, _id in enumerate(areas_id):
            if _id not in _property_values:
                continue
            if i == 0:
                base_exists = True
            print("found area%s: %s, len: %s" % (("[base]" if base_exists else "[area]"), _id, len(_coordinates)))
            # areas_points[_id] = {"index":i, "points": _coordinates}
            areas_points[_id] = _coordinates
    if not base_exists:
        raise ValueError("not found base area")
    return areas_points


def load_geojson(filename="./json/shandong.json"):
    source_map = {}
    with open(filename)as _fp:
        source_map = json.load(_fp, encoding="utf-8")
    return source_map


def dump_geojson(obj, filename="./json/shandong-merged.json"):
    with open(filename, "w")as _fp:
        _fp.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))


def main(source_file, base, *areas_id):
    target_file = None
    if not source_file:
        raise ValueError("source_file cant be null")
    if not base:
        raise ValueError("base area cant be null")
    if not target_file:
        target_file = source_file + ".merged"
    if not areas_id:
        raise ValueError("areas required")
    source_map = load_geojson(filename=source_file)
    merge_areas(source_map, base, *areas_id)
    print("dump merge geojson map into:%s" % target_file)
    dump_geojson(source_map, filename=target_file)


if __name__ == '__main__':
    main("./json/geo/china/province-city/shandong.geojson", u"济南市", *[u"莱芜市", u"莱芜市", ])
