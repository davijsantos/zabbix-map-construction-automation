import mysql.connector
from mysql.connector import errorcode


class ConnectDB:
    def __init__(self, host: str, database: str, user, password, NeedToConvertByteArrayToString=False):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.NeedToConvertByteArrayToString = NeedToConvertByteArrayToString
        
        try:
            self.cnx = mysql.connector.connect(host=host, database=database, user=user, password=password)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
                exit()
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                exit()
            else:
                print(err)
                exit()
            
        self.cursor = self.cnx.cursor(dictionary=True)
        
        
    def query(self, sql):
        self.cnx.commit()
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if self.NeedToConvertByteArrayToString:
            return self.decodeZabbixQueryOutput(result)
        else:
            return result
        
        
    def decodeZabbixQueryOutput(self, data):
        """
            For some reason, mysql ptython module return string
            as bytearray. So, it's needed to convert byte array in string
        """
        output = []
        
        for dt in data:
            _new_dic = {}
            for k, v in dt.items():
                try:
                    if type(v) in (bytearray, bytes):
                        _new_dic[k] = v.decode()
                    else:
                        _new_dic[k] = v
                except:
                    _new_dic[k] = str(v)
                
            output.append(_new_dic)
            
        return output

