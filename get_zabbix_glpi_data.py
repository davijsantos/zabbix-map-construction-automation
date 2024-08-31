from os import path

def get_zabbix_maps_and_datacom_info(zabbix_db):
    
    zbx_map_and_datacom = {}  # Check ouput at 'output_samples/zbx_map_and_datacom.json'
    ip_x_se = {}  # Check ouput at 'output_samples/ip_x_se.json'
    
    with open(path.join('queries', 'zbx_getMapsAndDatacom.sql'), 'r') as q:
        result = zabbix_db.query(q.read())
    
    
    for r in result:

        backhaul_ipv4 = r["BACKHAUL_IPV4"]
        hxap_ipv4 = r["HXAP_IPV4"]

        # 'output_samples/ip_x_se.json'
        ip_x_se[backhaul_ipv4[:backhaul_ipv4.rfind('.') + 1]] = r["HOST"]  # Convert 10.93.1.1 to 10.93.1.
        ip_x_se[hxap_ipv4[:hxap_ipv4.rfind('.') + 1]] = r["HOST"]  # Convert 10.94.1.1 to 10.94.1.

        # 'output_samples/zbx_map_and_datacom.json'
        zbx_map_and_datacom[r["HOST"]] = {
            "map": {
                "map_name": r["MAP_NAME"],
                "sysmapid": r["SYSMAPID"],
            },
            "datacom": {
                "zabbix": {
                    "hostid": r["DATACOM_HOSTID"],
                    "ping_trigger_id": r["DATACOM_PING_TRIGGER_ID"],
                    "backhaul_ipv4": r["BACKHAUL_IPV4"],
                    "hxap_ipv4": r["HXAP_IPV4"]
                }
            }
        }
    
    return [zbx_map_and_datacom, ip_x_se]

def get_circuits_on_glpi(glpi_db):
    
    with open(path.join('queries', 'glpi_getDatacom.sql'), 'r') as q:
        circuits_on_glpi = glpi_db.query(q.read())
    
    # Check ouput at 'output_samples/circuits_on_glpi.json'
    return circuits_on_glpi

def get_ge_radios(glpi_db, zabbix_db):
    output = {}

    with open(path.join('queries', 'glpi_getGeRadio.sql'), 'r') as q:
        result = glpi_db.query(q.read())
    
    
    for r in result:
        output[r["PERIPHERAL"]] = { "glpi": r }

    with open(path.join('queries', 'zbx_getGeRadio.sql'), 'r') as q:
        result = zabbix_db.query(q.read())
    
    
    for r in result:
        try:
            output[r["NAME"]]["zabbix"] = r
        except:
            continue

    return output

def get_hxap(glpi_db, zabbix_db):
    output = {}

    with open(path.join('queries', 'glpi_getHXAP.sql'), 'r') as q:
        result = glpi_db.query(q.read())
    
    
    for r in result:
        output[r["PERIPHERAL"]] = { "glpi": r }
        

    with open(path.join('queries', 'zbx_getHXAP.sql'), 'r') as q:
        result = zabbix_db.query(q.read())
    
    
    for r in result:
        try:
            output[r["NAME"]]["zabbix"] = r
        except:
            continue

    return output

def get_data(glpi_db, zabbix_db):
    [zbx_info, ip_x_se] = get_zabbix_maps_and_datacom_info(zabbix_db)
    
    output = zbx_info
    
    glpi_info = get_circuits_on_glpi(glpi_db)
    
    for row in glpi_info:
        try:
            output[row["peripheral"]]["datacom"]["glpi"] = row
        except:
            continue
        
    
    ge_radios = get_ge_radios(glpi_db, zabbix_db)
    
    
    for k, v in ge_radios.items():

        if "glpi" in v: 
            sigla_se =  v["glpi"]["SIGLASE"]
        elif "zabbix" in v:
            ipv4 = v["zabbix"]["IPV4"]
            ipv4 = ipv4[:ipv4.rfind('.') + 1]  # Convert 10.93.1.1 to 10.93.1.
            
            try:
                sigla_se = ip_x_se[ipv4]
            except KeyError as e:
                continue
        
        try:
            if not "ge" in output[sigla_se]:
                output[sigla_se]["ge"] = {}
        except:
            continue
        

        output[sigla_se]["ge"][k] = v
        # output[sigla_se]["ge"].append({k: v})

    
    hxap = get_hxap(glpi_db, zabbix_db)
    
    for k, v in hxap.items():

        if "glpi" in v: 
            sigla_se =  v["glpi"]["SIGLASE"]
        else:
            ipv4 = v["zabbix"]["IPV4"]
            ipv4 = ipv4[:ipv4.rfind('.') + 1]  # Convert 10.93.1.1 to 10.93.1.

            try:
                sigla_se = ip_x_se[ipv4]
            except KeyError as e:
                continue
        
        try:
            if not "hxap" in output[sigla_se]:
                output[sigla_se]["hxap"] = {}
        except:
            continue
        
        output[sigla_se]["hxap"][k] = v
        # output[sigla_se]["hxap"].append({k: v})
    
    

    
    # for k, v in output.items():
    #     print(k, v)
    
    # return output
    import json
    
    with open('data.json', 'w') as fp:
        json.dump(output, fp)
    
    return True