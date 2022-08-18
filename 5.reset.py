#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import datetime
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

print ("Reset Database Stop dan Start")

#Start time----------------------------------------------
print ("Reset start")
cnxn = psycopg2.connect(con_string)
crsr = cnxn.cursor()
sql = "update machine_master set status_start='False' where id_machine=" + str(id)
crsr.execute(sql)
crsr = cnxn.cursor()
cnxn.commit()
crsr.close()
cnxn.close()

#update data di trans_operation
cnxn = psycopg2.connect(con_string)
crsr = cnxn.cursor()	
sql = "update trans_operation set finish=NOW() where id_machine=" + str(id)+ " and finish is NULL"
print (sql)
crsr.execute(sql)
cnxn.commit()
crsr.close()
cnxn.close()	

#Stop time----------------------------------------------
time.sleep(1)
print ("Reset stop")
cnxn = psycopg2.connect(con_string)
crsr = cnxn.cursor()
sql = "update machine_master set status_stop='False' where id_machine=" + str(id)
crsr.execute(sql)
crsr = cnxn.cursor()
cnxn.commit()
crsr.close()
cnxn.close()

#update data di trans_stop
cnxn = psycopg2.connect(con_string)
crsr = cnxn.cursor()	
sql = "update trans_stop set finish=NOW() where id_machine=" + str(id)+ " and finish is NULL"
print (sql)
crsr.execute(sql)
cnxn.commit()
crsr.close()
cnxn.close()	

time.sleep(1)


	