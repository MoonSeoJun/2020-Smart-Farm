import threading                                #threading
import serial                                   #arduino port
import PyQt5
import pyqtgraph as pg                          #graph
from smart_farm import *                        #designer ui
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal             #Qt <- signal
from time import sleep                          #time sleep
from functools import partial             
from threading import Thread                    #threading



#그래프 좌표
temp_list = []
humi_list = []
cds_list = []

#아두이노 포트연결
'''
ser = serial.Serial(port='COM8',
                        baudrate = 9600,
                        parity = serial.PARITY_NONE,
                        stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS,
                        timeout=1)
'''

class main(QtWidgets.QMainWindow, Ui_MainWindow):
      update_signal = pyqtSignal()
      def __init__(self, parent=None):
            QtWidgets.QMainWindow.__init__(self, parent=parent)
            self.setupUi(self)
            super().__init__()
            self.update_signal.connect(self.graph_update)

      #그래프 업데이트
      def graph_update(self):

            #온도 그래프
            if self.check_temp.isChecked() == True:
                  self.graphicsView.plot(temp_list, pen=pg.mkPen('r', width=2)) #그래프 표시
            else:
                  self.graphicsView.plot(temp_list, pen=pg.mkPen('w', width=2)) #그래프 숨기기

            #습도 그래프
            if self.check_humi.isChecked() == True:
                  self.graphicsView.plot(humi_list, pen=pg.mkPen('b', width=2)) #그래프 표시
            else: 
                  self.graphicsView.plot(humi_list, pen=pg.mkPen('w', width=2)) #그래프 숨기기

            #조도 그래프
            if self.check_CDS.isChecked() == True:
                  self.graphicsView.plot(cds_list, pen=pg.mkPen('g', width=2)) #그래프 표시
            else:
                  self.graphicsView.plot(cds_list, pen=pg.mkPen('w', width=2)) #그래프 숨기기

            pass

      #Auto 기능 집합
      def Auto_button(self, state):
            
            #바람 불어주기
            if self.check_air.isChecked() == True:
                  print('air on')
            else:
                  print('air off')

            #불 켜주기
            if self.check_light.isChecked() == True:
                  print('light on')
                  ser.write(('LEDON' + '\n').encode())
            else:
                  print('light off')
                  ser.write(('LEDOFf' + '\n').encode())

            #물 뿌려주기
            if self.check_water.isChecked() == True:
                  print('water on')
            else:
                  print('water off') 

            print('\n----------------------------------\n')         

      #메뉴
      def setup(self):

            #창 바꾸기
            mainButton_list = [self.page1_button,self.page2_button,self.page3_button,self.page4_button]
            for i, mainButton in enumerate(mainButton_list):
                  mainButton.clicked.connect(partial(self.stackedWidget.setCurrentIndex, i))

            #종료 버튼
            self.Quit_button.clicked.connect(self.close_app)

            #자동화 버튼
            self.check_water.stateChanged.connect(self.Auto_button)
            self.check_light.stateChanged.connect(self.Auto_button)
            self.check_air.stateChanged.connect(self.Auto_button)

            #그래프 색상 및 원하는 그래프 표시하기
            self.graphicsView.setBackground('#FFFFFF')
            self.check_temp.stateChanged.connect(self.graph_update)
            self.check_humi.stateChanged.connect(self.graph_update)
            self.check_CDS.stateChanged.connect(self.graph_update)

      #종료
      def close_app(self):
            print('close_app')
            sys.exit()


#온습도, 조도 값 받아오기
def temp_humi_thread(ui):
      global temp_list, humi_list, cds_list
      while True:
            #온습도,조도 출력
            item = ser.readline()
            temp_humi_data = item.decode('utf-8')
            ui.temp_label.setText(str(temp_humi_data[4:6]))
            ui.humi_label.setText(str(temp_humi_data[10:12]))
            ui.cds_label.setText(str(temp_humi_data[17:20]))
            
            #정수형으로 변환해서 그래프로 표현
            if temp_humi_data is not '':
                  temp_list.append(int(temp_humi_data[4:6]))
                  humi_list.append(int(temp_humi_data[10:12]))
                  cds_list.append(int(temp_humi_data[17:20]))

            ui.update_signal.emit()
            
            #데이터 베이스에 값 저장
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

            cur.execute("INSERT INTO datas VALUES({}, {}, {});".format(temp_data, humi_data, cds_data))
            con.commit()
            con.close()
                  
            sleep(3)  

if __name__ == "__main__":
      import sys
      app = QtWidgets.QApplication(sys.argv)
      MainWindow = QtWidgets.QMainWindow()
      ui = main()
      ui.setupUi(MainWindow)

      th = threading.Thread(target=temp_humi_thread, args=(ui,))
      th.daemon = True
      th.start()

      ui.setupUi(MainWindow)
      ui.setup()

      MainWindow.show()
      sys.exit(app.exec_())
