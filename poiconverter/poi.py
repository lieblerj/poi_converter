"""
POI

holds point of interest

"""
class Poi:
    def __init__(self, node_id, name, lat, lon):
        self.name = name
        self.node_id = node_id
        self.lat = lat
        self.lon = lon
        self.tags = dict()

    def set_type(self,type):
        self.type = type
        if len(self.name) < 1:
            self.name = self.type[1]

    def add_tag(self, k, v):
        self.tags[k] = v

    def add_tags(self,tags):
        self.tags = tags

    def filter_tags(self, valid_tags):
        new_tags = dict()
        for key in self.tags.keys():
            if key in valid_tags.keys():
                new_tags[key] = self.tags[key]
        self.tags = new_tags

    def translate_name(self, translations):
        if self.name in translations.keys():
                self.name = translations[self.name]

    def __repr__(self):
        return "ID: {}, Name: {}, Lat: {}, Lon: {}, Tags:{}".format(self.node_id, self.name, self.lat, self.lon, self.tags)

