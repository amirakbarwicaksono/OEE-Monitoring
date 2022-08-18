import RPi.GPIO as GPIO
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
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
awal = data['awal_hour']
akhir = data['akhir_hour']
jam_akhir = data['jam_akhir']

con_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)

pin_in = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_in,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setwarnings(False)
tombol=False

print ("Counter Defect")
time.sleep(0.2)

while True:
	try:
		sekarang = datetime.now()
		jam = int(sekarang.hour)
		tgl_skrg = str(sekarang)[:10]
		tgl_skrg2 = str(sekarang)[:19]
	
		if 0 <= jam <=jam_akhir:
			start_date = sekarang + relativedelta(days=-1)
			tgl = start_date.strftime("%Y-%m-%d")
			tgl2 = sekarang.strftime("%Y-%m-%d")

		else:
			end_date = sekarang + relativedelta(days=1)
			tgl = sekarang.strftime("%Y-%m-%d")
			tgl2 = end_date.strftime("%Y-%m-%d")

		input=GPIO.input(pin_in)
		time.sleep(0.1)			

		if input==False:
			input=GPIO.input(pin_in)
			time.sleep(0.1)

			#----------------------
			#mengambil tipe yang sedang berjalan
			cnxn = psycopg2.connect(con_string)
			crsr = cnxn.cursor()
			sql = "select id_type,ct,qty_perct from machine_master where id_machine=" + str(id)
			#print(sql)
			crsr.execute(sql)
			row = crsr.fetchone()
			tipe = row[0]
			ct = row[1]
			qty_perct = row[2]
			cnxn.commit()
			crsr.close()
			cnxn.close()
			#print("Type yang sedang berjalan: " + str(tipe))

			#Cek berapa jumlah output
			cnxn = psycopg2.connect(con_string)
			crsr = cnxn.cursor()
			sql = "select sum(qty) from trans_output where id_machine=" + str(id) + " and id_type=" + str(tipe) + " and time between '" + tgl + awal + "' and '" + tgl2 + akhir + "'"
			#print(sql)
			crsr.execute(sql)
			row = crsr.fetchone()
			if row[0] != None:		
				qty = int(row[0])
			else:
				qty=0

			cnxn.commit()
			crsr.close()
			cnxn.close()
			#print("Type: " + str(tipe) + ", Total output: " + str(qty))

			#Cek berapa ng yang telah ditambahkan
			cnxn = psycopg2.connect(con_string)
			crsr = cnxn.cursor()
			sql = "select sum(qty) from trans_ng where id_machine=" + str(id) + " and id_type=" + str(tipe) + " and time between '" + tgl + awal + "' and '" + tgl2 + akhir + "'"
			#print(sql)
			crsr.execute(sql)
			row = crsr.fetchone()
			if row[0] != None:			
				qty_ng = int(row[0])
			else:
				qty_ng=0
			cnxn.commit()
			crsr.close()
			cnxn.close()
			#print("Total output NG: " + str(qty_ng))
			sisa = int(qty) - int(qty_ng)
			#print("Sisa: " + str(sisa))
			#----------------------

			print("Sisa output: " + str(sisa))
			if tombol==False and input==False and sisa > 0:
				print("NG detected, Type: " + str(tipe) + ", Sisa Quantity:" + str(sisa-1))
				tombol=True
				cnxn = psycopg2.connect(con_string)
				crsr = cnxn.cursor()
				sql = "insert into trans_ng (id_machine,id_type,time,qty,ct,qty_perct) values(" + str(id) + ",'" + str(tipe) + "',now(),1," + str(ct) + "," + str(qty_perct) + ")"
				crsr.execute(sql)
				cnxn.commit()
				crsr.close()
				cnxn.close()

				time.sleep(0.1)
		if input==True:
			if tombol==True:
				tombol=False
				time.sleep(0.1)
	
		time.sleep(0.2)	
	
	except Exception:
		pass

GPIO.cleanup()		