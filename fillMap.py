from configparser import ConfigParser
from custom_modules.mysqlInit import ConnectDB
from pyzabbix import ZabbixAPI
from pyzabbix import ZabbixAPIException
from get_zabbix_glpi_data import get_data
from custom_modules.mapdesigner import DrawZabbixMap
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

############################################################################################################
# Reading configuration file                                                                               #
############################################################################################################
config = ConfigParser()
ini_path = '/opt/config.ini'
config.read(ini_path)

# ZABBIX
zabbix_api_url = config['Zabbix']['server_ext_url']
zabbix_api_sessionid = config['Zabbix']['session_id']
zabbix_db_host = config['Zabbix']['db_host']
zabbix_db_user = config['Zabbix']['db_user']
zabbix_db_pass = config['Zabbix']['db_pass']
zabbix_db_name = config['Zabbix']['db_name']

# GLPI
glpi_db_host = config['Glpi']['db_host']
glpi_db_user = config['Glpi']['db_user']
glpi_db_pass = config['Glpi']['db_pass']
glpi_db_name = config['Glpi']['db_name']

config_2 = ConfigParser()
ini_path = 'config.ini'
config_2.read(ini_path)
confdict = { section: dict(config_2.items(section)) for section in config_2.sections() }

############################################################################################################
# Login into zabbix API                                                                                    #
############################################################################################################

try:
    zapi = ZabbixAPI(zabbix_api_url)
    zapi.session.verify = False
    zapi.timeout = 5.1
    zapi.login(api_token=zabbix_api_sessionid)
    zapi.host.get(hostids=10084)   #  hostid 10084 = Zabbix Server
except BaseException as err:
    print(f"Zabbix API login fail: {str(err)}")
    exit()

############################################################################################################
# Connecting to mysql database                                                                             #
############################################################################################################
glpi_db = ConnectDB(glpi_db_host, glpi_db_name, glpi_db_user, glpi_db_pass)
zabbix_db = ConnectDB(zabbix_db_host, zabbix_db_name, zabbix_db_user, zabbix_db_pass, True)

get_data(glpi_db=glpi_db, zabbix_db=zabbix_db)