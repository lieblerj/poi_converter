'''
Importer for openandromaps POI database files

File format:
- sqlite3 database with 3 tables: poi_index, poi_categories and poi_data

- poi_index contains index and boundary box for location as R*tree (sqlite3 needs R*tree support to read table)
- poi_data contains index and tags as string 
- poi_categories contains category tree (not used)

'''

import sqlite3
from poiconverter.poi import Poi
from tqdm import tqdm

class PoiImporter():

    def __init__(self, callback, tag_filter):
        self.callback = callback
        self.tag_filter = tag_filter
        self.node_id = 0

    def handle_node(self, node):
        node_type = self.tag_filter.tag_matched(node.tags)
        if node_type:
            name = node.tags.get('name', '')
            poi = Poi(node.id, name, node.location.lat, node.location.lon)
            for tag in node.tags:
                poi.add_tag(*tag)
            self.callback(poi)

    def handle_result(self, result): #result is tuple of all database columns 
        self.node_id += 1
        lat = (result[0] + result[1]) / 2 # use arithmetic mean to calculate location
        lon = (result[2] + result[3]) / 2
        tags = dict()
        for line in result[4].replace("\r\n", " ").split('\r'):
            matches = line.split('=')
            try:
                tags[matches[0]] = matches[1]
            except IndexError:
                print("Improper tag: {}".format(matches))
        node_type = self.tag_filter.tag_matched(tags)
        if node_type:
            name = tags.get('name', '')
            poi = Poi(self.node_id, name, lat, lon)
            poi.set_type(node_type)
            poi.add_tags(tags)
            self.callback(poi)

    def apply_file(self, file):
        with sqlite3.connect(file) as connection:
            cursor = connection.cursor()
            result = cursor.execute("SELECT DISTINCT poi_index.minLat,poi_index.maxLat,poi_index.minLon,\
                poi_index.maxLon,poi_data.data FROM poi_index, poi_data WHERE poi_data.id = poi_index.id;")

            for row in tqdm(result, unit=' entries', smoothing=0.1):
                self.handle_result(row)
