import RPi.GPIO as GPIO
import time
from datetime import datetime
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

pin_in = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_in,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setwarnings(False)
tombol=False
status_start = False
status_stop = False
qty = 1

print ("Counter output")

time.sleep(0.2)

while True:
	try:
		input=GPIO.input(pin_in)
		time.sleep(0.1)

		if input==False:
			if tombol==False:
				#Cek apakah mesin dalam keadaan run
				cnxn = psycopg2.connect(con_string)
				crsr = cnxn.cursor()
				sql = "select status_start from machine_master where id_machine=" + str(id)
				crsr.execute(sql)
				row = crsr.fetchone()
				status_start = row[0]

				#Cek apakah mesin dalam keadaan stop
				crsr = cnxn.cursor()
				sql = "select status_stop from machine_master where id_machine=" + str(id)
				crsr.execute(sql)
				row = crsr.fetchone()
				status_stop = row[0]
				cnxn.commit()
				crsr.close()
				cnxn.close()
				#time.sleep(0.1)

				if status_start == True and status_stop == False:
					tombol=True
					#time.sleep(0.1)

					sekarang = datetime.now()

					#mengambil tipe yang sedang berjalan
					cnxn = psycopg2.connect(con_string)
					crsr = cnxn.cursor()
					sql = "select id_type,ct,qty_perct from machine_master where id_machine=" + str(id)
					crsr.execute(sql)
					row = crsr.fetchone()
					tipe = row[0]
					ct = row[1]
					qty_perct = row[2]

					crsr = cnxn.cursor()
					sql = "insert into trans_output values(" + str(id) + ",'" + str(tipe) + "',now()," + str(qty) + "," + str(ct) +  "," + str(qty_perct) +  ")"
					crsr.execute(sql)
					cnxn.commit()
					crsr.close()
					cnxn.close()
					#print (sql)
					print("OUTPUT detected, Type: " + str(tipe) + ", Quantity:" + str(qty) + ", " + str(sekarang))

					time.sleep(0.1)
		if input==True:
			if tombol==True:
				tombol=False
				time.sleep(0.1)
	
		time.sleep(0.1)		
	except Exception:
		pass

GPIO.cleanup()		