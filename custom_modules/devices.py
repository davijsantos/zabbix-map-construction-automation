from pprint import pprint
import re
from datetime import datetime


class CreateDevices:
    def __init__(self, main):
        self.main = main
        self.config = self.main._data["config"] #carrega valores padrão
        try:
            self.ge = self.main._data["ge"]
        except:
            self.ge = {}
        
        try:
            self.hxap = self.main._data["hxap"]
        except:
            self.hxap = {}
            
        self.p70 = {} #dicionário para filtrar todos os P70 de "self.ge"
        self.datacomHXAP = {} #dicionário para guardar os APs ligados a cada datacom
        self.layers = {} #dicionário para guardar os dados filtrados dos GEs
        self.layer_count = 0 #não está sendo usado
        self.finalX = {} #dicionário que guarda o elemento (GE) criado no mapa, as coordenadas x e y, um flag "previousHasAp" para saber se o GE anterior tem AP (o que afeta a coordenada x referencial para a construção das camadas subsequentes), indicador "layerAp" para registrar a camada corrente do mapa (sendo 0 a camada do P70)
        self.finalPointLayers = {} #dicionário que guarda o elemento do primeiro pixel da camada
        self.width = 0 #Acumulador para indicar a largura total do mapa, considerando o total de elementos no mapa
        self.height = 0 #Acumulador para indicar a altura total do mapa, considerando o total de elementos no mapa
        self.shapeGeNoGwId = False
        self.genogwid = []
        self.fatherHasChildren = {}
        self.finalXLayers = {'1':{'x':58,'HasAp':False,'HasDa':False,'geName':''}}
        self.hasMiddleB2b = False
    
    def checkIfHasChildren(self,geName):
        for k,v in self.layers.items(): #loop chave para inserir filamentos e subfilamentos, o que consequentemente constrói as camadas
            for k2, v2 in v.items():
                if v2['nextdevice'] == geName and v2['idbtwob'] != geName:
                    return True
        return False
    
    def create_devices(self):
        _to_del = []
        for  i, g in self.ge.items():
            for k, v in g.items():
                if '-P7-' in i or g['glpi']["DEVICETYPE"] == "P70":
                    self.p70[k] = g
                    _to_del.append(k)
        for k, v in self.hxap.items():
            if v['glpi']["AP_DEVICE_MODE"] in ["SUBESTACAO", "TORRE"]:
                self.datacomHXAP[k] = v
                _to_del.append(k)
                
        if self.p70:
            self.insert_substation_hxap() #insere os APs de subestação
            self.insert_P70() #insere o P70
            self.insert_layers() #insere os demais elementos
        return
    
    def sum_layer_count(self):
        self.layer_count += 1
        return self.layer_count
    
    def _to_delete_from_dict(self, keys_to_delete):
        for k in keys_to_delete:
            del self.ge[0]       
        return True

    def checkHeightFilament(self,geName,layer):
        height = 0
        layer = int(layer) + 1
        keys = list(self.layers.keys())
        for i,k in enumerate(keys):
            if keys[i]:
                keys[i] = int(keys[i])
        found = False
        while layer <= max(keys):
            for ge,info in self.layers[str(layer)].items():
                if info['nextdevice'] == geName:
                    found = True
                    height += 1
                    if info['idbtwob']:
                        if "-GE-" in info['idbtwob'] and info['idbtwob'] != info['nextdevice']:
                            layer -= 1
                            height -= 1
                            self.hasMiddleB2b = True
                    geName = ge
                    layer += 1
                    break
                
            if not found:
                break
            found = False
        return height

    def getLayerGreaterX(self,layer,height):
        i = int(layer)
        lastLayer = int(height) + int(layer)
        greaterX = {'x':0,'layer':'0'}
        while i <= lastLayer:
            if str(i) in self.finalXLayers.keys():
                if int(self.finalXLayers[str(i)]['x']) > greaterX['x']:
                    greaterX['x'] = int(self.finalXLayers[str(i)]['x'])
                    greaterX['layer'] = str(i)
            else:
                break
            i+=1
        return greaterX

    def preparedataGE(self):
        self.layers = {} #dicionário que traz separados os GEs por camada, considerando o Installation Order.
        for ge, data in self.ge.items():
            if "zabbix" in data.keys():
                try:
                    networkname = data["zabbix"]["NETWORKNAME"] if data["zabbix"]["NETWORKNAME"] else data["glpi"]["NETWORKNAME"]
                except:
                    networkname = data["glpi"]["NETWORKNAME"]
                
                try:
                    devicemode = data["zabbix"]["DEVICEMODE"] if data["zabbix"]["DEVICEMODE"] else data["glpi"]["DEVICEMODE"]
                except:
                    devicemode = data["glpi"]["DEVICEMODE"]
                
                try:
                    nicid = data["zabbix"]["NIC_ID"] if data["zabbix"]["NIC_ID"] else data["glpi"]["NIC_ID"]
                except:
                    nicid = data["glpi"]["NIC_ID"]
                
                try:
                    gwid = data["zabbix"]["GATEWAY_ID"] if data["zabbix"]["GATEWAY_ID"] else data["glpi"]["GATEWAY_ID"]
                except:
                    gwid = data["glpi"]["GATEWAY_ID"]
                    
                entidade = data['glpi']['entidade']
                hostid = data['zabbix']['HOSTID']
                description = data['zabbix']['DESCRIPTION']
            else:
                entidade = data['glpi']['entidade']
                networkname = data["glpi"]["NETWORKNAME"]
                devicemode = data["glpi"]["DEVICEMODE"]
                hostid = ""
                nicid = data["glpi"]["NIC_ID"]
                gwid = data["glpi"]["GATEWAY_ID"]
                description = ""
            try:
                self.layers[data['glpi']['INSTALLATIONORDER']][data['glpi']['PERIPHERAL']] = {
                    'idap':data['glpi']['IDAP'],
                    'idda':data['glpi']['IDDA'],
                    'networkname':networkname,
                    'devicemode':devicemode,
                    'nextdevice':data['glpi']['NEXTDEVICE'],
                    'hostid':hostid,
                    'nicid':nicid,
                    'gwid':gwid,
                    'description':description,
                    'idbtwob':data['glpi']['IDBTWOB'],
                    'element':None,
                    'link':None,
                    'drawn':False,
                    'x':0,
                    'y':0,
                    'linkap':None,
                    'linkda':None,
                    'entidade':entidade,
                    'status_ticket':data['glpi']['status_ticket'],
                    'ticket_id':data['glpi']['ticket_id'],
                    'tipo_de_pendencia':data['glpi']['tipo_de_pendencia']
                }
            except KeyError:
                self.layers[data['glpi']['INSTALLATIONORDER']] = {
                    data['glpi']['PERIPHERAL']:{
                        'idap':data['glpi']['IDAP'],
                        'idda':data['glpi']['IDDA'],
                        'networkname':networkname,
                        'devicemode':devicemode,
                        'nextdevice':data['glpi']['NEXTDEVICE'],
                        'hostid':hostid,
                        'nicid':nicid,
                        'gwid':gwid,
                        'description':description,
                        'idbtwob':data['glpi']['IDBTWOB'],
                        'element':None,
                        'link':None,
                        'drawn':False,
                        'x':0,
                        'y':0,
                        'linkap':None,
                        'linkda':None,
                        'entidade':entidade,
                        'status_ticket':data['glpi']['status_ticket'],
                        'ticket_id':data['glpi']['ticket_id'],
                        'tipo_de_pendencia':data['glpi']['tipo_de_pendencia']
                    }
                }

    def insert_P70(self):
        if not self.p70:
            return

        for v in self.p70.values():
            _x = "122"
            _y = "325"
            _hostid = v["zabbix"]["HOSTID"] if "zabbix" in v else None
            _host_description = v['zabbix']["DESCRIPTION"] if "zabbix" in v else ""
            _trigger_id = v['zabbix']["PING_TRIGGER_ID"] if "zabbix" in v else None
            _device_mode = v['glpi']["DEVICEMODE"]
            p70Name = v['glpi']["PERIPHERAL"]
            status_ticket = v['glpi']["status_ticket"]
            ticket_id = v['glpi']["ticket_id"]
            tipo_de_pendencia = v['glpi']["tipo_de_pendencia"]
            _selementid1 = self.insert_ge(_x, _y, _hostid, _host_description, _device_mode,p70Name,tipo_de_pendencia,ticket_id,status_ticket)
            _selementid2 = self.insert_pixel("138", "298") #ponto superior ao P70
            self.insert_link(_selementid1, _selementid2, _trigger_id) #link entre ponto superior e o GE
            if p70Name == "MSO-R-P7-001":
                _selementid3 = self.insert_pixel("785", "298") #ponto intermediário que liga o P70 ao datacom
                _selementid4 = self.insert_pixel("785", "175") #ponto intermediário que liga o P70 ao datacom
            else:
                _selementid3 = self.insert_pixel("745", "298") #ponto intermediário que liga o P70 ao datacom
                _selementid4 = self.insert_pixel("745", "175") #ponto intermediário que liga o P70 ao datacom
            self.insert_link(_selementid2, _selementid3, _trigger_id) #link entre pontos intermediários
            self.insert_link(_selementid3, _selementid4, _trigger_id) #link entre pontos intermediários
            break
        self.finalPointLayers['1'] = _selementid2 # ponto inferior ao P70
        self.finalX = {
            "name":p70Name, #guarda nome do P70
            "element":_selementid1, #guarda elemento criado no mapa P70 para futuras construções de links
            "x":138, #guarda a coordenada X do ponto superior ao P70
            "y":298, #guarda a coordenada Y do ponto superior ao P70
            "layerAp":0, #guarda a camada corrente do AP
            "layerDa":0, #guarda a camada corrente do DA
            "previousHasAp":False, #guarda se o GE anterior possui P70 para não afetar a coordenada X referencial
            "previousHasDa":False, #guarda se o GE anterior possui P70 para não afetar a coordenada X referencial
            "filament":0, #guarda se o GE anterior possui P70 para não afetar a coordenada X referencial
            "previousFilament":0, #guarda se o GE anterior possui P70 para não afetar a coordenada X referencial
            "layer":0 #guarda se o GE anterior possui P70 para não afetar a coordenada X referencial
        }
        self.finalXHeader = {
            "name":p70Name, #guarda nome do P70
            "element":_selementid1, #guarda elemento criado no mapa P70 para futuras construções de links
            "x":1600, #guarda a coordenada X do ponto superior ao P70
            "y":40, #guarda a coordenada Y do ponto superior ao P70
            "layerAp":0, #guarda a camada corrente do AP
            "layerDa":0, #guarda a camada corrente do DA
            "previousHasAp":False, #guarda se o GE anterior possui P70 para não afetar a coordenada X referencial
            "previousHasDa":False, #guarda se o GE anterior possui P70 para não afetar a coordenada X referencial
            "filament":0, #guarda se o GE anterior possui P70 para não afetar a coordenada X referencial
            "previousFilament":0, #guarda se o GE anterior possui P70 para não afetar a coordenada X referencial
            "layer":0 #guarda se o GE anterior possui P70 para não afetar a coordenada X referencial
        }

    def insert_substation_hxap(self):
        for i, v in enumerate(self.datacomHXAP.values()):
            if not (self.main.map_id in ['104','108']):
                if v["glpi"]["entidade"] == 1:
                    _x = "900" if i == 0 else "756" # Check if is has 1 or 2 APs. i == 0 is xxx-x-A-001
                    _y = "308"
                else:
                    _x = "756" if i == 0 else "900" # Check if is has 1 or 2 APs. i == 0 is xxx-x-A-001
                    _y = "308"
                try:
                    _hostid = v["zabbix"]["HOSTID"]
                    _host_description = v["zabbix"]["DESCRIPTION"]
                    _trigger_id = v["zabbix"]["PING_TRIGGER_ID"]
                    # _selementid1 = self.insert_hxap(_x, _y, _hostid, _host_description)
                    _selementid1 = self.insert_hxap(_x, _y, _hostid,_host_description)

                    if v["glpi"]["entidade"] == 1:
                        pixel_x = "960" if i == 0 else "785" # Check if is has 1 or 2 APs. i == 0 is xxx-x-A-001
                    else:
                        pixel_x = "785" if i == 0 else "960" # Check if is has 1 or 2 APs. i == 0 is xxx-x-A-001

                    if v["glpi"]["entidade"] == 1:
                        pixel_y = "337" if i == 0 else "175" # Check if is has 1 or 2 APs. i == 0 is xxx-x-A-001
                    else:
                        pixel_y = "175" if i == 0 else "337" # Check if is has 1 or 2 APs. i == 0 is xxx-x-A-001

                    _selementid2 = self.insert_pixel(pixel_x, pixel_y)
                    self.insert_link(_selementid1, _selementid2, _trigger_id)
                    
                    # Code (pixels and links) below is only for xxx-x-A-001
                    if v["glpi"]["entidade"] == 1:
                        if i == 0:
                            
                            _selementid3 = self.insert_pixel("960", "87")
                            self.insert_link(_selementid2, _selementid3, _trigger_id)
                            _selementid4 = self.insert_pixel("745", "87")
                            self.insert_link(_selementid3, _selementid4, _trigger_id)
                            _selementid5 = self.insert_pixel("745", "135")
                            self.insert_link(_selementid4, _selementid5, _trigger_id)
                    else:
                        if i == 1:
                            _selementid3 = self.insert_pixel("960", "87")
                            self.insert_link(_selementid2, _selementid3, _trigger_id)
                            _selementid4 = self.insert_pixel("745", "87")
                            self.insert_link(_selementid3, _selementid4, _trigger_id)
                            _selementid5 = self.insert_pixel("745", "135")
                            self.insert_link(_selementid4, _selementid5, _trigger_id)
                except:
                    pass
            else:
                if i == 0:
                    _x = "938"
                elif i == 1:
                    _x = "758"
                elif i == 2:
                    _x = "578"
                else:
                    _x = "398"
                _y = "370"
                try:
                    _hostid = v["zabbix"]["HOSTID"]
                    _host_description = v["zabbix"]["DESCRIPTION"]
                    _trigger_id = v["zabbix"]["PING_TRIGGER_ID"]
                    _selementid1 = self.insert_hxap(_x, _y, _hostid,_host_description)
                    
                    if i == 0:
                        pixel_x = "1019"
                        pixel_y = "400"
                    elif i == 1:
                        pixel_x = "787"
                        pixel_y = "360"
                    elif i == 2:
                        pixel_x = "608"
                        pixel_y = "340"
                    else:
                        pixel_x = "428"
                        pixel_y = "320"
                    _selementid2 = self.insert_pixel(pixel_x, pixel_y)
                    self.insert_link(_selementid1, _selementid2, _trigger_id)
                    
                    # Code (pixels and links) below is only for xxx-x-A-001
                    if i == 0:
                        _selementid3 = self.insert_pixel("1019", "60")
                        self.insert_link(_selementid2, _selementid3, _trigger_id)
                        _selementid4 = self.insert_pixel("690", "60")
                        self.insert_link(_selementid3, _selementid4, _trigger_id)
                        _selementid5 = self.insert_pixel("690", "135")
                        self.insert_link(_selementid4, _selementid5, _trigger_id)
                    elif i == 1:
                        _selementid3 = self.insert_pixel("998", "360")
                        self.insert_link(_selementid2, _selementid3, _trigger_id)
                        _selementid4 = self.insert_pixel("998", "73")
                        self.insert_link(_selementid3, _selementid4, _trigger_id)
                        _selementid5 = self.insert_pixel("745", "75")
                        self.insert_link(_selementid4, _selementid5, _trigger_id)
                        _selementid6 = self.insert_pixel("745", "135")
                        self.insert_link(_selementid5, _selementid6, _trigger_id)
                    elif i == 2:
                        _selementid3 = self.insert_pixel("977", "340")
                        self.insert_link(_selementid2, _selementid3, _trigger_id)
                        _selementid4 = self.insert_pixel("977", "85")
                        self.insert_link(_selementid3, _selementid4, _trigger_id)
                        _selementid5 = self.insert_pixel("785", "85")
                        self.insert_link(_selementid4, _selementid5, _trigger_id)
                        _selementid6 = self.insert_pixel("785", "135")
                        self.insert_link(_selementid5, _selementid6, _trigger_id)
                    elif i == 3:
                        _selementid3 = self.insert_pixel("785", "320")
                        self.insert_link(_selementid2, _selementid3, _trigger_id)
                        _selementid4 = self.insert_pixel("785", "175")
                        self.insert_link(_selementid3, _selementid4, _trigger_id)
                except:
                    pass

    def insert_layer_elements(self, geName, layer, i, apName = "", b2b = "", daName = "", description = "", devicemode = "",fatherElement = "",tipo_de_pendencia = "-",ticket_id = "-",status_ticket = "-"):
        apAlreadyInserted = False #flag para checar se o AP do GE corrente já foi inserido
        daAlreadyInserted = False #flag para checar se o DA do GE corrente já foi inserido
        daAndApAlreadyInserted = False #flag para checar se o AP e o DA do GE corrente já foi inserido
        aps = self.hxap #instancia o dicionário de APs do mapa corrente
        ges = self.layers #instancia o dicionário de GEs do mapa corrente
        _host_description = description #captura descrição contida no Zabbix
        xPlusPointAp = 165 #estabelece o distanciamento no eixo X padrão para AP
        y = self.finalX['y']+350*(int(layer)) #inicia o y padrão da camada corrente a partir do Y da camada imediatamente anterior
        checkap = False
        checkb2b = False
        checkda = False
        hostidAp = None
        hostidApDesc = ""

        if apName:
            if "-A-" in apName:
                checkap = True
                if apName in aps.keys():
                    if "zabbix" in aps[apName]:
                        hostidAp = aps[apName]['zabbix']['HOSTID']
                        hostidApDesc = aps[apName]['zabbix']['DESCRIPTION']
        if b2b:
            if "-GE-" in b2b:
                checkb2b = True
        if daName:
            if daName == None or daName == "-":
                checkda = False
            else:
                checkda = True #checa se o GE possui um valor de DA válido
        if checkb2b:
            checkIfHasChildren = self.checkIfHasChildren(geName)
            if  not checkIfHasChildren:
                heightFilament = int(self.checkHeightFilament(b2b,layer))
            else:
                heightFilamentB2b = int(self.checkHeightFilament(b2b,layer))
                heightFilamentGe = int(self.checkHeightFilament(geName,layer))
                heightFilament = heightFilamentB2b if heightFilamentB2b > heightFilamentGe else heightFilamentGe
        else:
            heightFilament = int(self.checkHeightFilament(geName,layer))
        
        
        if str(layer) in self.finalXLayers.keys():
            if int(self.finalX['filament']) != int(self.finalX['previousFilament']):
                if not checkb2b:
                    checkIfHasChildren = self.checkIfHasChildren(geName)
                    if not checkIfHasChildren:
                        self.finalX['x'] = self.finalXLayers[layer]['x']
                        # if self.finalXLayers[layer]['HasAp']:
                        #     self.finalX['x'] = int(self.finalX['x']) + 165
                    else:
                        greaterX = self.getLayerGreaterX(layer,heightFilament) #greaterX = {'x':0,"layer":"0"}
                        if str(greaterX['layer']) != str(layer):
                            self.finalX['x'] = greaterX['x'] - 24*(int(greaterX['layer']) - int(layer))
                        else:
                            self.finalX['x'] = greaterX['x']
                else:
                    checkIfHasChildren = self.checkIfHasChildren(geName)
                    if not checkIfHasChildren:
                        checkIfHasChildren = self.checkIfHasChildren(b2b)
                        if not checkIfHasChildren:
                            self.finalX['x'] = self.finalXLayers[layer]['x']
                            # if self.finalXLayers[layer]['HasAp'] or self.finalXLayers[layer]['HasAp']:
                            #     self.finalX['x'] = int(self.finalX['x']) + 165
                        else:
                            greaterX = self.getLayerGreaterX(layer,heightFilament) #greaterX = {'x':0,"layer":"0"}
                            if str(greaterX['layer']) != str(layer):
                                self.finalX['x'] = greaterX['x'] - (xPlusPointAp + 24*(int(greaterX['layer']) - int(layer)))
                            else:
                                self.finalX['x'] = greaterX['x']
                    else:
                        greaterX = self.getLayerGreaterX(layer,heightFilament) #greaterX = {'x':0,"layer":"0"}
                        if str(greaterX['layer']) != str(layer):
                            self.finalX['x'] = greaterX['x'] - 165*(int(greaterX['layer']) - int(layer))
                        else:
                            self.finalX['x'] = greaterX['x']
                    self.finalX['x'] = int(self.finalX['x']) + xPlusPointAp
        
        if layer in self.finalXLayers.keys():
            if checkb2b:
                if self.finalXLayers[layer]['HasAp'] and int(self.finalX['filament']) != int(self.finalX['previousFilament']):
                    self.finalX['x'] = int(int(self.finalX['x']) - xPlusPointAp)
                elif self.finalXLayers[layer]['HasDa'] and int(self.finalX['filament']) != int(self.finalX['previousFilament']):
                    # self.finalX['x'] = int(int(self.finalX['x']))
                    if  ((not self.finalX['previousHasAp']) and (self.finalX['layerAp'] != str(layer))) or (not self.finalX['previousHasDa']) and (self.finalX['layerDa'] != str(layer)):
                        self.finalX['x'] = int(int(self.finalX['x']) - xPlusPointAp)

        if i == 0: #flag i indica se se trata do primeiro GE da camada
            _selementidx = self.insert_pixel(str(int(self.finalX['x'])) , str(y)) #insere o primeiro pixel antes do pixel do primeiro filho da cadeia de filhos
            if fatherElement: #verifica se há um elemento pai informado
                self.insert_link(fatherElement, _selementidx,False) #insere link entre o elemento pai e o primeiro pixel (posicionado abaixo do elemento pai)
            try: #adiciona na camada corrente qual é o último pixel inserido
                self.finalPointLayers[layer] = _selementidx
            except KeyError:
                self.finalPointLayers = {
                    layer:_selementidx
                }
            xPlusPoint = 42 #valor base de distância do primeiro pixel da camada para o outro
        else:
            xPlusPoint = 165 #valor base de distância de qualquer outro pixel da camada para o outro

        if str(devicemode) != 'access-point': #verifica se o GE corrente é o access point, o que define o segundo de um B2B
            
            if checkb2b and checkap and checkda: #se é um B2B com AP e DA, a posição do AP e do DA será à esquerda.
                _selementid4 = self.insert_da(str(int(int(self.finalX['x']) + xPlusPoint*(5/4)-19) - 5), str(int(y) + 27 + 7),daName) #(self, x, y, hostname, ip = "", hostid = "")
                
                _selementid2 = self.insert_hxap(str(int(int(self.finalX['x']) + xPlusPoint*(5/4)-19)), str(int(y) + 27 + 91), hostidAp,hostidApDesc,"HXAP_SMALLICONS",apName) #insere o HXAP antes do GE no mapa
                self.finalX['previousHasAp'] = True
                self.finalX['previousHasDa'] = True
                self.finalX['layerAp'] = layer #registra a camada do AP no dicionário do X de referência
                self.finalX['layerDa'] = layer #registra a camada do DA no dicionário do X de referência
                if i == 0:
                    xPlusPoint = 165
                    self.finalX['x'] = str(int(int(self.finalX['x']) + xPlusPoint*(1/5))) #guarda o último valor de coordenada do eixo X
                else:
                    self.finalX['x'] = str(int(int(self.finalX['x']) + xPlusPoint*(5/4)-19)) #guarda o último valor de coordenada do eixo X
                daAlreadyInserted = True #marca que o AP da unidade foi inserido
                apAlreadyInserted = True #marca que o AP da unidade foi inserido
            
            if checkb2b and checkap: #se é um B2B com AP, a posição do AP será à esquerda.
                if not("zabbix" in aps[apName]):
                    hostidAp = None
                    hostidApDesc = ""
                else:
                    hostidAp = aps[apName]['zabbix']['HOSTID']
                    hostidApDesc = aps[apName]['zabbix']['DESCRIPTION']
                _selementid2 = self.insert_hxap(str(int(int(self.finalX['x']) + xPlusPoint*(5/4)-19)), str(int(y) + 27 + 11), hostidAp,hostidApDesc,"HXAP_SMALLICONS",apName) #insere o HXAP antes do GE no mapa
                self.finalX['previousHasAp'] = True
                self.finalX['layerAp'] = layer #registra a camada do AP no dicionário do X de referência
                if i == 0:
                    xPlusPoint = 165
                    self.finalX['x'] = str(int(int(self.finalX['x']) + xPlusPoint*(1/5))) #guarda o último valor de coordenada do eixo X
                else:
                    self.finalX['x'] = str(int(int(self.finalX['x']) + xPlusPoint*(5/4)-19)) #guarda o último valor de coordenada do eixo X
                apAlreadyInserted = True #marca que o AP da unidade foi inserido

            if checkb2b and checkda: #se é um B2B com DA, a posição do DA será à esquerda.                
                _selementid4 = self.insert_da(str(int(int(self.finalX['x']) + xPlusPoint*(5/4)-19) - 5), str(int(y) + 27 + 7),daName) #(self, x, y, hostname, ip = "", hostid = "")
                self.finalX['previousHasDa'] = True
                self.finalX['layerDa'] = layer #registra a camada do DA no dicionário do X de referência
                if i == 0:
                    xPlusPoint = 165
                    self.finalX['x'] = str(int(int(self.finalX['x']) + xPlusPoint*(1/5))) #guarda o último valor de coordenada do eixo X
                else:
                    self.finalX['x'] = str(int(int(self.finalX['x']) + xPlusPoint*(5/4)-19)) #guarda o último valor de coordenada do eixo X
                daAlreadyInserted = True #marca que o AP da unidade foi inserido
            
            if checkap and checkda: #se é um GE com AP e com DA, a posição do DA será à esquerda.
                _selementid4 = self.insert_da(str(int(int(self.finalX['x']) + xPlusPoint)), str(int(y) + 27 + 7),daName) #(self, x, y, hostname, ip = "", hostid = "")
                self.finalX['previousHasAp'] = True
                self.finalX['previousHasDa'] = True
                daAndApAlreadyInserted = True
                self.finalX['layerDa'] = layer #registra a camada do DA no dicionário do X de referência
                self.finalX['layerAp'] = layer #registra a camada do AP no dicionário do X de referência
                if i == 0:
                    xPlusPoint = 165
                else:
                    self.finalX['x'] = str(int(int(self.finalX['x']) + xPlusPoint*(3/4))) #guarda o último valor de coordenada do eixo X
                
                try:
                    if not("zabbix" in aps[apName]):
                        hostidAp = None
                        hostidApDesc = ""
                    else:
                        hostidAp = aps[apName]['zabbix']['HOSTID']
                        hostidApDesc = aps[apName]['zabbix']['DESCRIPTION']
                except:
                    pass
                
                _selementid2 = self.insert_hxap(str(int(int(self.finalX['x']) + xPlusPoint*(3/4-1/20)+(xPlusPoint))), str(int(y) + 38), hostidAp,hostidApDesc,"HXAP_SMALLICONS",apName) #insere o HXAP antes do GE no mapa
                daAlreadyInserted = True #marca que o DA da unidade foi inserido
                apAlreadyInserted = True #marca que o AP da unidade foi inserido

            _selementid0 = self.insert_pixel(str(int(self.finalX['x']) + xPlusPoint) , str(y)) #insere o pixel imediatamente superior ao AP
            self.insert_link(self.finalPointLayers[layer], _selementid0,False) #faz o link que entre o pixel anterior e o pixel do GE
            try: #guarda como último pixel inserido na camada corrente o pixel do GE
                self.finalPointLayers[layer] = _selementid0
            except KeyError:
                self.finalPointLayers = {
                    layer:_selementid0
                }
            _selementid1 = self.insert_ge(str(int(self.finalX['x']) + xPlusPoint - 16), str(int(y) + 27), ges[layer][geName]['hostid'], _host_description, devicemode,geName,tipo_de_pendencia,ticket_id,status_ticket) #insere o GE da unidade
            self.insert_link(_selementid1, _selementid0,False) #insere o link entre o pixel do GE e o GE
            if apAlreadyInserted: #verifica se o AP da unidade já foi inserido
                self.insert_link(_selementid2, _selementid1,False) #insere link entre o AP e o GE
            if daAlreadyInserted: #verifica se o DA da unidade já foi inserido
                self.insert_link(_selementid4, _selementid1,False) #insere link entre o AP e o GE
            
            ges[layer][geName]['x'] = int(self.finalX['x']) + xPlusPoint - 16 #guarda valor X do GE corrente
            ges[layer][geName]['y'] = int(y) + 27 #guarda valor Y do GE corrente
            ges[layer][geName]['element'] = _selementid1 #guarda selementid do GE corrente
            ges[layer][geName]['drawn'] = True #flag para indicar que o GE já foi desenhado no mapa

            self.finalX['element'] = _selementid0 #guarda selementid do pixel do GE
            if checkap and not apAlreadyInserted: #checa se o GE possui AP e ele ainda não foi inserido; essa verificação dará falsa no caso de um B2B com AP
                try:
                    _selementid2 = self.insert_hxap(str(int(ges[layer][geName]['x'] + xPlusPointAp*(3/4))), str(int(ges[layer][geName]['y']) + 11), hostidAp,hostidApDesc,"HXAP_SMALLICONS",apName) #insere o HXAP no mapa
                    ges[layer][geName]['linkap'] = self.insert_link(_selementid1, _selementid2,False) #cria o link entre o HXAP e o GE
                    self.finalX['layerAp'] = layer #registra a camada do AP no dicionário do X de referência
                    self.finalX['previousHasAp'] = True #registra que o GE anterior tem um AP
                except KeyError:
                    pass
            elif not daAndApAlreadyInserted:
                self.finalX['previousHasAp'] = False
            
            if checkda and not daAlreadyInserted: #checa se o GE possui DA e ele ainda não foi inserido; essa verificação dará falsa no caso de um B2B com DA
                try:
                    _selementid4 = self.insert_da(str(int(ges[layer][geName]['x'] + xPlusPointAp*(3/4))), str(int(ges[layer][geName]['y']) + 7),daName) #(self, x, y, hostname, ip = "", hostid = "")
                    ges[layer][geName]['linkda'] = self.insert_link(_selementid1, _selementid4,False) #cria o link entre o HXAP e o GE
                    self.finalX['layerDa'] = layer #registra a camada do DA no dicionário do X de referência
                    self.finalX['previousHasDa'] = True #registra que o GE pai tem um AP
                except KeyError:
                    pass
            elif not daAndApAlreadyInserted:
                self.finalX['previousHasDa'] = False
            
            if checkb2b: #Checa se o GE corrente é B2B, não access-point
                try:
                    xPlusPoint = 165
                    self.finalX['x'] = str(int(ges[layer][geName]['x']) + 16)
                    self.insert_filament(geName,ges[layer][geName]['element'])
                    self.finalX['previousFilament'] = self.finalX['filament']
                    self.finalX['filament'] += 1
                    if self.finalX['previousHasAp'] and int(self.finalX['filament']) != int(self.finalX['previousFilament']): #incrementa o valor do último elemento no eixo X caso o último equipamento inserido da camada anterior tenha AP.
                        self.finalX['x'] = int(int(self.finalX['x']) + xPlusPointAp)
                    elif self.finalX['previousHasDa'] and int(self.finalX['filament']) != int(self.finalX['previousFilament']): #incrementa o valor do último elemento no eixo X caso o último equipamento inserido da camada anterior tenha AP.
                        self.finalX['x'] = int(int(self.finalX['x']) + xPlusPointAp)
                    _selementid3 = self.insert_ge(str(int(self.finalX['x']) + xPlusPoint), str(ges[layer][geName]['y']), ges[layer][b2b]['hostid'], ges[layer][b2b]['description'], ges[layer][b2b]['devicemode'],b2b,tipo_de_pendencia,ticket_id,status_ticket)#insere o GE access point do B2B corrente
                    ges[layer][geName]['x'] = str(int(ges[layer][geName]['x']) + xPlusPoint)
                    ges[layer][ges[layer][geName]['idbtwob']]['link'] = self.insert_link(_selementid1, _selementid3,False,"B2B") #insere link entre os GEs do B2B com o label B2B
                    ges[layer][geName]['link'] = ges[layer][b2b]['link'] #registra o id do link
                    ges[layer][b2b]['x'] = int(self.finalX['x']) + xPlusPoint #guarda valor X do GE corrente
                    ges[layer][b2b]['y'] = int(ges[layer][geName]['y']) #guarda valor Y do GE corrente
                    ges[layer][b2b]['element'] = _selementid3 #guarda o selementid do access point do B2B
                    ges[layer][b2b]['drawn'] = True #registra que o access point do B2B
                    self.finalX['x'] = int(self.finalX['x']) + xPlusPoint + 16 #guarda valor X do GE corrente 

                except Exception as e:
                    # print(e)
                    pass
            else:
                self.finalX['x'] = str(int(self.finalX['x']) + xPlusPoint) #guarda o último valor de coordenada do eixo X
        
        try:
            if self.finalX['previousHasAp'] or self.finalX['previousHasDa']:
                self.finalXLayers[layer]["x"] = int(self.finalX['x']) + xPlusPointAp
            else:
                self.finalXLayers[layer]["x"] = int(self.finalX['x'])
                
            self.finalXLayers[layer]["HasAp"] = self.finalX['previousHasAp']
            self.finalXLayers[layer]["HasDa"] = self.finalX['previousHasDa']
            if checkb2b:
                self.finalXLayers[layer]["geName"] = b2b
            else:
                self.finalXLayers[layer]["geName"] = geName
        except KeyError:
            fx = int(self.finalX['x'])
            if self.finalX['previousHasAp'] or self.finalX['previousHasDa']:
                fx = int(fx) + xPlusPointAp
            else:
                fx = int(fx)
            if checkb2b:
                self.finalXLayers[layer] = {
                    "x":fx,
                    "HasAp":self.finalX['previousHasAp'],
                    "HasDa":self.finalX['previousHasDa'],
                    "geName":b2b
                }
            else:
                self.finalXLayers[layer] = {
                    "x":fx,
                    "HasAp":self.finalX['previousHasAp'],
                    "HasDa":self.finalX['previousHasDa'],
                    "geName":geName
                }
        
        self.finalX['layer'] = layer
        self.finalX['name'] = geName

    def insert_layers(self):
        self.preparedataGE() #alimenta o dicionário self.layers com os GEs separados por camada
        self.insert_filament(self.finalX['name'],self.finalX['element']) #método que começa insere os elementos a partir do P70.
        x = list(self.finalPointLayers.keys()) 
        self.height = self.finalX['y']+500+350*int(x[len(x)-1]) #calcula a altura a partir do último valor Y preenchido do último elemento com uma sobra de 400px a partir do último pixel superior ao seu GE
        greaterX = self.getLayerGreaterX(1,len(self.finalXLayers)) #retorna a coordenada X da maior camada
        self.width = int(greaterX['x']) + 300 #calcula a largura a partir do último valor X preenchido do último elemento com uma sobra de 400px a partir do último pixel superior ao seu GE
        if self.width < 1320:
            self.width = 1500
        self.insert_shape("40",str(int(self.height)-50),"450","33","12","FFFFFF","0","2",'000000',"Last updated on "+datetime.now().strftime('%d/%m/%Y %H:%M:%S')+" by NOC Hexing Brasil")
        if self.shapeGeNoGwId:
            self.insert_shape("1400","10",str(int(self.finalXHeader['x'])-1320),"298","12","FFFFFF","1","2",'FFA726','GEs with GWID equal to zero or with no "Next Device Communication" on GLPI',0,2)
            if self.width < self.finalXHeader['x']:
                self.width = self.finalXHeader['x'] + 300

    def insert_filament(self,father,fatherElement = ""):
        firstGeInserted = 0 #flag para identificar que é o primeiro GE de uma camada, informação necessária para estabelecer o distanciamento do primeiro pixel, que é um pouco menor que a distância entre os subsequentes
        ges = self.layers #instancia o dicionário que filtra GEs no data.json
        for k,v in ges.items(): #loop chave para inserir filamentos e subfilamentos, o que consequentemente constrói as camadas
            for k2, v2 in v.items():
                nicIdValido = False #insere GEs que não possuem next device communication declarado no topo do mapa, ao lado direito da legenda.
                checkValidFatherNameGe = False
                checkValidFatherNameP7 = False
                
                if v2['nextdevice']:
                    if "-GE-" in v2['nextdevice']:
                        checkValidFatherNameGe = True
                    if "-P7-" in v2['nextdevice']:
                        checkValidFatherNameP7 = True
                
                if (not (checkValidFatherNameP7 or checkValidFatherNameGe) and not ges[k][k2]['drawn'] and "-P7-" not in k2) or (father in self.genogwid and father == v2['nextdevice']):
                        
                    if not self.shapeGeNoGwId:
                        self.shapeGeNoGwId = True
                    if (father in self.genogwid and father == v2['nextdevice']):
                        ges[k][k2]['description'] = ges[k][k2]['description'] + "\nDevice has a father with no GWID"
                        
                    selementnoid = self.insert_ge(self.finalXHeader['x'], self.finalXHeader['y'], ges[k][k2]['hostid'], ges[k][k2]['description'], ges[k][k2]['devicemode'],k2,ges[k][k2]['tipo_de_pendencia'],ges[k][k2]['ticket_id'],ges[k][k2]['status_ticket'])
                    self.genogwid.append(k2)
                    self.finalXHeader['x'] += 160
                    ges[k][k2]['drawn'] = True
                    self.insert_filament(k2,selementnoid)
                    
                elif '-P7-' not in k2:
                    try:
                        if v2['nextdevice'] == father and v2['idbtwob'] != father:
                            nicIdValido = True
                        
                        if nicIdValido:
                            if father in self.fatherHasChildren.keys():
                                self.fatherHasChildren[father] += 1
                            else:
                                self.fatherHasChildren[father] = 1
                            
                            self.finalX['previousFilament'] = self.finalX['filament']                                
                            
                            if father in self.fatherHasChildren.keys():
                                if self.fatherHasChildren[father] > 1:
                                    self.finalX['filament'] += 1
                            
                            if k: #k = installation order
                                self.insert_layer_elements(k2,k,firstGeInserted,v2['idap'],v2['idbtwob'],v2['idda'],v2['description'],v2['devicemode'],fatherElement,ges[k][k2]['tipo_de_pendencia'],ges[k][k2]['ticket_id'],ges[k][k2]['status_ticket']) #insere o conjunto de elementos parte da unidade (GE, GE+HXAP, GE+B2B, GE+B2B+HXAP)
                            checkb2b = False
                            if v2['idbtwob']:
                                if "-GE-" in v2['idbtwob']:
                                    checkb2b = True

                            if checkb2b:
                                self.insert_filament(v2['idbtwob'],ges[k][v2['idbtwob']]['element'])
                            else:
                                self.insert_filament(k2,ges[k][k2]['element'])

                            firstGeInserted=1
                    except KeyError:
                        pass
        return None

    def insert_ge(self, x, y, hostid, host_description, device_mode,geName,tipo_de_pendencia = "-",ticket_id = "-",status_ticket = "-"): # adiciona GE no mapa
        label = ""
        
        # if str(tipo_de_pendencia) != "-" and str(tipo_de_pendencia) != "None":
        #     label += "Pending: "+str(tipo_de_pendencia)+"\n"
        
        label += self.config["GE_ICONS"]["label"].replace('\\n', '\n').replace('\\r','\r') if device_mode != "access-point" else self.config["GE_ICONS"]["label_access_point"].replace('\\n','\n').replace('\\r','\r')
        
        label += "\r\nping average: {?avg(/{HOST.HOST}/icmpping[,4,5000,32,10000],24h)}\r\n{HOST.DESCRIPTION}\r\nGE Power (Antenna DB): {?last(/{HOST.HOST}/ge.power.db)}\r\nWD: {?last(/{HOST.HOST}/ge.netmon.restart.trigger)}"
        if "Device has a father with no GWID" in host_description:
            label += "\nDevice has a father with no GWID"
        
        label.replace('\\n', '\n').replace('\\r','\r')
        
        if str(ticket_id) != "-" and str(ticket_id) != "None":
            label += "\nTicket ID: "+str(ticket_id)

        iconid_on = ""
        iconid_off = ""
        iconid_maintenance = ""
        iconid_disabled = ""
            
        if status_ticket != "-":
            if status_ticket in ["1","2","3","4"] and (str(tipo_de_pendencia).upper() == "4" or str(tipo_de_pendencia).upper() == "7"):
                iconid_on = self.config["GE_ICONS"]["iconid_on_pending2"]
                iconid_off = self.config["GE_ICONS"]["iconid_off_pending2"]
                iconid_maintenance = self.config["GE_ICONS"]["iconid_maintenance_pending2"]
                iconid_disabled = self.config["GE_ICONS"]["iconid_disabled_pending2"]
                iconid_disabled_2 = self.config["GE_ICONS"]["iconid_disabled_2_pending2"]
            elif status_ticket == "1":
                iconid_on = self.config["GE_ICONS"]["iconid_on_pending"]
                iconid_off = self.config["GE_ICONS"]["iconid_off_pending"]
                iconid_maintenance = self.config["GE_ICONS"]["iconid_maintenance_pending"]
                iconid_disabled = self.config["GE_ICONS"]["iconid_disabled_pending"]
                iconid_disabled_2 = self.config["GE_ICONS"]["iconid_disabled_2_pending"]
            elif status_ticket == "2":
                iconid_on = self.config["GE_ICONS"]["iconid_on_pending"]
                iconid_off = self.config["GE_ICONS"]["iconid_off_pending"]
                iconid_maintenance = self.config["GE_ICONS"]["iconid_maintenance_pending"]
                iconid_disabled = self.config["GE_ICONS"]["iconid_disabled_pending"]
                iconid_disabled_2 = self.config["GE_ICONS"]["iconid_disabled_2_pending"]
            elif status_ticket == "3":
                iconid_on = self.config["GE_ICONS"]["iconid_on_pending"]
                iconid_off = self.config["GE_ICONS"]["iconid_off_pending"]
                iconid_maintenance = self.config["GE_ICONS"]["iconid_maintenance_pending"]
                iconid_disabled = self.config["GE_ICONS"]["iconid_disabled_pending"]
                iconid_disabled_2 = self.config["GE_ICONS"]["iconid_disabled_2_pending"]
            elif status_ticket == "4":
                if tipo_de_pendencia == "1" or tipo_de_pendencia == "16":
                    iconid_on = self.config["GE_ICONS"]["iconid_on_general"]
                    iconid_off = self.config["GE_ICONS"]["iconid_off_general"]
                    iconid_maintenance = self.config["GE_ICONS"]["iconid_maintenance_general"]
                    iconid_disabled = self.config["GE_ICONS"]["iconid_disabled_general"]
                    iconid_disabled_2 = self.config["GE_ICONS"]["iconid_disabled_2_general"]
                else:
                    iconid_on = self.config["GE_ICONS"]["iconid_on_pending"]
                    iconid_off = self.config["GE_ICONS"]["iconid_off_pending"]
                    iconid_maintenance = self.config["GE_ICONS"]["iconid_maintenance_pending"]
                    iconid_disabled = self.config["GE_ICONS"]["iconid_disabled_pending"]
                    iconid_disabled_2 = self.config["GE_ICONS"]["iconid_disabled_2_pending"]
            elif status_ticket == "5":
                iconid_on = self.config["GE_ICONS"]["iconid_on_solved"]
                iconid_off = self.config["GE_ICONS"]["iconid_off_solved"]
                iconid_maintenance = self.config["GE_ICONS"]["iconid_maintenance_solved"]
                iconid_disabled = self.config["GE_ICONS"]["iconid_disabled_solved"]
                iconid_disabled_2 = self.config["GE_ICONS"]["iconid_disabled_2_solved"]
            elif status_ticket == "6":
                iconid_on = self.config["GE_ICONS"]["iconid_on_closed"]
                iconid_off = self.config["GE_ICONS"]["iconid_off_closed"]
                iconid_maintenance = self.config["GE_ICONS"]["iconid_maintenance_closed"]
                iconid_disabled = self.config["GE_ICONS"]["iconid_disabled_closed"]
                iconid_disabled_2 = self.config["GE_ICONS"]["iconid_disabled_2_closed"]
        else:
            iconid_on = self.config["GE_ICONS"]["iconid_on"]
            iconid_off = self.config["GE_ICONS"]["iconid_off"]
            iconid_maintenance = self.config["GE_ICONS"]["iconid_maintenance"]
            iconid_disabled = self.config["GE_ICONS"]["iconid_disabled"]
            iconid_disabled_2 = self.config["GE_ICONS"]["iconid_disabled_2"]

        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "0" if hostid else "4",
            "iconid_off": iconid_off if hostid else iconid_disabled,
            "iconid_on": iconid_on,
            "label": label if hostid else geName,
            "label_location": "-1",
            "x": x,
            "y": y,
            "iconid_disabled": iconid_disabled if 'previous host' not in host_description else iconid_disabled_2,
            "iconid_maintenance": iconid_maintenance,
            "elementsubtype": "0",
            "areatype": "0",
            "width": self.config["GE_ICONS"]["width"],
            "height": self.config["GE_ICONS"]["height"],
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [{"hostid": hostid}] if hostid else [],
            "urls": [],
            "permission": 2
        })

        return self.main.selementid_count

    def insert_hxap(self, x, y, hostid,host_description,type="HXAP_ICONS",apName=""): #adiciona hxap no mapa
        label = self.config[type]["label"].replace('\\n', '\n').replace('\\r','\r')
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "0" if hostid else "4",
            "iconid_off": self.config[type]["iconid_off"] if hostid else self.config[type]["iconid_disabled"],
            "iconid_on": self.config[type]["iconid_on"],
            "label": label if hostid else apName,
            "label_location": "-1",
            "x": x,
            "y": y,
            "iconid_disabled": self.config[type]["iconid_disabled"] if 'previous host' not in host_description else self.config[type]["iconid_disabled_2"],
            "iconid_maintenance": self.config[type]["iconid_maintenance"],
            "elementsubtype": "0",
            "areatype": "0",
            "width": self.config[type]["width"],
            "height": self.config[type]["height"],
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "elements": [{"hostid": hostid}] if hostid else [],
            "urls": [],
            "permission": 2
        })
    
        return self.main.selementid_count

    def insert_da(self, x, y, hostname, ip = "", hostid = ""): #adiciona da no mapa
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": self.config["DA_ICONS"]["iconid_off"],
            "label": str(hostname)+"\n"+str(ip),
            "label_location": "-1",
            "x": x,
            "y": y,
            "elementsubtype": "0",
            "areatype": "0",
            "viewtype": "0",
            "use_iconmap": "0",
            "application": "",
            "urls": [],
            "permission": 2
        })
    
        return self.main.selementid_count

    def insert_pixel(self, x, y): #adiciona pixel no mapa
        self.main.selements.append({
            "selementid": self.main.sum_selementid_count(),
            "sysmapid": self.main.map_id,
            "elementtype": "4",
            "iconid_off": "2697",
            "iconid_on": "0",
            "label": "",
            "label_location": "-1",
            "x": x,
            "y": y,
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

    def insert_link (self, selementid1, selementid2, trigger_id, label = ""): #adiciona link com ou sem label entre dois elementos já criados
        
        linkid = self.main.sum_linkid_count()
        
        if trigger_id:
            linktriggers = [{
                    "linktriggerid": self.main.sum_linktriggerid_count(),
                    "linkid": linkid,
                    "triggerid": trigger_id,
                    "drawtype": "0",
                    "color": "DD0000"
                }]
        else:
            linktriggers = False
        if linktriggers:
            self.main.links.append({
                "linkid": linkid,
                "sysmapid": self.main.map_id,
                "selementid1": selementid1,
                "selementid2": selementid2,
                "drawtype": "0",
                "color": "00CC00",
                "label": label,
                "linktriggers": linktriggers,
                "permission": 2
            })
        else:
            self.main.links.append({
                "linkid": linkid,
                "sysmapid": self.main.map_id,
                "selementid1": selementid1,
                "selementid2": selementid2,
                "drawtype": "0",
                "color": "00CC00",
                "label": label,
                "permission": 2
            })

    def insert_shape(self,x,y,width,height,font_size,font_color,border_type,border_width,border_color,text="",text_halign=0,text_valign=0):
        self.main.shapes.append({
            "x":x,
            "y":y,
            "type":0,
            "width":width,
            "height":height,
            "font_size":font_size,
            "font_color":font_color,
            "border_type":border_type,
            "border_width":border_width,
            "border_color":border_color,
            "text":text,
            "text_halign":text_halign,
            "text_valign":text_valign,
        })

