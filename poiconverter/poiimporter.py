'''
Importer for OpenAndroMaps (v2) and Mapsforge (v3) POI databases.

File format:
- sqlite3 database with 3 tables: poi_index, poi_categories and poi_data

- poi_index contains index and boundary box for location as R*tree (sqlite3 needs R*tree support to read table)
- poi_data contains index and tags as string 
- poi_categories contains category tree (not used)

'''

import sqlite3
from poiconverter.poi import Poi
from tqdm import tqdm
import re


class PoiImporter:

    def __init__(self, callback, tag_filter):
        self.callback = callback
        self.tag_filter = tag_filter

    def osm_get_info(self, osm_data):
        result = re.search(
            r'openstreetmap\.org/(node|way|relation)/(\d+)',
            osm_data
        )

        if result:
            osm_id = int(result.group(2))
            osm_type = {
                "node": "P",
                "way": "W",
                "relation": "R"
            }[result.group(1)]

            return osm_id, osm_type

        return None, None

    def parse_tags(self, data):
        tags = {}

        if not data:
            return tags

        data = data.replace("\r\n", "\n").replace("\r", "\n")

        for line in data.split("\n"):
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            tags[key] = value

        return tags

    def handle_result(self, row, version):

        if version >= 3:
            osm_id = row[0]
            lat = row[1]
            lon = row[2]
            data = row[3]

        else:
            osm_id = None
            lat = (row[0] + row[1]) / 2
            lon = (row[2] + row[3]) / 2
            data = row[4]

        tags = self.parse_tags(data)

        node_type = self.tag_filter.tag_matched(tags)

        if not node_type:
            return

        name = tags.get("name")

        #
        # Old OpenAndroMaps databases stored the original OSM link.
        #
        if version < 3:

            parsed_id, parsed_type = self.osm_get_info(
                tags.get("osm_id_link", "")
            )

            if parsed_id is not None:
                osm_id = parsed_id
            else:
                osm_id = 0

            osm_type = parsed_type or "P"

        #
        # Mapsforge v3 no longer stores node/way/relation.
        #
        else:

            if osm_id is None:
                osm_id = 0

            osm_type = "P"

        poi = Poi(osm_id, name, lat, lon)
        poi.set_osm_type(osm_type)
        poi.set_type(node_type)
        poi.add_tags(tags)

        self.callback(poi)

    def apply_file(self, filename):

        with sqlite3.connect(filename) as connection:

            cursor = connection.cursor()

            #
            # Detect database format.
            #
            tables = {
                row[0]
                for row in cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }

            if "metadata" in tables:

                try:
                    version = int(
                        cursor.execute(
                            "SELECT value FROM metadata WHERE name='version'"
                        ).fetchone()[0]
                    )
                except Exception:
                    version = 2

            else:
                version = 2

            #
            # Mapsforge v3
            #
            if version >= 3:

                sql = """
                SELECT
                    poi_index.id,
                    poi_index.lat,
                    poi_index.lon,
                    poi_data.data
                FROM poi_index
                JOIN poi_data USING(id)
                """

            #
            # OpenAndroMaps v2
            #
            else:

                sql = """
                SELECT
                    poi_index.minLat,
                    poi_index.maxLat,
                    poi_index.minLon,
                    poi_index.maxLon,
                    poi_data.data
                FROM poi_index
                JOIN poi_data USING(id)
                """

            result = cursor.execute(sql)

            for row in tqdm(result, unit=" entries", smoothing=0.1):
                self.handle_result(row, version)

