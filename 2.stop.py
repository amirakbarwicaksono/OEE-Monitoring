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

pin_in = 25

GPIO.setmode(GPIO.BCM)
#Setting GPIO
GPIO.setup(pin_in,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setwarnings(False)

tombol=False
status_start = False
print ("Receiving signal from relay STOP and input to database")


first_time = True
time.sleep(1)

while True:
	try:
		if first_time==True:
			print ("First time reset")
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
			first_time = False
		else:
			input=GPIO.input(pin_in)
			time.sleep(0.2)
		
			if input==False:
				#Cek apakah status start true
				cnxn = psycopg2.connect(con_string)
				crsr = cnxn.cursor()
				sql = "select status_start from machine_master where id_machine=" + str(id)
				#print (sql)
				crsr.execute(sql)
				row = crsr.fetchone()
				status_start = row[0]
				cnxn.commit()
				crsr.close()
				cnxn.close()
				time.sleep(0.1)

				if tombol==False:
					if status_start ==True:
						print('STOP ON')
						tombol = True
						time.sleep(0.1)	

						#update di master_machine
						cnxn = psycopg2.connect(con_string)
						crsr = cnxn.cursor()
						sql = "update machine_master set status_stop='True' where id_machine=" + str(id)
						#print (sql)
						crsr.execute(sql)
						crsr = cnxn.cursor()
						cnxn.commit()
						crsr.close()
						cnxn.close()

						#insert data ke trans_stop
						cnxn = psycopg2.connect(con_string)
						crsr = cnxn.cursor()	
						sql = "insert into trans_stop(id_machine) values(" + str(id) + ")"
						#print (sql)
						crsr.execute(sql)
						cnxn.commit()
						crsr.close()
						cnxn.close()

				if status_start ==False and tombol==True:
					print('STOP OFF')
					tombol = False
					time.sleep(0.1)
					#update di master_machine
					cnxn = psycopg2.connect(con_string)
					crsr = cnxn.cursor()
					sql = "update machine_master set status_stop='False' where id_machine=" + str(id)
					print (sql)
					crsr.execute(sql)
					crsr = cnxn.cursor()
					cnxn.commit()
					crsr.close()
					cnxn.close()

					#update data di trans_stop
					cnxn = psycopg2.connect(con_string)
					crsr = cnxn.cursor()	
					sql = "update trans_stop set finish=NOW() where id_machine=" + str(id)+ " and finish is NULL"
					#print (sql)
					crsr.execute(sql)
					cnxn.commit()
					crsr.close()
					cnxn.close()	

				#Jika tiba2 status dipaksa false maka ubah status tombol menjadi false
				else:
					#Cek apakah mesin dalam keadaan stop
					cnxn = psycopg2.connect(con_string)
					crsr = cnxn.cursor()
					sql = "select status_stop from machine_master where id_machine=" + str(id)
					crsr.execute(sql)
					row = crsr.fetchone()
					status_start = row[0]
					cnxn.commit()
					crsr.close()
					cnxn.close()
					if status_start==False:
						tombol = False
						time.sleep(0.1)


			if input==True:
				if tombol==True:
					print('STOP OFF1')
					tombol = False
					time.sleep(0.1)

					#update di master_machine
					cnxn = psycopg2.connect(con_string)
					crsr = cnxn.cursor()
					sql = "update machine_master set status_stop='False' where id_machine=" + str(id)
					#print (sql)
					crsr.execute(sql)
					crsr = cnxn.cursor()
					cnxn.commit()
					crsr.close()
					cnxn.close()

					#update data di trans_operation
					cnxn = psycopg2.connect(con_string)
					crsr = cnxn.cursor()	
					sql = "update trans_stop set finish=NOW() where id_machine=" + str(id)+ " and finish is NULL"
					#print (sql)
					crsr.execute(sql)
					cnxn.commit()
					crsr.close()
					cnxn.close()			

			time.sleep(0.5)
		
	except Exception:
		pass

GPIO.cleanup()		