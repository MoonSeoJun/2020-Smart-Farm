import sqlite3
from time import sleep
from random import randrange
import serial


ser = serial.Serial(port='COM8',
                        baudrate = 9600,
                        parity = serial.PARITY_NONE,
                        stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS,
                        timeout=1)

                        

while True:
    item = ser.readline()
    temp_humi_data = item.decode('utf-8')
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE if not exists datas(temp int, humi int, cds int);")


    temp_data = 0
    humi_data = 0
    cds_data = 0

    if temp_humi_data is not '':
        temp_data = int(temp_humi_data[4:6])
        humi_data = int(temp_humi_data[10:12])
        cds_data = int(temp_humi_data[17:20])

    print(temp_data, humi_data, cds_data)

    cur.execute("INSERT INTO datas VALUES({}, {}, {});".format(temp_data, humi_data, cds_data))
    con.commit()
    con.close()
    sleep(3)