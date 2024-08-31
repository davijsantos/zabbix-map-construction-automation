from custom_modules.header import CreateHeader
from custom_modules.devices import CreateDevices


class DrawZabbixMap():
    def __init__(self, data: dict):
        # super(DrawZabbixMap, self).__init__(data)

        # Full content of data
        self._data: dict[str,dict] = data
        self.map_id: int = data["map"]["sysmapid"] # map id
        self.selementid_count: int = 0
        self.linkid_count: int = 0
        self.linktriggerid_count: int = 0

        self.selements: list = []
        self.shapes: list = []
        self.links: list = []
        self.lines: list = []

        self.header = CreateHeader(self)
        self.header.create_header()
        self.devices = CreateDevices(self)
        self.devices.create_devices()

        self.result: dict[str, list] = { "selements": self.selements, "shapes": self.shapes, "links": self.links, "width":self.devices.width, "height":self.devices.height }


    def content(self):
        return self.result


    def sum_selementid_count(self):
        self.selementid_count += 1
        return self.selementid_count


    def sum_linkid_count(self):
        self.linkid_count += 1
        return self.linkid_count


    def sum_linktriggerid_count(self):
        self.linktriggerid_count += 1
        return self.linktriggerid_count