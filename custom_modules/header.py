
class CreateHeader:
    def __init__(self, main):
        self.main = main
        self.circuit_host_id = self.main._data["datacom"]["zabbix"]["hostid"]  # Host id of (PTO-SE, PTO-RE, MRO-SE, ect..)
        self.circuit_ping_trigger_id = self.main._data["datacom"]["zabbix"]["ping_trigger_id"]
        if self.main._data["datacom"]["glpi"]["siglase"][-1:] == "S":
            if "SUBESTACAO" in self.main._data["datacom"]["glpi"]["se"]:
                self.map_top_title = self.main._data["datacom"]["glpi"]["se"]
            else:
                self.map_top_title = "SUBESTAÇÃO DE "+self.main._data["datacom"]["glpi"]["se"]
        elif self.main._data["datacom"]["glpi"]["siglase"][-1:] == "R" and "REPETIDORA" not in self.main._data["datacom"]["glpi"]["se"]:
            self.map_top_title = "REPETIDORA DE "+self.main._data["datacom"]["glpi"]["se"]
        else:
            self.map_top_title = self.main._data["datacom"]["glpi"]["se"]
            

    
    def create_header(self):
        self.vlan_circuit_box()
        self.datacom_button()
        self.write_top_title()  # SE Name
        a = self.backbone_cloud_icon()
        b = self.pixel_under_backbone_cloud_icon()
        self.link_backbone_cloud_icon_x_pixel_under_backbone_cloud_icon(a, b)
        c = self.pixel_under_datacom_port_3()
        self.link_pixel_under_backbone_cloud_icon_x_pixel_under_datacom_port_3(b, c)
        d = self.pixel_on_datacom_port_3()
        self.link_pixel_under_datacom_port_3_x_pixel_on_datacom_port_3(c, d)
        self.icons_legend_box()
        self.ok_icon_legend_box()
        self.problem_icon_legend_box()
        self.maintenance_icon_legend_box()
        self.disabled_icon_legend_box()
        self.purple_icon_legend_box()
        self.ping_ok_green_line()
        self.ping_down_red_line()
        self.tip_box()

        return
    
    # VLAN and Circuit box, left wing
    def vlan_circuit_box(self):
    
        # Top bar || Top Squarer (Blue line)
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "2617",
            "iconid_on": "0",
            "label": "",
            "label_location": "-1",
            "x": "20",
            "y": "0",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
        
        # Bottom bar || Bottom Squarer (Blue line)
        self.main.selements.append({

            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "0",
            "iconid_off": "2601",
            "iconid_on": "0",
            "label": "{HOST.NAME}\n\n{HOST.DESCRIPTION}",
            "label_location": "3",
            "x": "20",
            "y": "225",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [{"hostid": self.circuit_host_id}],
            "urls": [],
            "permission": 2
        })

    
    def backbone_cloud_icon(self):
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "5",
            "iconid_on": "0",
            "label": "BACKBONE\r\nCTE",
            "label_location": "-1",
            "x": "332",
            "y": "34",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
        
        return self.main.selementid_count
        
    
    def pixel_under_backbone_cloud_icon(self):
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "2697",
            "iconid_on": "0",
            "label": "",
            "label_location": "-1",
            "x": "378",
            "y": "218",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
        
        return self.main.selementid_count

    
    def link_backbone_cloud_icon_x_pixel_under_backbone_cloud_icon(self, selementid1, selementid2):
        
        linkid = self.main.sum_linkid_count()
        
        self.main.links.append({
            "linkid": linkid,
            "sysmapid": self.main.map_id,
            "selementid1": selementid1,
            "selementid2": selementid2,
            "drawtype": "0",
            "color": "00CC00",
            "label": "",
            "linktriggers": [{
                "linktriggerid": self.main.sum_linktriggerid_count(),
                "linkid": linkid,
                "triggerid": self.circuit_ping_trigger_id,
                "drawtype": "0",
                "color": "DD0000"
            }],
            "permission": 2
        })


    def pixel_under_datacom_port_3(self):
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "2697",
            "iconid_on": "0",
            "label": "",
            "label_location": "-1",
            "x": "689",
            "y": "218",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
        
        return self.main.selementid_count


    def link_pixel_under_backbone_cloud_icon_x_pixel_under_datacom_port_3(self, selementid1, selementid2):
        
        linkid = self.main.sum_linkid_count()
        
        self.main.links.append({
            "linkid": linkid,
            "sysmapid": self.main.map_id,
            "selementid1": selementid1,
            "selementid2": selementid2,
            "drawtype": "0",
            "color": "00CC00",
            "label": "",
            "linktriggers": [{
                "linktriggerid": self.main.sum_linktriggerid_count(),
                "linkid": linkid,
                "triggerid": self.circuit_ping_trigger_id,
                "drawtype": "0",
                "color": "DD0000"
            }],
            "permission": 2
        })
        
        
    def pixel_on_datacom_port_3(self):
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "elementtype": "4",
            "iconid_off": "2697",
            "iconid_on": "0",
            "label": "",
            "label_location": "-1",
            "x": "689",
            "y": "178",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
        
        return self.main.selementid_count


    def link_pixel_under_datacom_port_3_x_pixel_on_datacom_port_3(self, selementid1, selementid2):
        
        linkid = self.main.sum_linkid_count()
        
        self.main.links.append({
            "linkid": linkid,
            "sysmapid": self.main.map_id,
            "selementid1": selementid1,
            "selementid2": selementid2,
            "drawtype": "0",
            "color": "00CC00",
            "label": "",
            "linktriggers": [{
                "linktriggerid": self.main.sum_linktriggerid_count(),
                "linkid": linkid,
                "triggerid": self.circuit_ping_trigger_id,
                "drawtype": "0",
                "color": "DD0000"
            }],
            "permission": 2
        })


    def datacom_button(self):
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "0",
            "iconid_off": "1442",
            "iconid_on": "1446",
            "label": "",
            "label_location": "2",
            "x": "861",
            "y": "134",
            "iconid_disabled": "1434",
            "iconid_maintenance": "1438",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [{"hostid": self.circuit_host_id}],
            "urls": [],
            "permission": 2
        })

    # SUBSTATION NAME AT TOP OF THE MAP
    def write_top_title(self):
        if self.main.map_id in ['104','108']:
            self.main.shapes.append({
                # "sysmap_shapeid": self.sum_sysmap_shapeid_count(),
                "type": "0",
                "x": "433",
                "y": "0",
                "width": "496",
                "height": "40",
                "text": self.map_top_title,
                "font": "9",
                "font_size": "32",
                "font_color": "D2D2D2",
                "text_halign": "0",
                "text_valign": "2",
                "border_type": "0",
                "border_width": "2",
                "border_color": "000000",
                "background_color": "",
                "zindex": "0"
            })
        else:
            self.main.shapes.append({
                # "sysmap_shapeid": self.sum_sysmap_shapeid_count(),
                "type": "0",
                "x": "433",
                "y": "0",
                "width": "496",
                "height": "80",
                "text": self.map_top_title,
                "font": "9",
                "font_size": "32",
                "font_color": "D2D2D2",
                "text_halign": "0",
                "text_valign": "2",
                "border_type": "0",
                "border_width": "2",
                "border_color": "000000",
                "background_color": "",
                "zindex": "0"
            })
    
    
    def icons_legend_box(self):
        self.main.shapes.append({
            "type": "0",
            "x": "1075",
            "y": "10",
            "width": "275",
            "height": "210",
            "text": "",
            "font": "9",
            "font_size": "11",
            "font_color": "FFA726",
            "text_halign": "0",
            "text_valign": "0",
            "border_type": "1",
            "border_width": "2",
            "border_color": "FFA726",
            "background_color": "",
            "zindex": "1"
        })
    
    
    def ok_icon_legend_box(self):
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "3076",
            "iconid_on": "0",
            "label": "OK",
            "label_location": "2",
            "x": "1103",
            "y": "18",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
    
        
    def problem_icon_legend_box(self):
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "459",
            "iconid_on": "0",
            "label": "PROBLEM",
            "label_location": "2",
            "x": "1103",
            "y": "58",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
    
        
    def maintenance_icon_legend_box(self):
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "3074",
            "iconid_on": "0",
            "label": "MAINTENANCE",
            "label_location": "2",
            "x": "1103",
            "y": "98",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
        
        
    def disabled_icon_legend_box(self):
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "3075",
            "iconid_on": "0",
            "label": "DISABLED",
            "label_location": "2",
            "x": "1103",
            "y": "138",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
        
        
    def purple_icon_legend_box(self):
            self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "3084",
            "iconid_on": "0",
            "label": "INSTALLED, BUT\r\nPREVIOUS HOST\r\nNOT INSTALLED",
            "label_location": "2",
            "x": "1103",
            "y": "178",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
    
    
    def ping_ok_green_line(self):
        # Left pixel
        selementid1 = self.main.sum_selementid_count()
        self.main.selements.append({
            "selementid": selementid1,
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "2697",
            "iconid_on": "0",
            "label": "",
            "label_location": "2",
            "x": "1233",
            "y": "32",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
        # Right pixel
        selementid2 = self.main.sum_selementid_count()
        self.main.selements.append({
            "selementid": selementid2,
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "2697",
            "iconid_on": "0",
            "label": "PING OK",
            "label_location": "2",
            "x": "1273",
            "y": "32",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
        
        # link / green line
        linkid = self.main.sum_linkid_count()
        
        self.main.links.append({
            "linkid": linkid,
            "sysmapid": self.main.map_id,
            "selementid1": selementid1,
            "selementid2": selementid2,
            "drawtype": "0",
            "color": "00CC00",
            "label": "",
            "linktriggers": [],
            "permission": 2
        })

    def ping_down_red_line(self):
        # Left pixel
        selementid1 = self.main.sum_selementid_count()
        self.main.selements.append({
            "selementid": selementid1,
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "2697",
            "iconid_on": "0",
            "label": "",
            "label_location": "2",
            "x": "1233",
            "y": "72",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
        # Right pixel
        selementid2 = self.main.sum_selementid_count()
        self.main.selements.append({
            "selementid": selementid2,
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "2697",
            "iconid_on": "0",
            "label": "PING DOWN",
            "label_location": "2",
            "x": "1273",
            "y": "72",
            "iconid_disabled": "0",
            "iconid_maintenance": "0",
            "elementsubtype": "0",
            "areatype": "0",
            "width": "200",
            "height": "200",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [],
            "urls": [],
            "permission": 2
        })
        
        # link / green line
        linkid = self.main.sum_linkid_count()
        
        self.main.links.append({
            "linkid": linkid,
            "sysmapid": self.main.map_id,
            "selementid1": selementid1,
            "selementid2": selementid2,
            "drawtype": "0",
            "color": "DD0000",
            "label": "",
            "linktriggers": [],
            "permission": 2
        })

    def tip_box(self):
        self.main.shapes.append({
            "type": "0",
            "x": "1075",
            "y": "231",
            "width": "275",
            "height": "77",
            "text": "TIP / 建議使用方法\r\n\r\nUse the shift button + mouse wheel to navigate from side to side\r\n使用 shift 按钮和鼠标滚动来左右导航",
            "font": "9",
            "font_size": "11",
            "font_color": "F0F0F0",
            "text_halign": "0",
            "text_valign": "0",
            "border_type": "1",
            "border_width": "2",
            "border_color": "FFA726",
            "background_color": "",
            "zindex": "1"
        })