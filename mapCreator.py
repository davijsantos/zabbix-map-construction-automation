from configparser import ConfigParser
from custom_modules.mysqlInit import ConnectDB
from pyzabbix import ZabbixAPI
from pyzabbix import ZabbixAPIException
from get_zabbix_glpi_data import get_data
from custom_modules.mapdesigner import DrawZabbixMap
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

############################################################################################################
# Reading configuration file                                                                               #
############################################################################################################
config = ConfigParser()
ini_path = '/opt/config.ini'
config.read(ini_path)

config_2 = ConfigParser()
ini_path = 'config.ini'
config_2.read(ini_path)
confdict = { section: dict(config_2.items(section)) for section in config_2.sections() }

# ZABBIX
zabbix_api_url = config['Zabbix']['server_ext_url']
zabbix_api_sessionid = config['Zabbix']['session_id']

############################################################################################################
# Login into zabbix API                                                                                    #
############################################################################################################

try:
    zapi = ZabbixAPI(zabbix_api_url)
    zapi.session.verify = False
    zapi.timeout = 15
    zapi.login(api_token=zabbix_api_sessionid)
    zapi.host.get(hostids=10084)   #  hostid 10084 = Zabbix Server
except BaseException as err:
    print(f"Zabbix API login fail: {str(err)}")
    exit()

############################################################################################################
# Reading Data Json                                                                                        #
############################################################################################################

f = open('data.json')
data = json.load(f)
f.close()
# selementid_count = 0
# linkid_count = 0
# linktriggerid_count = 0

for d in data.values():
    if d['map']['map_name']:
        if d['datacom']['glpi'] and d['datacom']['glpi']['siglase']:
            if d["map"]["sysmapid"] != "null" and d["datacom"]["glpi"]["siglase"][0:3] != "CAV":
                sysmapid = d["map"]["sysmapid"]
                if sysmapid in ["64","98","99","106","107","200","120"] or sysmapid == None:
                    continue
                d["config"] = confdict
                # print(d["datacom"]["glpi"]["siglase"])
                create_map = DrawZabbixMap(d)
                map_content = create_map.content()

                if d["datacom"]["glpi"]["entidade"] == 12:
                    usergroupMap = [
                        {
                            "usrgrpid":"26", #NOC COPEL
                            "permission":"2" #READ
                        },
                        {
                            "usrgrpid":"30", #COPEL2
                            "permission":"2" #READ
                        },
                        {
                            "usrgrpid":"31", #ELENGE
                            "permission":"2" #READ
                        },
                        {
                            "usrgrpid":"21", #MAP MAKER
                            "permission":"3" #READ-WRITE
                        }
                    ]
                else:
                    usergroupMap = [
                        {
                            "usrgrpid":"26", #NOC COPEL
                            "permission":"2" #READ
                        },
                        {
                            "usrgrpid":"13", #COPEL1
                            "permission":"2" #READ
                        },
                        {
                            "usrgrpid":"21", #MAP MAKER
                            "permission":"3" #READ-WRITE
                        }
                    ]
                content = {
                    "sysmapid": sysmapid,
                    "highlight": "1",
                    "selements": map_content["selements"],
                    "shapes": map_content["shapes"],
                    "links": map_content["links"],
                    "width":map_content["width"] if map_content["width"] else 1920,
                    "height":map_content["height"] if map_content["height"] else 1080,
                    "userGroups":usergroupMap
                }

                mu = zapi.map.update(content)
            elif d["datacom"]["glpi"]["siglase"][0:3] == "CAV":
                continue
                titlemap = ""
                if d["datacom"]["glpi"]["siglase"][-1:] == 'S':
                    titlemap = d["datacom"]["glpi"]["siglase"]+"E ("+d["datacom"]["glpi"]["se"]+" Substation)"
                elif d["datacom"]["glpi"]["siglase"][-1:] == 'R':
                    titlemap = d["datacom"]["glpi"]["siglase"]+"E ("+d["datacom"]["glpi"]["se"]+" Tower)"
                elif d["datacom"]["glpi"]["siglase"][-1:] == 'U' and d["datacom"]["glpi"]["siglase"][0:3] == "PAS":
                    titlemap = d["datacom"]["glpi"]["siglase"]+"S (Usina de "+d["datacom"]["glpi"]["se"]+")"
                else:
                    titlemap = d["datacom"]["glpi"]["siglase"]+"D (Unidade de "+d["datacom"]["glpi"]["se"]+")"

                # d["config"] = confdict
                # # create_map = DrawZabbixMap(d)
                # # map_content = create_map.content()
                
                mu = zapi.map.create({
                    "name": titlemap.capitalize(),
                    "backgroundid": "3094",
                    "label_type": "0",
                    "label_location": "0",
                    "highlight": "1",
                    "expandproblem": "1",
                    "markelements": "0",
                    "show_unack": "0",
                    "grid_size": "40",
                    "grid_show": "1",
                    "grid_align": "1",
                    "label_format": "0",
                    "label_type_host": "2",
                    "label_type_hostgroup": "2",
                    "label_type_trigger": "2",
                    "label_type_map": "2",
                    "label_type_image": "2",
                    "label_string_host": "",
                    "label_string_hostgroup": "",
                    "label_string_trigger": "",
                    "label_string_map": "",
                    "label_string_image": "",
                    "iconmapid": "0",
                    "expand_macros": "1",
                    "severity_min": "2",
                    "userid": "3",
                    "private": "1",
                    "show_suppressed": "0",
                    "userGroups": [
                        {
                            "sysmapusrgrpid": "40",
                            "usrgrpid": "13",
                            "permission": "2"
                        },
                        {
                            "sysmapusrgrpid": "262",
                            "usrgrpid": "21",
                            "permission": "3"
                        },
                        {
                            "sysmapusrgrpid": "202",
                            "usrgrpid": "26",
                            "permission": "2"
                        }
                    ],
                    "width":600,
                    "height":600
                })
exit()
