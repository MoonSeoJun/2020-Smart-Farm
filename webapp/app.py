from flask import Flask, render_template
import sqlite3
from time import sleep
import threading
from threading import Thread
import serial

'''
ser = serial.Serial(port='COM8',
                       baudrate = 9600,
                        parity = serial.PARITY_NONE,
                        stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS,
                        timeout=1)
'''

app = Flask(__name__)
i = 0

con = sqlite3.connect("data.db")
cur = con.cursor()
cur.execute("CREATE TABLE if not exists datas(temp int, humi int, cds int);")

def thread():
    global i
    while True:
        item = ser.readline()
        temp_humi_data = item.decode('utf-8')
        con = sqlite3.connect("data.db")
        cur = con.cursor()

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

        i += 1

        sleep(3)

@app.route('/')

def index():
    return render_template('index.html', state='HOME')

@app.route('/temp/')

def temp_site():
    global i
    i += 1
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM datas")
    farm_data = cur.fetchall()
    temp_database = farm_data[i][0]

    return render_template('index.html', state='TEMP', temp = temp_database)

@app.route('/humi/')

def humi_site():
    global i
    #데이터베이스에서 가져오기
    i += 1
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM datas")
    farm_data = cur.fetchall()
    humi_database = farm_data[i][1]

    return render_template('index.html', state='HUMI', humi = humi_database)

@app.route('/cds/')

def cds_site():

    global i
    #데이터베이스에서 가져오기
    i += 1
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM datas")
    farm_data = cur.fetchall()
    cds_database = farm_data[i][2]

    return render_template('index.html', state = 'CDS', cds = cds_database)

@app.route('/home/')

def home_site():

    return render_template('index.html', state = 'HOME')


@app.route('/all/')

def all_data_site():

    global i
    #데이터베이스에서 가져오기
    i += 1
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM datas")
    farm_data = cur.fetchall()
    temp_database = farm_data[i][0]
    humi_database = farm_data[i][1]
    cds_database = farm_data[i][2]

    return render_template('index.html', state = "ALL", temp = temp_database, humi = humi_database, cds = cds_database)


if __name__ == '__main__':
    th = threading.Thread(target=thread, args=())
    th.daemon = True
    th.start()
    app.run(host = '0.0.0.0', port = 5000, threaded = True)
    ser.close()