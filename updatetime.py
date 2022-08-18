import time
import datetime
import os
import psycopg2

import json
file_json = open("/home/pi/OEE/database.json")
data = json.loads(file_json.read())

host = data['host']
dbname = data['dbname']
user = data['user']
password = data['password']
sslmode = data['sslmode']
id = data['id_machine']

con_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)

cnxn = psycopg2.connect(con_string)
crsr = cnxn.cursor()
sql = "SELECT NOW()"
crsr.execute(sql)
row = crsr.fetchone()
tanggal = row[0]
print (tanggal)
os.system("sudo date -s " + "'" + str(tanggal) + "'")

time.sleep(1)
cnxn.commit()
crsr.close()
cnxn.close()
		

		
		
