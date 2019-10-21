"""
Create database and write POIs into file
"""
import spatialite
import os

class Database:
    def __init__(self, init_file):
        self.entries = 0
        self.init_file = init_file

    def open_append(self, file):
        self.db = spatialite.connect(self.file_name)
        self.cursor = self.db.cursor()

    def open_create(self):
        if os.path.isfile(self.file_name):
            os.remove(self.file_name)
        self.db = spatialite.connect(self.file_name)
        self.cursor = self.db.cursor()
        self.initialize_database()

    def open(self, file, mode):
        self.file_name = file
        self.output_mode = mode
        if mode == 'create':
            self.open_create()
        elif mode == 'append':
            self.open_append()
        else:            
            raise ValueError('Wrong mode parameter')

    def close(self):
        self.db.commit()
        self.db.close()

    def initialize_database(self):
        self.cursor = self.db.cursor()
        with open(self.init_file,'r') as f:
            sql_commands = f.readlines()
            sql = 'SELECT InitSpatialMetadata(1)'
            result = self.db.execute(sql).fetchone()
            for command in sql_commands:
                if command.strip(): #skip empty lines
                    result = self.db.execute(command)

    def insert_poi(self, poi):
        sql = "INSERT INTO 'Points' VALUES(?,'P',?, GEOMFROMTEXT('POINT({} {})', 4326));".format(poi.lon, poi.lat)
        params = [poi.node_id, poi.name]
        result = self.cursor.execute(sql, params)
        self.row_id = self.cursor.lastrowid # rowid id is used for all other tables in database

    def insert_root_sub_folder(self, poi_type):
        sql = ("SELECT FoldersRoot.id, FoldersSub.id  FROM FoldersSub,FoldersRoot WHERE FoldersSub.name = ?" 
            "AND FoldersRoot.name = (SELECT RootSubMapping.rootname FROM RootSubMapping"
            " WHERE RootSubMapping.subname = ?);")
        root_sub = self.db.execute(sql, (poi_type[1],poi_type[1])).fetchone()

        sql = "INSERT INTO Points_Root_Sub VALUES({},{},{});".format(self.row_id,root_sub[0],root_sub[1])
        result = self.db.execute(sql)

    def insert_tags(self, tags):
        for key in tags:
            value = tags[key]
            result = self.cursor.execute("INSERT OR IGNORE INTO TagValues (name) VALUES(?);", (value,))
            sql = "INSERT INTO Points_Key_Value (Points_id, TagKeys_id, TagValues_id) VALUES(?, (SELECT id FROM TagKeys WHERE TagKeys.name = ?), (SELECT id FROM TagValues WHERE TagValues.name = ?));"
            result = self.cursor.execute(sql, (self.row_id, key, value))

    def write_poi(self, poi):
        self.insert_poi(poi)
        self.insert_root_sub_folder(poi.type)
        self.insert_tags(poi.tags)
        self.entries += 1

    def read_tags(self):
        sql = "SELECT name, id from TagKeys;"
        result = self.db.execute(sql).fetchall()
        return result

    def read_folders_sub(self):
        sql = "SELECT name, id from FoldersSub;"
        result = self.db.execute(sql).fetchall()
        return result
