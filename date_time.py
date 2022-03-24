import serial
import datetime
import time

ser = serial.Serial('/dev/ttyACM0')

date_count = 0

while 1:

    date = datetime.datetime.now()

    time_data = date.strftime("%H:%M")

    if time_data == "08:30":
        ser.write("LEDON\n".encode())
    if time_data == "20:30":
        ser.write("LEDOFF\n".encode())


    print(time_data)

    time.sleep(2)