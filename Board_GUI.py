# -*- coding: utf-8 -*-
import copy
import sys
from Board import Ui_MainWindow
from PyQt5 import QtGui, QtCore, QtWidgets, QtMultimedia
from PyQt5.QtWidgets import QApplication, QMainWindow
from gameManager import *


# Preset
goBoard = [[0 for i in range(19)] for j in range(19)]
blackPreviousBoard = copy.deepcopy(goBoard)
whitePreviousBoard = copy.deepcopy(goBoard)
turns = get_turns()
chessNum = 0


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        global goBoard
        global turns

        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Nighty Go')
        self.statusBar().showMessage('歡迎使用 Nighty Go 記譜程式。')

        # Chess
        self.c01 = Chess(self.centralwidget)
        self.c01.setGeometry(QtCore.QRect(7, 57, 42, 42))
        self.c01.setText("")
        self.c01.setScaledContents(True)
        self.c01.setObjectName("c01")
        self.c02 = Chess(self.centralwidget)
        self.c02.setGeometry(QtCore.QRect(57, 57, 42, 42))
        self.c02.setText("")
        self.c02.setScaledContents(True)
        self.c02.setObjectName("c02")
        self.c03 = Chess(self.centralwidget)
        self.c03.setGeometry(QtCore.QRect(107, 57, 42, 42))
        self.c03.setText("")
        self.c03.setScaledContents(True)
        self.c03.setObjectName("c03")
        self.c04 = Chess(self.centralwidget)
        self.c04.setGeometry(QtCore.QRect(157, 57, 42, 42))
        self.c04.setText("")
        self.c04.setScaledContents(True)
        self.c04.setObjectName("c04")
        self.c05 = Chess(self.centralwidget)
        self.c05.setGeometry(QtCore.QRect(207, 57, 42, 42))
        self.c05.setText("")
        self.c05.setScaledContents(True)
        self.c05.setObjectName("c05")
        self.c06 = Chess(self.centralwidget)
        self.c06.setGeometry(QtCore.QRect(257, 57, 42, 42))
        self.c06.setText("")
        self.c06.setScaledContents(True)
        self.c06.setObjectName("c06")
        self.c07 = Chess(self.centralwidget)
        self.c07.setGeometry(QtCore.QRect(307, 57, 42, 42))
        self.c07.setText("")
        self.c07.setScaledContents(True)
        self.c07.setObjectName("c07")
        self.c08 = Chess(self.centralwidget)
        self.c08.setGeometry(QtCore.QRect(357, 57, 42, 42))
        self.c08.setText("")
        self.c08.setScaledContents(True)
        self.c08.setObjectName("c08")
        self.c09 = Chess(self.centralwidget)
        self.c09.setGeometry(QtCore.QRect(407, 57, 42, 42))
        self.c09.setText("")
        self.c09.setScaledContents(True)
        self.c09.setObjectName("c09")
        self.c10 = Chess(self.centralwidget)
        self.c10.setGeometry(QtCore.QRect(457, 57, 42, 42))
        self.c10.setText("")
        self.c10.setScaledContents(True)
        self.c10.setObjectName("c10")
        self.c11 = Chess(self.centralwidget)
        self.c11.setGeometry(QtCore.QRect(507, 57, 42, 42))
        self.c11.setText("")
        self.c11.setScaledContents(True)
        self.c11.setObjectName("c11")
        self.c12 = Chess(self.centralwidget)
        self.c12.setGeometry(QtCore.QRect(557, 57, 42, 42))
        self.c12.setText("")
        self.c12.setScaledContents(True)
        self.c12.setObjectName("c12")
        self.c13 = Chess(self.centralwidget)
        self.c13.setGeometry(QtCore.QRect(607, 57, 42, 42))
        self.c13.setText("")
        self.c13.setScaledContents(True)
        self.c13.setObjectName("c13")
        self.c14 = Chess(self.centralwidget)
        self.c14.setGeometry(QtCore.QRect(657, 57, 42, 42))
        self.c14.setText("")
        self.c14.setScaledContents(True)
        self.c14.setObjectName("c14")
        self.c15 = Chess(self.centralwidget)
        self.c15.setGeometry(QtCore.QRect(707, 57, 42, 42))
        self.c15.setText("")
        self.c15.setScaledContents(True)
        self.c15.setObjectName("c15")
        self.c16 = Chess(self.centralwidget)
        self.c16.setGeometry(QtCore.QRect(757, 57, 42, 42))
        self.c16.setText("")
        self.c16.setScaledContents(True)
        self.c16.setObjectName("c16")
        self.c17 = Chess(self.centralwidget)
        self.c17.setGeometry(QtCore.QRect(807, 57, 42, 42))
        self.c17.setText("")
        self.c17.setScaledContents(True)
        self.c17.setObjectName("c17")
        self.c18 = Chess(self.centralwidget)
        self.c18.setGeometry(QtCore.QRect(857, 57, 42, 42))
        self.c18.setText("")
        self.c18.setScaledContents(True)
        self.c18.setObjectName("c18")
        self.c19 = Chess(self.centralwidget)
        self.c19.setGeometry(QtCore.QRect(907, 57, 42, 42))
        self.c19.setText("")
        self.c19.setScaledContents(True)
        self.c19.setObjectName("c19")
        self.c25 = Chess(self.centralwidget)
        self.c25.setGeometry(QtCore.QRect(257, 107, 42, 42))
        self.c25.setText("")
        self.c25.setScaledContents(True)
        self.c25.setObjectName("c25")
        self.c27 = Chess(self.centralwidget)
        self.c27.setGeometry(QtCore.QRect(357, 107, 42, 42))
        self.c27.setText("")
        self.c27.setScaledContents(True)
        self.c27.setObjectName("c27")
        self.c20 = Chess(self.centralwidget)
        self.c20.setGeometry(QtCore.QRect(7, 107, 42, 42))
        self.c20.setText("")
        self.c20.setScaledContents(True)
        self.c20.setObjectName("c20")
        self.c33 = Chess(self.centralwidget)
        self.c33.setGeometry(QtCore.QRect(657, 107, 42, 42))
        self.c33.setText("")
        self.c33.setScaledContents(True)
        self.c33.setObjectName("c33")
        self.c22 = Chess(self.centralwidget)
        self.c22.setGeometry(QtCore.QRect(107, 107, 42, 42))
        self.c22.setText("")
        self.c22.setScaledContents(True)
        self.c22.setObjectName("c22")
        self.c34 = Chess(self.centralwidget)
        self.c34.setGeometry(QtCore.QRect(707, 107, 42, 42))
        self.c34.setText("")
        self.c34.setScaledContents(True)
        self.c34.setObjectName("c34")
        self.c26 = Chess(self.centralwidget)
        self.c26.setGeometry(QtCore.QRect(307, 107, 42, 42))
        self.c26.setText("")
        self.c26.setScaledContents(True)
        self.c26.setObjectName("c26")
        self.c28 = Chess(self.centralwidget)
        self.c28.setGeometry(QtCore.QRect(407, 107, 42, 42))
        self.c28.setText("")
        self.c28.setScaledContents(True)
        self.c28.setObjectName("c28")
        self.c31 = Chess(self.centralwidget)
        self.c31.setGeometry(QtCore.QRect(557, 107, 42, 42))
        self.c31.setText("")
        self.c31.setScaledContents(True)
        self.c31.setObjectName("c31")
        self.c24 = Chess(self.centralwidget)
        self.c24.setGeometry(QtCore.QRect(207, 107, 42, 42))
        self.c24.setText("")
        self.c24.setScaledContents(True)
        self.c24.setObjectName("c24")
        self.c35 = Chess(self.centralwidget)
        self.c35.setGeometry(QtCore.QRect(757, 107, 42, 42))
        self.c35.setText("")
        self.c35.setScaledContents(True)
        self.c35.setObjectName("c35")
        self.c38 = Chess(self.centralwidget)
        self.c38.setGeometry(QtCore.QRect(907, 107, 42, 42))
        self.c38.setText("")
        self.c38.setScaledContents(True)
        self.c38.setObjectName("c38")
        self.c30 = Chess(self.centralwidget)
        self.c30.setGeometry(QtCore.QRect(507, 107, 42, 42))
        self.c30.setText("")
        self.c30.setScaledContents(True)
        self.c30.setObjectName("c30")
        self.c36 = Chess(self.centralwidget)
        self.c36.setGeometry(QtCore.QRect(807, 107, 42, 42))
        self.c36.setText("")
        self.c36.setScaledContents(True)
        self.c36.setObjectName("c36")
        self.c21 = Chess(self.centralwidget)
        self.c21.setGeometry(QtCore.QRect(57, 107, 42, 42))
        self.c21.setText("")
        self.c21.setScaledContents(True)
        self.c21.setObjectName("c21")
        self.c29 = Chess(self.centralwidget)
        self.c29.setGeometry(QtCore.QRect(457, 107, 42, 42))
        self.c29.setText("")
        self.c29.setScaledContents(True)
        self.c29.setObjectName("c29")
        self.c37 = Chess(self.centralwidget)
        self.c37.setGeometry(QtCore.QRect(857, 107, 42, 42))
        self.c37.setText("")
        self.c37.setScaledContents(True)
        self.c37.setObjectName("c37")
        self.c32 = Chess(self.centralwidget)
        self.c32.setGeometry(QtCore.QRect(607, 107, 42, 42))
        self.c32.setText("")
        self.c32.setScaledContents(True)
        self.c32.setObjectName("c32")
        self.c23 = Chess(self.centralwidget)
        self.c23.setGeometry(QtCore.QRect(157, 107, 42, 42))
        self.c23.setText("")
        self.c23.setScaledContents(True)
        self.c23.setObjectName("c23")
        self.c52 = Chess(self.centralwidget)
        self.c52.setGeometry(QtCore.QRect(657, 157, 42, 42))
        self.c52.setText("")
        self.c52.setScaledContents(True)
        self.c52.setObjectName("c52")
        self.c50 = Chess(self.centralwidget)
        self.c50.setGeometry(QtCore.QRect(557, 157, 42, 42))
        self.c50.setText("")
        self.c50.setScaledContents(True)
        self.c50.setObjectName("c50")
        self.c56 = Chess(self.centralwidget)
        self.c56.setGeometry(QtCore.QRect(857, 157, 42, 42))
        self.c56.setText("")
        self.c56.setScaledContents(True)
        self.c56.setObjectName("c56")
        self.c58 = Chess(self.centralwidget)
        self.c58.setGeometry(QtCore.QRect(7, 207, 42, 42))
        self.c58.setText("")
        self.c58.setScaledContents(True)
        self.c58.setObjectName("c58")
        self.c43 = Chess(self.centralwidget)
        self.c43.setGeometry(QtCore.QRect(207, 157, 42, 42))
        self.c43.setText("")
        self.c43.setScaledContents(True)
        self.c43.setObjectName("c43")
        self.c41 = Chess(self.centralwidget)
        self.c41.setGeometry(QtCore.QRect(107, 157, 42, 42))
        self.c41.setText("")
        self.c41.setScaledContents(True)
        self.c41.setObjectName("c41")
        self.c74 = Chess(self.centralwidget)
        self.c74.setGeometry(QtCore.QRect(807, 207, 42, 42))
        self.c74.setText("")
        self.c74.setScaledContents(True)
        self.c74.setObjectName("c74")
        self.c53 = Chess(self.centralwidget)
        self.c53.setGeometry(QtCore.QRect(707, 157, 42, 42))
        self.c53.setText("")
        self.c53.setScaledContents(True)
        self.c53.setObjectName("c53")
        self.c64 = Chess(self.centralwidget)
        self.c64.setGeometry(QtCore.QRect(307, 207, 42, 42))
        self.c64.setText("")
        self.c64.setScaledContents(True)
        self.c64.setObjectName("c64")
        self.c57 = Chess(self.centralwidget)
        self.c57.setGeometry(QtCore.QRect(907, 157, 42, 42))
        self.c57.setText("")
        self.c57.setScaledContents(True)
        self.c57.setObjectName("c57")
        self.c49 = Chess(self.centralwidget)
        self.c49.setGeometry(QtCore.QRect(507, 157, 42, 42))
        self.c49.setText("")
        self.c49.setScaledContents(True)
        self.c49.setObjectName("c49")
        self.c62 = Chess(self.centralwidget)
        self.c62.setGeometry(QtCore.QRect(207, 207, 42, 42))
        self.c62.setText("")
        self.c62.setScaledContents(True)
        self.c62.setObjectName("c62")
        self.c54 = Chess(self.centralwidget)
        self.c54.setGeometry(QtCore.QRect(757, 157, 42, 42))
        self.c54.setText("")
        self.c54.setScaledContents(True)
        self.c54.setObjectName("c54")
        self.c47 = Chess(self.centralwidget)
        self.c47.setGeometry(QtCore.QRect(407, 157, 42, 42))
        self.c47.setText("")
        self.c47.setScaledContents(True)
        self.c47.setObjectName("c47")
        self.c63 = Chess(self.centralwidget)
        self.c63.setGeometry(QtCore.QRect(257, 207, 42, 42))
        self.c63.setText("")
        self.c63.setScaledContents(True)
        self.c63.setObjectName("c63")
        self.c72 = Chess(self.centralwidget)
        self.c72.setGeometry(QtCore.QRect(707, 207, 42, 42))
        self.c72.setText("")
        self.c72.setScaledContents(True)
        self.c72.setObjectName("c72")
        self.c55 = Chess(self.centralwidget)
        self.c55.setGeometry(QtCore.QRect(807, 157, 42, 42))
        self.c55.setText("")
        self.c55.setScaledContents(True)
        self.c55.setObjectName("c55")
        self.c70 = Chess(self.centralwidget)
        self.c70.setGeometry(QtCore.QRect(607, 207, 42, 42))
        self.c70.setText("")
        self.c70.setScaledContents(True)
        self.c70.setObjectName("c70")
        self.c44 = Chess(self.centralwidget)
        self.c44.setGeometry(QtCore.QRect(257, 157, 42, 42))
        self.c44.setText("")
        self.c44.setScaledContents(True)
        self.c44.setObjectName("c44")
        self.c75 = Chess(self.centralwidget)
        self.c75.setGeometry(QtCore.QRect(857, 207, 42, 42))
        self.c75.setText("")
        self.c75.setScaledContents(True)
        self.c75.setObjectName("c75")
        self.c69 = Chess(self.centralwidget)
        self.c69.setGeometry(QtCore.QRect(557, 207, 42, 42))
        self.c69.setText("")
        self.c69.setScaledContents(True)
        self.c69.setObjectName("c69")
        self.c59 = Chess(self.centralwidget)
        self.c59.setGeometry(QtCore.QRect(57, 207, 42, 42))
        self.c59.setText("")
        self.c59.setScaledContents(True)
        self.c59.setObjectName("c59")
        self.c76 = Chess(self.centralwidget)
        self.c76.setGeometry(QtCore.QRect(907, 207, 42, 42))
        self.c76.setText("")
        self.c76.setScaledContents(True)
        self.c76.setObjectName("c76")
        self.c60 = Chess(self.centralwidget)
        self.c60.setGeometry(QtCore.QRect(107, 207, 42, 42))
        self.c60.setText("")
        self.c60.setScaledContents(True)
        self.c60.setObjectName("c60")
        self.c66 = Chess(self.centralwidget)
        self.c66.setGeometry(QtCore.QRect(407, 207, 42, 42))
        self.c66.setText("")
        self.c66.setScaledContents(True)
        self.c66.setObjectName("c66")
        self.c73 = Chess(self.centralwidget)
        self.c73.setGeometry(QtCore.QRect(757, 207, 42, 42))
        self.c73.setText("")
        self.c73.setScaledContents(True)
        self.c73.setObjectName("c73")
        self.c42 = Chess(self.centralwidget)
        self.c42.setGeometry(QtCore.QRect(157, 157, 42, 42))
        self.c42.setText("")
        self.c42.setScaledContents(True)
        self.c42.setObjectName("c42")
        self.c46 = Chess(self.centralwidget)
        self.c46.setGeometry(QtCore.QRect(357, 157, 42, 42))
        self.c46.setText("")
        self.c46.setScaledContents(True)
        self.c46.setObjectName("c46")
        self.c68 = Chess(self.centralwidget)
        self.c68.setGeometry(QtCore.QRect(507, 207, 42, 42))
        self.c68.setText("")
        self.c68.setScaledContents(True)
        self.c68.setObjectName("c68")
        self.c61 = Chess(self.centralwidget)
        self.c61.setGeometry(QtCore.QRect(157, 207, 42, 42))
        self.c61.setText("")
        self.c61.setScaledContents(True)
        self.c61.setObjectName("c61")
        self.c48 = Chess(self.centralwidget)
        self.c48.setGeometry(QtCore.QRect(457, 157, 42, 42))
        self.c48.setText("")
        self.c48.setScaledContents(True)
        self.c48.setObjectName("c48")
        self.c71 = Chess(self.centralwidget)
        self.c71.setGeometry(QtCore.QRect(657, 207, 42, 42))
        self.c71.setText("")
        self.c71.setScaledContents(True)
        self.c71.setObjectName("c71")
        self.c67 = Chess(self.centralwidget)
        self.c67.setGeometry(QtCore.QRect(457, 207, 42, 42))
        self.c67.setText("")
        self.c67.setScaledContents(True)
        self.c67.setObjectName("c67")
        self.c45 = Chess(self.centralwidget)
        self.c45.setGeometry(QtCore.QRect(307, 157, 42, 42))
        self.c45.setText("")
        self.c45.setScaledContents(True)
        self.c45.setObjectName("c45")
        self.c65 = Chess(self.centralwidget)
        self.c65.setGeometry(QtCore.QRect(357, 207, 42, 42))
        self.c65.setText("")
        self.c65.setScaledContents(True)
        self.c65.setObjectName("c65")
        self.c40 = Chess(self.centralwidget)
        self.c40.setGeometry(QtCore.QRect(57, 157, 42, 42))
        self.c40.setText("")
        self.c40.setScaledContents(True)
        self.c40.setObjectName("c40")
        self.c51 = Chess(self.centralwidget)
        self.c51.setGeometry(QtCore.QRect(607, 157, 42, 42))
        self.c51.setText("")
        self.c51.setScaledContents(True)
        self.c51.setObjectName("c51")
        self.c39 = Chess(self.centralwidget)
        self.c39.setGeometry(QtCore.QRect(7, 157, 42, 42))
        self.c39.setText("")
        self.c39.setScaledContents(True)
        self.c39.setObjectName("c39")
        self.c116 = Chess(self.centralwidget)
        self.c116.setGeometry(QtCore.QRect(57, 357, 42, 42))
        self.c116.setText("")
        self.c116.setScaledContents(True)
        self.c116.setObjectName("c116")
        self.c124 = Chess(self.centralwidget)
        self.c124.setGeometry(QtCore.QRect(457, 357, 42, 42))
        self.c124.setText("")
        self.c124.setScaledContents(True)
        self.c124.setObjectName("c124")
        self.c141 = Chess(self.centralwidget)
        self.c141.setGeometry(QtCore.QRect(357, 407, 42, 42))
        self.c141.setText("")
        self.c141.setScaledContents(True)
        self.c141.setObjectName("c141")
        self.c101 = Chess(self.centralwidget)
        self.c101.setGeometry(QtCore.QRect(257, 307, 42, 42))
        self.c101.setText("")
        self.c101.setScaledContents(True)
        self.c101.setObjectName("c101")
        self.c108 = Chess(self.centralwidget)
        self.c108.setGeometry(QtCore.QRect(607, 307, 42, 42))
        self.c108.setText("")
        self.c108.setScaledContents(True)
        self.c108.setObjectName("c108")
        self.c142 = Chess(self.centralwidget)
        self.c142.setGeometry(QtCore.QRect(407, 407, 42, 42))
        self.c142.setText("")
        self.c142.setScaledContents(True)
        self.c142.setObjectName("c142")
        self.c128 = Chess(self.centralwidget)
        self.c128.setGeometry(QtCore.QRect(657, 357, 42, 42))
        self.c128.setText("")
        self.c128.setScaledContents(True)
        self.c128.setObjectName("c128")
        self.c113 = Chess(self.centralwidget)
        self.c113.setGeometry(QtCore.QRect(857, 307, 42, 42))
        self.c113.setText("")
        self.c113.setScaledContents(True)
        self.c113.setObjectName("c113")
        self.c125 = Chess(self.centralwidget)
        self.c125.setGeometry(QtCore.QRect(507, 357, 42, 42))
        self.c125.setText("")
        self.c125.setScaledContents(True)
        self.c125.setObjectName("c125")
        self.c150 = Chess(self.centralwidget)
        self.c150.setGeometry(QtCore.QRect(807, 407, 42, 42))
        self.c150.setText("")
        self.c150.setScaledContents(True)
        self.c150.setObjectName("c150")
        self.c99 = Chess(self.centralwidget)
        self.c99.setGeometry(QtCore.QRect(157, 307, 42, 42))
        self.c99.setText("")
        self.c99.setScaledContents(True)
        self.c99.setObjectName("c99")
        self.c117 = Chess(self.centralwidget)
        self.c117.setGeometry(QtCore.QRect(107, 357, 42, 42))
        self.c117.setText("")
        self.c117.setScaledContents(True)
        self.c117.setObjectName("c117")
        self.c112 = Chess(self.centralwidget)
        self.c112.setGeometry(QtCore.QRect(807, 307, 42, 42))
        self.c112.setText("")
        self.c112.setScaledContents(True)
        self.c112.setObjectName("c112")
        self.c89 = Chess(self.centralwidget)
        self.c89.setGeometry(QtCore.QRect(607, 257, 42, 42))
        self.c89.setText("")
        self.c89.setScaledContents(True)
        self.c89.setObjectName("c89")
        self.c127 = Chess(self.centralwidget)
        self.c127.setGeometry(QtCore.QRect(607, 357, 42, 42))
        self.c127.setText("")
        self.c127.setScaledContents(True)
        self.c127.setObjectName("c127")
        self.c88 = Chess(self.centralwidget)
        self.c88.setGeometry(QtCore.QRect(557, 257, 42, 42))
        self.c88.setText("")
        self.c88.setScaledContents(True)
        self.c88.setObjectName("c88")
        self.c136 = Chess(self.centralwidget)
        self.c136.setGeometry(QtCore.QRect(107, 407, 42, 42))
        self.c136.setText("")
        self.c136.setScaledContents(True)
        self.c136.setObjectName("c136")
        self.c92 = Chess(self.centralwidget)
        self.c92.setGeometry(QtCore.QRect(757, 257, 42, 42))
        self.c92.setText("")
        self.c92.setScaledContents(True)
        self.c92.setObjectName("c92")
        self.c133 = Chess(self.centralwidget)
        self.c133.setGeometry(QtCore.QRect(907, 357, 42, 42))
        self.c133.setText("")
        self.c133.setScaledContents(True)
        self.c133.setObjectName("c133")
        self.c111 = Chess(self.centralwidget)
        self.c111.setGeometry(QtCore.QRect(757, 307, 42, 42))
        self.c111.setText("")
        self.c111.setScaledContents(True)
        self.c111.setObjectName("c111")
        self.c109 = Chess(self.centralwidget)
        self.c109.setGeometry(QtCore.QRect(657, 307, 42, 42))
        self.c109.setText("")
        self.c109.setScaledContents(True)
        self.c109.setObjectName("c109")
        self.c97 = Chess(self.centralwidget)
        self.c97.setGeometry(QtCore.QRect(57, 307, 42, 42))
        self.c97.setText("")
        self.c97.setScaledContents(True)
        self.c97.setObjectName("c97")
        self.c143 = Chess(self.centralwidget)
        self.c143.setGeometry(QtCore.QRect(457, 407, 42, 42))
        self.c143.setText("")
        self.c143.setScaledContents(True)
        self.c143.setObjectName("c143")
        self.c145 = Chess(self.centralwidget)
        self.c145.setGeometry(QtCore.QRect(557, 407, 42, 42))
        self.c145.setText("")
        self.c145.setScaledContents(True)
        self.c145.setObjectName("c145")
        self.c110 = Chess(self.centralwidget)
        self.c110.setGeometry(QtCore.QRect(707, 307, 42, 42))
        self.c110.setText("")
        self.c110.setScaledContents(True)
        self.c110.setObjectName("c110")
        self.c139 = Chess(self.centralwidget)
        self.c139.setGeometry(QtCore.QRect(257, 407, 42, 42))
        self.c139.setText("")
        self.c139.setScaledContents(True)
        self.c139.setObjectName("c139")
        self.c82 = Chess(self.centralwidget)
        self.c82.setGeometry(QtCore.QRect(257, 257, 42, 42))
        self.c82.setText("")
        self.c82.setScaledContents(True)
        self.c82.setObjectName("c82")
        self.c80 = Chess(self.centralwidget)
        self.c80.setGeometry(QtCore.QRect(157, 257, 42, 42))
        self.c80.setText("")
        self.c80.setScaledContents(True)
        self.c80.setObjectName("c80")
        self.c126 = Chess(self.centralwidget)
        self.c126.setGeometry(QtCore.QRect(557, 357, 42, 42))
        self.c126.setText("")
        self.c126.setScaledContents(True)
        self.c126.setObjectName("c126")
        self.c131 = Chess(self.centralwidget)
        self.c131.setGeometry(QtCore.QRect(807, 357, 42, 42))
        self.c131.setText("")
        self.c131.setScaledContents(True)
        self.c131.setObjectName("c131")
        self.c91 = Chess(self.centralwidget)
        self.c91.setGeometry(QtCore.QRect(707, 257, 42, 42))
        self.c91.setText("")
        self.c91.setScaledContents(True)
        self.c91.setObjectName("c91")
        self.c98 = Chess(self.centralwidget)
        self.c98.setGeometry(QtCore.QRect(107, 307, 42, 42))
        self.c98.setText("")
        self.c98.setScaledContents(True)
        self.c98.setObjectName("c98")
        self.c81 = Chess(self.centralwidget)
        self.c81.setGeometry(QtCore.QRect(207, 257, 42, 42))
        self.c81.setText("")
        self.c81.setScaledContents(True)
        self.c81.setObjectName("c81")
        self.c95 = Chess(self.centralwidget)
        self.c95.setGeometry(QtCore.QRect(907, 257, 42, 42))
        self.c95.setText("")
        self.c95.setScaledContents(True)
        self.c95.setObjectName("c95")
        self.c84 = Chess(self.centralwidget)
        self.c84.setGeometry(QtCore.QRect(357, 257, 42, 42))
        self.c84.setText("")
        self.c84.setScaledContents(True)
        self.c84.setObjectName("c84")
        self.c90 = Chess(self.centralwidget)
        self.c90.setGeometry(QtCore.QRect(657, 257, 42, 42))
        self.c90.setText("")
        self.c90.setScaledContents(True)
        self.c90.setObjectName("c90")
        self.c115 = Chess(self.centralwidget)
        self.c115.setGeometry(QtCore.QRect(7, 357, 42, 42))
        self.c115.setText("")
        self.c115.setScaledContents(True)
        self.c115.setObjectName("c115")
        self.c134 = Chess(self.centralwidget)
        self.c134.setGeometry(QtCore.QRect(7, 407, 42, 42))
        self.c134.setText("")
        self.c134.setScaledContents(True)
        self.c134.setObjectName("c134")
        self.c151 = Chess(self.centralwidget)
        self.c151.setGeometry(QtCore.QRect(857, 407, 42, 42))
        self.c151.setText("")
        self.c151.setScaledContents(True)
        self.c151.setObjectName("c151")
        self.c149 = Chess(self.centralwidget)
        self.c149.setGeometry(QtCore.QRect(757, 407, 42, 42))
        self.c149.setText("")
        self.c149.setScaledContents(True)
        self.c149.setObjectName("c149")
        self.c104 = Chess(self.centralwidget)
        self.c104.setGeometry(QtCore.QRect(407, 307, 42, 42))
        self.c104.setText("")
        self.c104.setScaledContents(True)
        self.c104.setObjectName("c104")
        self.c94 = Chess(self.centralwidget)
        self.c94.setGeometry(QtCore.QRect(857, 257, 42, 42))
        self.c94.setText("")
        self.c94.setScaledContents(True)
        self.c94.setObjectName("c94")
        self.c140 = Chess(self.centralwidget)
        self.c140.setGeometry(QtCore.QRect(307, 407, 42, 42))
        self.c140.setText("")
        self.c140.setScaledContents(True)
        self.c140.setObjectName("c140")
        self.c137 = Chess(self.centralwidget)
        self.c137.setGeometry(QtCore.QRect(157, 407, 42, 42))
        self.c137.setText("")
        self.c137.setScaledContents(True)
        self.c137.setObjectName("c137")
        self.c114 = Chess(self.centralwidget)
        self.c114.setGeometry(QtCore.QRect(907, 307, 42, 42))
        self.c114.setText("")
        self.c114.setScaledContents(True)
        self.c114.setObjectName("c114")
        self.c106 = Chess(self.centralwidget)
        self.c106.setGeometry(QtCore.QRect(507, 307, 42, 42))
        self.c106.setText("")
        self.c106.setScaledContents(True)
        self.c106.setObjectName("c106")
        self.c93 = Chess(self.centralwidget)
        self.c93.setGeometry(QtCore.QRect(807, 257, 42, 42))
        self.c93.setText("")
        self.c93.setScaledContents(True)
        self.c93.setObjectName("c93")
        self.c77 = Chess(self.centralwidget)
        self.c77.setGeometry(QtCore.QRect(7, 257, 42, 42))
        self.c77.setText("")
        self.c77.setScaledContents(True)
        self.c77.setObjectName("c77")
        self.c144 = Chess(self.centralwidget)
        self.c144.setGeometry(QtCore.QRect(507, 407, 42, 42))
        self.c144.setText("")
        self.c144.setScaledContents(True)
        self.c144.setObjectName("c144")
        self.c135 = Chess(self.centralwidget)
        self.c135.setGeometry(QtCore.QRect(57, 407, 42, 42))
        self.c135.setText("")
        self.c135.setScaledContents(True)
        self.c135.setObjectName("c135")
        self.c138 = Chess(self.centralwidget)
        self.c138.setGeometry(QtCore.QRect(207, 407, 42, 42))
        self.c138.setText("")
        self.c138.setScaledContents(True)
        self.c138.setObjectName("c138")
        self.c118 = Chess(self.centralwidget)
        self.c118.setGeometry(QtCore.QRect(157, 357, 42, 42))
        self.c118.setText("")
        self.c118.setScaledContents(True)
        self.c118.setObjectName("c118")
        self.c102 = Chess(self.centralwidget)
        self.c102.setGeometry(QtCore.QRect(307, 307, 42, 42))
        self.c102.setText("")
        self.c102.setScaledContents(True)
        self.c102.setObjectName("c102")
        self.c129 = Chess(self.centralwidget)
        self.c129.setGeometry(QtCore.QRect(707, 357, 42, 42))
        self.c129.setText("")
        self.c129.setScaledContents(True)
        self.c129.setObjectName("c129")
        self.c78 = Chess(self.centralwidget)
        self.c78.setGeometry(QtCore.QRect(57, 257, 42, 42))
        self.c78.setText("")
        self.c78.setScaledContents(True)
        self.c78.setObjectName("c78")
        self.c83 = Chess(self.centralwidget)
        self.c83.setGeometry(QtCore.QRect(307, 257, 42, 42))
        self.c83.setText("")
        self.c83.setScaledContents(True)
        self.c83.setObjectName("c83")
        self.c132 = Chess(self.centralwidget)
        self.c132.setGeometry(QtCore.QRect(857, 357, 42, 42))
        self.c132.setText("")
        self.c132.setScaledContents(True)
        self.c132.setObjectName("c132")
        self.c96 = Chess(self.centralwidget)
        self.c96.setGeometry(QtCore.QRect(7, 307, 42, 42))
        self.c96.setText("")
        self.c96.setScaledContents(True)
        self.c96.setObjectName("c96")
        self.c107 = Chess(self.centralwidget)
        self.c107.setGeometry(QtCore.QRect(557, 307, 42, 42))
        self.c107.setText("")
        self.c107.setScaledContents(True)
        self.c107.setObjectName("c107")
        self.c146 = Chess(self.centralwidget)
        self.c146.setGeometry(QtCore.QRect(607, 407, 42, 42))
        self.c146.setText("")
        self.c146.setScaledContents(True)
        self.c146.setObjectName("c146")
        self.c79 = Chess(self.centralwidget)
        self.c79.setGeometry(QtCore.QRect(107, 257, 42, 42))
        self.c79.setText("")
        self.c79.setScaledContents(True)
        self.c79.setObjectName("c79")
        self.c100 = Chess(self.centralwidget)
        self.c100.setGeometry(QtCore.QRect(207, 307, 42, 42))
        self.c100.setText("")
        self.c100.setScaledContents(True)
        self.c100.setObjectName("c100")
        self.c85 = Chess(self.centralwidget)
        self.c85.setGeometry(QtCore.QRect(407, 257, 42, 42))
        self.c85.setText("")
        self.c85.setScaledContents(True)
        self.c85.setObjectName("c85")
        self.c87 = Chess(self.centralwidget)
        self.c87.setGeometry(QtCore.QRect(507, 257, 42, 42))
        self.c87.setText("")
        self.c87.setScaledContents(True)
        self.c87.setObjectName("c87")
        self.c119 = Chess(self.centralwidget)
        self.c119.setGeometry(QtCore.QRect(207, 357, 42, 42))
        self.c119.setText("")
        self.c119.setScaledContents(True)
        self.c119.setObjectName("c119")
        self.c120 = Chess(self.centralwidget)
        self.c120.setGeometry(QtCore.QRect(257, 357, 42, 42))
        self.c120.setText("")
        self.c120.setScaledContents(True)
        self.c120.setObjectName("c120")
        self.c123 = Chess(self.centralwidget)
        self.c123.setGeometry(QtCore.QRect(407, 357, 42, 42))
        self.c123.setText("")
        self.c123.setScaledContents(True)
        self.c123.setObjectName("c123")
        self.c121 = Chess(self.centralwidget)
        self.c121.setGeometry(QtCore.QRect(307, 357, 42, 42))
        self.c121.setText("")
        self.c121.setScaledContents(True)
        self.c121.setObjectName("c121")
        self.c86 = Chess(self.centralwidget)
        self.c86.setGeometry(QtCore.QRect(457, 257, 42, 42))
        self.c86.setText("")
        self.c86.setScaledContents(True)
        self.c86.setObjectName("c86")
        self.c147 = Chess(self.centralwidget)
        self.c147.setGeometry(QtCore.QRect(657, 407, 42, 42))
        self.c147.setText("")
        self.c147.setScaledContents(True)
        self.c147.setObjectName("c147")
        self.c130 = Chess(self.centralwidget)
        self.c130.setGeometry(QtCore.QRect(757, 357, 42, 42))
        self.c130.setText("")
        self.c130.setScaledContents(True)
        self.c130.setObjectName("c130")
        self.c122 = Chess(self.centralwidget)
        self.c122.setGeometry(QtCore.QRect(357, 357, 42, 42))
        self.c122.setText("")
        self.c122.setScaledContents(True)
        self.c122.setObjectName("c122")
        self.c148 = Chess(self.centralwidget)
        self.c148.setGeometry(QtCore.QRect(707, 407, 42, 42))
        self.c148.setText("")
        self.c148.setScaledContents(True)
        self.c148.setObjectName("c148")
        self.c105 = Chess(self.centralwidget)
        self.c105.setGeometry(QtCore.QRect(457, 307, 42, 42))
        self.c105.setText("")
        self.c105.setScaledContents(True)
        self.c105.setObjectName("c105")
        self.c152 = Chess(self.centralwidget)
        self.c152.setGeometry(QtCore.QRect(907, 407, 42, 42))
        self.c152.setText("")
        self.c152.setScaledContents(True)
        self.c152.setObjectName("c152")
        self.c103 = Chess(self.centralwidget)
        self.c103.setGeometry(QtCore.QRect(357, 307, 42, 42))
        self.c103.setText("")
        self.c103.setScaledContents(True)
        self.c103.setObjectName("c103")
        self.c240 = Chess(self.centralwidget)
        self.c240.setGeometry(QtCore.QRect(557, 657, 42, 42))
        self.c240.setText("")
        self.c240.setScaledContents(True)
        self.c240.setObjectName("c240")
        self.c271 = Chess(self.centralwidget)
        self.c271.setGeometry(QtCore.QRect(207, 757, 42, 42))
        self.c271.setText("")
        self.c271.setScaledContents(True)
        self.c271.setObjectName("c271")
        self.c161 = Chess(self.centralwidget)
        self.c161.setGeometry(QtCore.QRect(407, 457, 42, 42))
        self.c161.setText("")
        self.c161.setScaledContents(True)
        self.c161.setObjectName("c161")
        self.c196 = Chess(self.centralwidget)
        self.c196.setGeometry(QtCore.QRect(257, 557, 42, 42))
        self.c196.setText("")
        self.c196.setScaledContents(True)
        self.c196.setObjectName("c196")
        self.c291 = Chess(self.centralwidget)
        self.c291.setGeometry(QtCore.QRect(257, 807, 42, 42))
        self.c291.setText("")
        self.c291.setScaledContents(True)
        self.c291.setObjectName("c291")
        self.c183 = Chess(self.centralwidget)
        self.c183.setGeometry(QtCore.QRect(557, 507, 42, 42))
        self.c183.setText("")
        self.c183.setScaledContents(True)
        self.c183.setObjectName("c183")
        self.c186 = Chess(self.centralwidget)
        self.c186.setGeometry(QtCore.QRect(707, 507, 42, 42))
        self.c186.setText("")
        self.c186.setScaledContents(True)
        self.c186.setObjectName("c186")
        self.c278 = Chess(self.centralwidget)
        self.c278.setGeometry(QtCore.QRect(557, 757, 42, 42))
        self.c278.setText("")
        self.c278.setScaledContents(True)
        self.c278.setObjectName("c278")
        self.c294 = Chess(self.centralwidget)
        self.c294.setGeometry(QtCore.QRect(407, 807, 42, 42))
        self.c294.setText("")
        self.c294.setScaledContents(True)
        self.c294.setObjectName("c294")
        self.c221 = Chess(self.centralwidget)
        self.c221.setGeometry(QtCore.QRect(557, 607, 42, 42))
        self.c221.setText("")
        self.c221.setScaledContents(True)
        self.c221.setObjectName("c221")
        self.c226 = Chess(self.centralwidget)
        self.c226.setGeometry(QtCore.QRect(807, 607, 42, 42))
        self.c226.setText("")
        self.c226.setScaledContents(True)
        self.c226.setObjectName("c226")
        self.c284 = Chess(self.centralwidget)
        self.c284.setGeometry(QtCore.QRect(857, 757, 42, 42))
        self.c284.setText("")
        self.c284.setScaledContents(True)
        self.c284.setObjectName("c284")
        self.c172 = Chess(self.centralwidget)
        self.c172.setGeometry(QtCore.QRect(7, 507, 42, 42))
        self.c172.setText("")
        self.c172.setScaledContents(True)
        self.c172.setObjectName("c172")
        self.c287 = Chess(self.centralwidget)
        self.c287.setGeometry(QtCore.QRect(57, 807, 42, 42))
        self.c287.setText("")
        self.c287.setScaledContents(True)
        self.c287.setObjectName("c287")
        self.c227 = Chess(self.centralwidget)
        self.c227.setGeometry(QtCore.QRect(857, 607, 42, 42))
        self.c227.setText("")
        self.c227.setScaledContents(True)
        self.c227.setObjectName("c227")
        self.c216 = Chess(self.centralwidget)
        self.c216.setGeometry(QtCore.QRect(307, 607, 42, 42))
        self.c216.setText("")
        self.c216.setScaledContents(True)
        self.c216.setObjectName("c216")
        self.c195 = Chess(self.centralwidget)
        self.c195.setGeometry(QtCore.QRect(207, 557, 42, 42))
        self.c195.setText("")
        self.c195.setScaledContents(True)
        self.c195.setObjectName("c195")
        self.c218 = Chess(self.centralwidget)
        self.c218.setGeometry(QtCore.QRect(407, 607, 42, 42))
        self.c218.setText("")
        self.c218.setScaledContents(True)
        self.c218.setObjectName("c218")
        self.c199 = Chess(self.centralwidget)
        self.c199.setGeometry(QtCore.QRect(407, 557, 42, 42))
        self.c199.setText("")
        self.c199.setScaledContents(True)
        self.c199.setObjectName("c199")
        self.c262 = Chess(self.centralwidget)
        self.c262.setGeometry(QtCore.QRect(707, 707, 42, 42))
        self.c262.setText("")
        self.c262.setScaledContents(True)
        self.c262.setObjectName("c262")
        self.c173 = Chess(self.centralwidget)
        self.c173.setGeometry(QtCore.QRect(57, 507, 42, 42))
        self.c173.setText("")
        self.c173.setScaledContents(True)
        self.c173.setObjectName("c173")
        self.c213 = Chess(self.centralwidget)
        self.c213.setGeometry(QtCore.QRect(157, 607, 42, 42))
        self.c213.setText("")
        self.c213.setScaledContents(True)
        self.c213.setObjectName("c213")
        self.c189 = Chess(self.centralwidget)
        self.c189.setGeometry(QtCore.QRect(857, 507, 42, 42))
        self.c189.setText("")
        self.c189.setScaledContents(True)
        self.c189.setObjectName("c189")
        self.c190 = Chess(self.centralwidget)
        self.c190.setGeometry(QtCore.QRect(907, 507, 42, 42))
        self.c190.setText("")
        self.c190.setScaledContents(True)
        self.c190.setObjectName("c190")
        self.c261 = Chess(self.centralwidget)
        self.c261.setGeometry(QtCore.QRect(657, 707, 42, 42))
        self.c261.setText("")
        self.c261.setScaledContents(True)
        self.c261.setObjectName("c261")
        self.c249 = Chess(self.centralwidget)
        self.c249.setGeometry(QtCore.QRect(57, 707, 42, 42))
        self.c249.setText("")
        self.c249.setScaledContents(True)
        self.c249.setObjectName("c249")
        self.c233 = Chess(self.centralwidget)
        self.c233.setGeometry(QtCore.QRect(207, 657, 42, 42))
        self.c233.setText("")
        self.c233.setScaledContents(True)
        self.c233.setObjectName("c233")
        self.c171 = Chess(self.centralwidget)
        self.c171.setGeometry(QtCore.QRect(907, 457, 42, 42))
        self.c171.setText("")
        self.c171.setScaledContents(True)
        self.c171.setObjectName("c171")
        self.c201 = Chess(self.centralwidget)
        self.c201.setGeometry(QtCore.QRect(507, 557, 42, 42))
        self.c201.setText("")
        self.c201.setScaledContents(True)
        self.c201.setObjectName("c201")
        self.c301 = Chess(self.centralwidget)
        self.c301.setGeometry(QtCore.QRect(757, 807, 42, 42))
        self.c301.setText("")
        self.c301.setScaledContents(True)
        self.c301.setObjectName("c301")
        self.c185 = Chess(self.centralwidget)
        self.c185.setGeometry(QtCore.QRect(657, 507, 42, 42))
        self.c185.setText("")
        self.c185.setScaledContents(True)
        self.c185.setObjectName("c185")
        self.c304 = Chess(self.centralwidget)
        self.c304.setGeometry(QtCore.QRect(907, 807, 42, 42))
        self.c304.setText("")
        self.c304.setScaledContents(True)
        self.c304.setObjectName("c304")
        self.c182 = Chess(self.centralwidget)
        self.c182.setGeometry(QtCore.QRect(507, 507, 42, 42))
        self.c182.setText("")
        self.c182.setScaledContents(True)
        self.c182.setObjectName("c182")
        self.c263 = Chess(self.centralwidget)
        self.c263.setGeometry(QtCore.QRect(757, 707, 42, 42))
        self.c263.setText("")
        self.c263.setScaledContents(True)
        self.c263.setObjectName("c263")
        self.c168 = Chess(self.centralwidget)
        self.c168.setGeometry(QtCore.QRect(757, 457, 42, 42))
        self.c168.setText("")
        self.c168.setScaledContents(True)
        self.c168.setObjectName("c168")
        self.c235 = Chess(self.centralwidget)
        self.c235.setGeometry(QtCore.QRect(307, 657, 42, 42))
        self.c235.setText("")
        self.c235.setScaledContents(True)
        self.c235.setObjectName("c235")
        self.c192 = Chess(self.centralwidget)
        self.c192.setGeometry(QtCore.QRect(57, 557, 42, 42))
        self.c192.setText("")
        self.c192.setScaledContents(True)
        self.c192.setObjectName("c192")
        self.c297 = Chess(self.centralwidget)
        self.c297.setGeometry(QtCore.QRect(557, 807, 42, 42))
        self.c297.setText("")
        self.c297.setScaledContents(True)
        self.c297.setObjectName("c297")
        self.c215 = Chess(self.centralwidget)
        self.c215.setGeometry(QtCore.QRect(257, 607, 42, 42))
        self.c215.setText("")
        self.c215.setScaledContents(True)
        self.c215.setObjectName("c215")
        self.c205 = Chess(self.centralwidget)
        self.c205.setGeometry(QtCore.QRect(707, 557, 42, 42))
        self.c205.setText("")
        self.c205.setScaledContents(True)
        self.c205.setObjectName("c205")
        self.c209 = Chess(self.centralwidget)
        self.c209.setGeometry(QtCore.QRect(907, 557, 42, 42))
        self.c209.setText("")
        self.c209.setScaledContents(True)
        self.c209.setObjectName("c209")
        self.c212 = Chess(self.centralwidget)
        self.c212.setGeometry(QtCore.QRect(107, 607, 42, 42))
        self.c212.setText("")
        self.c212.setScaledContents(True)
        self.c212.setObjectName("c212")
        self.c298 = Chess(self.centralwidget)
        self.c298.setGeometry(QtCore.QRect(607, 807, 42, 42))
        self.c298.setText("")
        self.c298.setScaledContents(True)
        self.c298.setObjectName("c298")
        self.c274 = Chess(self.centralwidget)
        self.c274.setGeometry(QtCore.QRect(357, 757, 42, 42))
        self.c274.setText("")
        self.c274.setScaledContents(True)
        self.c274.setObjectName("c274")
        self.c266 = Chess(self.centralwidget)
        self.c266.setGeometry(QtCore.QRect(907, 707, 42, 42))
        self.c266.setText("")
        self.c266.setScaledContents(True)
        self.c266.setObjectName("c266")
        self.c302 = Chess(self.centralwidget)
        self.c302.setGeometry(QtCore.QRect(807, 807, 42, 42))
        self.c302.setText("")
        self.c302.setScaledContents(True)
        self.c302.setObjectName("c302")
        self.c236 = Chess(self.centralwidget)
        self.c236.setGeometry(QtCore.QRect(357, 657, 42, 42))
        self.c236.setText("")
        self.c236.setScaledContents(True)
        self.c236.setObjectName("c236")
        self.c198 = Chess(self.centralwidget)
        self.c198.setGeometry(QtCore.QRect(357, 557, 42, 42))
        self.c198.setText("")
        self.c198.setScaledContents(True)
        self.c198.setObjectName("c198")
        self.c184 = Chess(self.centralwidget)
        self.c184.setGeometry(QtCore.QRect(607, 507, 42, 42))
        self.c184.setText("")
        self.c184.setScaledContents(True)
        self.c184.setObjectName("c184")
        self.c252 = Chess(self.centralwidget)
        self.c252.setGeometry(QtCore.QRect(207, 707, 42, 42))
        self.c252.setText("")
        self.c252.setScaledContents(True)
        self.c252.setObjectName("c252")
        self.c303 = Chess(self.centralwidget)
        self.c303.setGeometry(QtCore.QRect(857, 807, 42, 42))
        self.c303.setText("")
        self.c303.setScaledContents(True)
        self.c303.setObjectName("c303")
        self.c255 = Chess(self.centralwidget)
        self.c255.setGeometry(QtCore.QRect(357, 707, 42, 42))
        self.c255.setText("")
        self.c255.setScaledContents(True)
        self.c255.setObjectName("c255")
        self.c228 = Chess(self.centralwidget)
        self.c228.setGeometry(QtCore.QRect(907, 607, 42, 42))
        self.c228.setText("")
        self.c228.setScaledContents(True)
        self.c228.setObjectName("c228")
        self.c295 = Chess(self.centralwidget)
        self.c295.setGeometry(QtCore.QRect(457, 807, 42, 42))
        self.c295.setText("")
        self.c295.setScaledContents(True)
        self.c295.setObjectName("c295")
        self.c174 = Chess(self.centralwidget)
        self.c174.setGeometry(QtCore.QRect(107, 507, 42, 42))
        self.c174.setText("")
        self.c174.setScaledContents(True)
        self.c174.setObjectName("c174")
        self.c245 = Chess(self.centralwidget)
        self.c245.setGeometry(QtCore.QRect(807, 657, 42, 42))
        self.c245.setText("")
        self.c245.setScaledContents(True)
        self.c245.setObjectName("c245")
        self.c246 = Chess(self.centralwidget)
        self.c246.setGeometry(QtCore.QRect(857, 657, 42, 42))
        self.c246.setText("")
        self.c246.setScaledContents(True)
        self.c246.setObjectName("c246")
        self.c282 = Chess(self.centralwidget)
        self.c282.setGeometry(QtCore.QRect(757, 757, 42, 42))
        self.c282.setText("")
        self.c282.setScaledContents(True)
        self.c282.setObjectName("c282")
        self.c247 = Chess(self.centralwidget)
        self.c247.setGeometry(QtCore.QRect(907, 657, 42, 42))
        self.c247.setText("")
        self.c247.setScaledContents(True)
        self.c247.setObjectName("c247")
        self.c265 = Chess(self.centralwidget)
        self.c265.setGeometry(QtCore.QRect(857, 707, 42, 42))
        self.c265.setText("")
        self.c265.setScaledContents(True)
        self.c265.setObjectName("c265")
        self.c270 = Chess(self.centralwidget)
        self.c270.setGeometry(QtCore.QRect(157, 757, 42, 42))
        self.c270.setText("")
        self.c270.setScaledContents(True)
        self.c270.setObjectName("c270")
        self.c179 = Chess(self.centralwidget)
        self.c179.setGeometry(QtCore.QRect(357, 507, 42, 42))
        self.c179.setText("")
        self.c179.setScaledContents(True)
        self.c179.setObjectName("c179")
        self.c285 = Chess(self.centralwidget)
        self.c285.setGeometry(QtCore.QRect(907, 757, 42, 42))
        self.c285.setText("")
        self.c285.setScaledContents(True)
        self.c285.setObjectName("c285")
        self.c166 = Chess(self.centralwidget)
        self.c166.setGeometry(QtCore.QRect(657, 457, 42, 42))
        self.c166.setText("")
        self.c166.setScaledContents(True)
        self.c166.setObjectName("c166")
        self.c155 = Chess(self.centralwidget)
        self.c155.setGeometry(QtCore.QRect(107, 457, 42, 42))
        self.c155.setText("")
        self.c155.setScaledContents(True)
        self.c155.setObjectName("c155")
        self.c178 = Chess(self.centralwidget)
        self.c178.setGeometry(QtCore.QRect(307, 507, 42, 42))
        self.c178.setText("")
        self.c178.setScaledContents(True)
        self.c178.setObjectName("c178")
        self.c258 = Chess(self.centralwidget)
        self.c258.setGeometry(QtCore.QRect(507, 707, 42, 42))
        self.c258.setText("")
        self.c258.setScaledContents(True)
        self.c258.setObjectName("c258")
        self.c193 = Chess(self.centralwidget)
        self.c193.setGeometry(QtCore.QRect(107, 557, 42, 42))
        self.c193.setText("")
        self.c193.setScaledContents(True)
        self.c193.setObjectName("c193")
        self.c268 = Chess(self.centralwidget)
        self.c268.setGeometry(QtCore.QRect(57, 757, 42, 42))
        self.c268.setText("")
        self.c268.setScaledContents(True)
        self.c268.setObjectName("c268")
        self.c299 = Chess(self.centralwidget)
        self.c299.setGeometry(QtCore.QRect(657, 807, 42, 42))
        self.c299.setText("")
        self.c299.setScaledContents(True)
        self.c299.setObjectName("c299")
        self.c157 = Chess(self.centralwidget)
        self.c157.setGeometry(QtCore.QRect(207, 457, 42, 42))
        self.c157.setText("")
        self.c157.setScaledContents(True)
        self.c157.setObjectName("c157")
        self.c206 = Chess(self.centralwidget)
        self.c206.setGeometry(QtCore.QRect(757, 557, 42, 42))
        self.c206.setText("")
        self.c206.setScaledContents(True)
        self.c206.setObjectName("c206")
        self.c163 = Chess(self.centralwidget)
        self.c163.setGeometry(QtCore.QRect(507, 457, 42, 42))
        self.c163.setText("")
        self.c163.setScaledContents(True)
        self.c163.setObjectName("c163")
        self.c225 = Chess(self.centralwidget)
        self.c225.setGeometry(QtCore.QRect(757, 607, 42, 42))
        self.c225.setText("")
        self.c225.setScaledContents(True)
        self.c225.setObjectName("c225")
        self.c264 = Chess(self.centralwidget)
        self.c264.setGeometry(QtCore.QRect(807, 707, 42, 42))
        self.c264.setText("")
        self.c264.setScaledContents(True)
        self.c264.setObjectName("c264")
        self.c156 = Chess(self.centralwidget)
        self.c156.setGeometry(QtCore.QRect(157, 457, 42, 42))
        self.c156.setText("")
        self.c156.setScaledContents(True)
        self.c156.setObjectName("c156")
        self.c244 = Chess(self.centralwidget)
        self.c244.setGeometry(QtCore.QRect(757, 657, 42, 42))
        self.c244.setText("")
        self.c244.setScaledContents(True)
        self.c244.setObjectName("c244")
        self.c200 = Chess(self.centralwidget)
        self.c200.setGeometry(QtCore.QRect(457, 557, 42, 42))
        self.c200.setText("")
        self.c200.setScaledContents(True)
        self.c200.setObjectName("c200")
        self.c181 = Chess(self.centralwidget)
        self.c181.setGeometry(QtCore.QRect(457, 507, 42, 42))
        self.c181.setText("")
        self.c181.setScaledContents(True)
        self.c181.setObjectName("c181")
        self.c160 = Chess(self.centralwidget)
        self.c160.setGeometry(QtCore.QRect(357, 457, 42, 42))
        self.c160.setText("")
        self.c160.setScaledContents(True)
        self.c160.setObjectName("c160")
        self.c191 = Chess(self.centralwidget)
        self.c191.setGeometry(QtCore.QRect(7, 557, 42, 42))
        self.c191.setText("")
        self.c191.setScaledContents(True)
        self.c191.setObjectName("c191")
        self.c254 = Chess(self.centralwidget)
        self.c254.setGeometry(QtCore.QRect(307, 707, 42, 42))
        self.c254.setText("")
        self.c254.setScaledContents(True)
        self.c254.setObjectName("c254")
        self.c230 = Chess(self.centralwidget)
        self.c230.setGeometry(QtCore.QRect(57, 657, 42, 42))
        self.c230.setText("")
        self.c230.setScaledContents(True)
        self.c230.setObjectName("c230")
        self.c232 = Chess(self.centralwidget)
        self.c232.setGeometry(QtCore.QRect(157, 657, 42, 42))
        self.c232.setText("")
        self.c232.setScaledContents(True)
        self.c232.setObjectName("c232")
        self.c279 = Chess(self.centralwidget)
        self.c279.setGeometry(QtCore.QRect(607, 757, 42, 42))
        self.c279.setText("")
        self.c279.setScaledContents(True)
        self.c279.setObjectName("c279")
        self.c169 = Chess(self.centralwidget)
        self.c169.setGeometry(QtCore.QRect(807, 457, 42, 42))
        self.c169.setText("")
        self.c169.setScaledContents(True)
        self.c169.setObjectName("c169")
        self.c275 = Chess(self.centralwidget)
        self.c275.setGeometry(QtCore.QRect(407, 757, 42, 42))
        self.c275.setText("")
        self.c275.setScaledContents(True)
        self.c275.setObjectName("c275")
        self.c242 = Chess(self.centralwidget)
        self.c242.setGeometry(QtCore.QRect(657, 657, 42, 42))
        self.c242.setText("")
        self.c242.setScaledContents(True)
        self.c242.setObjectName("c242")
        self.c256 = Chess(self.centralwidget)
        self.c256.setGeometry(QtCore.QRect(407, 707, 42, 42))
        self.c256.setText("")
        self.c256.setScaledContents(True)
        self.c256.setObjectName("c256")
        self.c300 = Chess(self.centralwidget)
        self.c300.setGeometry(QtCore.QRect(707, 807, 42, 42))
        self.c300.setText("")
        self.c300.setScaledContents(True)
        self.c300.setObjectName("c300")
        self.c281 = Chess(self.centralwidget)
        self.c281.setGeometry(QtCore.QRect(707, 757, 42, 42))
        self.c281.setText("")
        self.c281.setScaledContents(True)
        self.c281.setObjectName("c281")
        self.c202 = Chess(self.centralwidget)
        self.c202.setGeometry(QtCore.QRect(557, 557, 42, 42))
        self.c202.setText("")
        self.c202.setScaledContents(True)
        self.c202.setObjectName("c202")
        self.c259 = Chess(self.centralwidget)
        self.c259.setGeometry(QtCore.QRect(557, 707, 42, 42))
        self.c259.setText("")
        self.c259.setScaledContents(True)
        self.c259.setObjectName("c259")
        self.c293 = Chess(self.centralwidget)
        self.c293.setGeometry(QtCore.QRect(357, 807, 42, 42))
        self.c293.setText("")
        self.c293.setScaledContents(True)
        self.c293.setObjectName("c293")
        self.c289 = Chess(self.centralwidget)
        self.c289.setGeometry(QtCore.QRect(157, 807, 42, 42))
        self.c289.setText("")
        self.c289.setScaledContents(True)
        self.c289.setObjectName("c289")
        self.c224 = Chess(self.centralwidget)
        self.c224.setGeometry(QtCore.QRect(707, 607, 42, 42))
        self.c224.setText("")
        self.c224.setScaledContents(True)
        self.c224.setObjectName("c224")
        self.c234 = Chess(self.centralwidget)
        self.c234.setGeometry(QtCore.QRect(257, 657, 42, 42))
        self.c234.setText("")
        self.c234.setScaledContents(True)
        self.c234.setObjectName("c234")
        self.c194 = Chess(self.centralwidget)
        self.c194.setGeometry(QtCore.QRect(157, 557, 42, 42))
        self.c194.setText("")
        self.c194.setScaledContents(True)
        self.c194.setObjectName("c194")
        self.c280 = Chess(self.centralwidget)
        self.c280.setGeometry(QtCore.QRect(657, 757, 42, 42))
        self.c280.setText("")
        self.c280.setScaledContents(True)
        self.c280.setObjectName("c280")
        self.c260 = Chess(self.centralwidget)
        self.c260.setGeometry(QtCore.QRect(607, 707, 42, 42))
        self.c260.setText("")
        self.c260.setScaledContents(True)
        self.c260.setObjectName("c260")
        self.c211 = Chess(self.centralwidget)
        self.c211.setGeometry(QtCore.QRect(57, 607, 42, 42))
        self.c211.setText("")
        self.c211.setScaledContents(True)
        self.c211.setObjectName("c211")
        self.c159 = Chess(self.centralwidget)
        self.c159.setGeometry(QtCore.QRect(307, 457, 42, 42))
        self.c159.setText("")
        self.c159.setScaledContents(True)
        self.c159.setObjectName("c159")
        self.c203 = Chess(self.centralwidget)
        self.c203.setGeometry(QtCore.QRect(607, 557, 42, 42))
        self.c203.setText("")
        self.c203.setScaledContents(True)
        self.c203.setObjectName("c203")
        self.c273 = Chess(self.centralwidget)
        self.c273.setGeometry(QtCore.QRect(307, 757, 42, 42))
        self.c273.setText("")
        self.c273.setScaledContents(True)
        self.c273.setObjectName("c273")
        self.c277 = Chess(self.centralwidget)
        self.c277.setGeometry(QtCore.QRect(507, 757, 42, 42))
        self.c277.setText("")
        self.c277.setScaledContents(True)
        self.c277.setObjectName("c277")
        self.c167 = Chess(self.centralwidget)
        self.c167.setGeometry(QtCore.QRect(707, 457, 42, 42))
        self.c167.setText("")
        self.c167.setScaledContents(True)
        self.c167.setObjectName("c167")
        self.c180 = Chess(self.centralwidget)
        self.c180.setGeometry(QtCore.QRect(407, 507, 42, 42))
        self.c180.setText("")
        self.c180.setScaledContents(True)
        self.c180.setObjectName("c180")
        self.c283 = Chess(self.centralwidget)
        self.c283.setGeometry(QtCore.QRect(807, 757, 42, 42))
        self.c283.setText("")
        self.c283.setScaledContents(True)
        self.c283.setObjectName("c283")
        self.c250 = Chess(self.centralwidget)
        self.c250.setGeometry(QtCore.QRect(107, 707, 42, 42))
        self.c250.setText("")
        self.c250.setScaledContents(True)
        self.c250.setObjectName("c250")
        self.c220 = Chess(self.centralwidget)
        self.c220.setGeometry(QtCore.QRect(507, 607, 42, 42))
        self.c220.setText("")
        self.c220.setScaledContents(True)
        self.c220.setObjectName("c220")
        self.c164 = Chess(self.centralwidget)
        self.c164.setGeometry(QtCore.QRect(557, 457, 42, 42))
        self.c164.setText("")
        self.c164.setScaledContents(True)
        self.c164.setObjectName("c164")
        self.c248 = Chess(self.centralwidget)
        self.c248.setGeometry(QtCore.QRect(7, 707, 42, 42))
        self.c248.setText("")
        self.c248.setScaledContents(True)
        self.c248.setObjectName("c248")
        self.c292 = Chess(self.centralwidget)
        self.c292.setGeometry(QtCore.QRect(307, 807, 42, 42))
        self.c292.setText("")
        self.c292.setScaledContents(True)
        self.c292.setObjectName("c292")
        self.c267 = Chess(self.centralwidget)
        self.c267.setGeometry(QtCore.QRect(7, 757, 42, 42))
        self.c267.setText("")
        self.c267.setScaledContents(True)
        self.c267.setObjectName("c267")
        self.c237 = Chess(self.centralwidget)
        self.c237.setGeometry(QtCore.QRect(407, 657, 42, 42))
        self.c237.setText("")
        self.c237.setScaledContents(True)
        self.c237.setObjectName("c237")
        self.c207 = Chess(self.centralwidget)
        self.c207.setGeometry(QtCore.QRect(807, 557, 42, 42))
        self.c207.setText("")
        self.c207.setScaledContents(True)
        self.c207.setObjectName("c207")
        self.c238 = Chess(self.centralwidget)
        self.c238.setGeometry(QtCore.QRect(457, 657, 42, 42))
        self.c238.setText("")
        self.c238.setScaledContents(True)
        self.c238.setObjectName("c238")
        self.c214 = Chess(self.centralwidget)
        self.c214.setGeometry(QtCore.QRect(207, 607, 42, 42))
        self.c214.setText("")
        self.c214.setScaledContents(True)
        self.c214.setObjectName("c214")
        self.c208 = Chess(self.centralwidget)
        self.c208.setGeometry(QtCore.QRect(857, 557, 42, 42))
        self.c208.setText("")
        self.c208.setScaledContents(True)
        self.c208.setObjectName("c208")
        self.c162 = Chess(self.centralwidget)
        self.c162.setGeometry(QtCore.QRect(457, 457, 42, 42))
        self.c162.setText("")
        self.c162.setScaledContents(True)
        self.c162.setObjectName("c162")
        self.c222 = Chess(self.centralwidget)
        self.c222.setGeometry(QtCore.QRect(607, 607, 42, 42))
        self.c222.setText("")
        self.c222.setScaledContents(True)
        self.c222.setObjectName("c222")
        self.c219 = Chess(self.centralwidget)
        self.c219.setGeometry(QtCore.QRect(457, 607, 42, 42))
        self.c219.setText("")
        self.c219.setScaledContents(True)
        self.c219.setObjectName("c219")
        self.c257 = Chess(self.centralwidget)
        self.c257.setGeometry(QtCore.QRect(457, 707, 42, 42))
        self.c257.setText("")
        self.c257.setScaledContents(True)
        self.c257.setObjectName("c257")
        self.c170 = Chess(self.centralwidget)
        self.c170.setGeometry(QtCore.QRect(857, 457, 42, 42))
        self.c170.setText("")
        self.c170.setScaledContents(True)
        self.c170.setObjectName("c170")
        self.c269 = Chess(self.centralwidget)
        self.c269.setGeometry(QtCore.QRect(107, 757, 42, 42))
        self.c269.setText("")
        self.c269.setScaledContents(True)
        self.c269.setObjectName("c269")
        self.c175 = Chess(self.centralwidget)
        self.c175.setGeometry(QtCore.QRect(157, 507, 42, 42))
        self.c175.setText("")
        self.c175.setScaledContents(True)
        self.c175.setObjectName("c175")
        self.c176 = Chess(self.centralwidget)
        self.c176.setGeometry(QtCore.QRect(207, 507, 42, 42))
        self.c176.setText("")
        self.c176.setScaledContents(True)
        self.c176.setObjectName("c176")
        self.c239 = Chess(self.centralwidget)
        self.c239.setGeometry(QtCore.QRect(507, 657, 42, 42))
        self.c239.setText("")
        self.c239.setScaledContents(True)
        self.c239.setObjectName("c239")
        self.c153 = Chess(self.centralwidget)
        self.c153.setGeometry(QtCore.QRect(7, 457, 42, 42))
        self.c153.setText("")
        self.c153.setScaledContents(True)
        self.c153.setObjectName("c153")
        self.c158 = Chess(self.centralwidget)
        self.c158.setGeometry(QtCore.QRect(257, 457, 42, 42))
        self.c158.setText("")
        self.c158.setScaledContents(True)
        self.c158.setObjectName("c158")
        self.c243 = Chess(self.centralwidget)
        self.c243.setGeometry(QtCore.QRect(707, 657, 42, 42))
        self.c243.setText("")
        self.c243.setScaledContents(True)
        self.c243.setObjectName("c243")
        self.c288 = Chess(self.centralwidget)
        self.c288.setGeometry(QtCore.QRect(107, 807, 42, 42))
        self.c288.setText("")
        self.c288.setScaledContents(True)
        self.c288.setObjectName("c288")
        self.c217 = Chess(self.centralwidget)
        self.c217.setGeometry(QtCore.QRect(357, 607, 42, 42))
        self.c217.setText("")
        self.c217.setScaledContents(True)
        self.c217.setObjectName("c217")
        self.c253 = Chess(self.centralwidget)
        self.c253.setGeometry(QtCore.QRect(257, 707, 42, 42))
        self.c253.setText("")
        self.c253.setScaledContents(True)
        self.c253.setObjectName("c253")
        self.c204 = Chess(self.centralwidget)
        self.c204.setGeometry(QtCore.QRect(657, 557, 42, 42))
        self.c204.setText("")
        self.c204.setScaledContents(True)
        self.c204.setObjectName("c204")
        self.c296 = Chess(self.centralwidget)
        self.c296.setGeometry(QtCore.QRect(507, 807, 42, 42))
        self.c296.setText("")
        self.c296.setScaledContents(True)
        self.c296.setObjectName("c296")
        self.c223 = Chess(self.centralwidget)
        self.c223.setGeometry(QtCore.QRect(657, 607, 42, 42))
        self.c223.setText("")
        self.c223.setScaledContents(True)
        self.c223.setObjectName("c223")
        self.c188 = Chess(self.centralwidget)
        self.c188.setGeometry(QtCore.QRect(807, 507, 42, 42))
        self.c188.setText("")
        self.c188.setScaledContents(True)
        self.c188.setObjectName("c188")
        self.c177 = Chess(self.centralwidget)
        self.c177.setGeometry(QtCore.QRect(257, 507, 42, 42))
        self.c177.setText("")
        self.c177.setScaledContents(True)
        self.c177.setObjectName("c177")
        self.c154 = Chess(self.centralwidget)
        self.c154.setGeometry(QtCore.QRect(57, 457, 42, 42))
        self.c154.setText("")
        self.c154.setScaledContents(True)
        self.c154.setObjectName("c154")
        self.c229 = Chess(self.centralwidget)
        self.c229.setGeometry(QtCore.QRect(7, 657, 42, 42))
        self.c229.setText("")
        self.c229.setScaledContents(True)
        self.c229.setObjectName("c229")
        self.c210 = Chess(self.centralwidget)
        self.c210.setGeometry(QtCore.QRect(7, 607, 42, 42))
        self.c210.setText("")
        self.c210.setScaledContents(True)
        self.c210.setObjectName("c210")
        self.c290 = Chess(self.centralwidget)
        self.c290.setGeometry(QtCore.QRect(207, 807, 42, 42))
        self.c290.setText("")
        self.c290.setScaledContents(True)
        self.c290.setObjectName("c290")
        self.c286 = Chess(self.centralwidget)
        self.c286.setGeometry(QtCore.QRect(7, 807, 42, 42))
        self.c286.setText("")
        self.c286.setScaledContents(True)
        self.c286.setObjectName("c286")
        self.c187 = Chess(self.centralwidget)
        self.c187.setGeometry(QtCore.QRect(757, 507, 42, 42))
        self.c187.setText("")
        self.c187.setScaledContents(True)
        self.c187.setObjectName("c187")
        self.c231 = Chess(self.centralwidget)
        self.c231.setGeometry(QtCore.QRect(107, 657, 42, 42))
        self.c231.setText("")
        self.c231.setScaledContents(True)
        self.c231.setObjectName("c231")
        self.c197 = Chess(self.centralwidget)
        self.c197.setGeometry(QtCore.QRect(307, 557, 42, 42))
        self.c197.setText("")
        self.c197.setScaledContents(True)
        self.c197.setObjectName("c197")
        self.c272 = Chess(self.centralwidget)
        self.c272.setGeometry(QtCore.QRect(257, 757, 42, 42))
        self.c272.setText("")
        self.c272.setScaledContents(True)
        self.c272.setObjectName("c272")
        self.c251 = Chess(self.centralwidget)
        self.c251.setGeometry(QtCore.QRect(157, 707, 42, 42))
        self.c251.setText("")
        self.c251.setScaledContents(True)
        self.c251.setObjectName("c251")
        self.c276 = Chess(self.centralwidget)
        self.c276.setGeometry(QtCore.QRect(457, 757, 42, 42))
        self.c276.setText("")
        self.c276.setScaledContents(True)
        self.c276.setObjectName("c276")
        self.c241 = Chess(self.centralwidget)
        self.c241.setGeometry(QtCore.QRect(607, 657, 42, 42))
        self.c241.setText("")
        self.c241.setScaledContents(True)
        self.c241.setObjectName("c241")
        self.c165 = Chess(self.centralwidget)
        self.c165.setGeometry(QtCore.QRect(607, 457, 42, 42))
        self.c165.setText("")
        self.c165.setScaledContents(True)
        self.c165.setObjectName("c165")
        self.c310 = Chess(self.centralwidget)
        self.c310.setGeometry(QtCore.QRect(257, 857, 42, 42))
        self.c310.setText("")
        self.c310.setScaledContents(True)
        self.c310.setObjectName("c310")
        self.c311 = Chess(self.centralwidget)
        self.c311.setGeometry(QtCore.QRect(307, 857, 42, 42))
        self.c311.setText("")
        self.c311.setScaledContents(True)
        self.c311.setObjectName("c311")
        self.c347 = Chess(self.centralwidget)
        self.c347.setGeometry(QtCore.QRect(207, 957, 42, 42))
        self.c347.setText("")
        self.c347.setScaledContents(True)
        self.c347.setObjectName("c347")
        self.c319 = Chess(self.centralwidget)
        self.c319.setGeometry(QtCore.QRect(707, 857, 42, 42))
        self.c319.setText("")
        self.c319.setScaledContents(True)
        self.c319.setObjectName("c319")
        self.c338 = Chess(self.centralwidget)
        self.c338.setGeometry(QtCore.QRect(707, 907, 42, 42))
        self.c338.setText("")
        self.c338.setScaledContents(True)
        self.c338.setObjectName("c338")
        self.c353 = Chess(self.centralwidget)
        self.c353.setGeometry(QtCore.QRect(507, 957, 42, 42))
        self.c353.setText("")
        self.c353.setScaledContents(True)
        self.c353.setObjectName("c353")
        self.c328 = Chess(self.centralwidget)
        self.c328.setGeometry(QtCore.QRect(207, 907, 42, 42))
        self.c328.setText("")
        self.c328.setScaledContents(True)
        self.c328.setObjectName("c328")
        self.c320 = Chess(self.centralwidget)
        self.c320.setGeometry(QtCore.QRect(757, 857, 42, 42))
        self.c320.setText("")
        self.c320.setScaledContents(True)
        self.c320.setObjectName("c320")
        self.c358 = Chess(self.centralwidget)
        self.c358.setGeometry(QtCore.QRect(757, 957, 42, 42))
        self.c358.setText("")
        self.c358.setScaledContents(True)
        self.c358.setObjectName("c358")
        self.c326 = Chess(self.centralwidget)
        self.c326.setGeometry(QtCore.QRect(107, 907, 42, 42))
        self.c326.setText("")
        self.c326.setScaledContents(True)
        self.c326.setObjectName("c326")
        self.c325 = Chess(self.centralwidget)
        self.c325.setGeometry(QtCore.QRect(57, 907, 42, 42))
        self.c325.setText("")
        self.c325.setScaledContents(True)
        self.c325.setObjectName("c325")
        self.c361 = Chess(self.centralwidget)
        self.c361.setGeometry(QtCore.QRect(907, 957, 42, 42))
        self.c361.setText("")
        self.c361.setScaledContents(True)
        self.c361.setObjectName("c361")
        self.c316 = Chess(self.centralwidget)
        self.c316.setGeometry(QtCore.QRect(557, 857, 42, 42))
        self.c316.setText("")
        self.c316.setScaledContents(True)
        self.c316.setObjectName("c316")
        self.c307 = Chess(self.centralwidget)
        self.c307.setGeometry(QtCore.QRect(107, 857, 42, 42))
        self.c307.setText("")
        self.c307.setScaledContents(True)
        self.c307.setObjectName("c307")
        self.c323 = Chess(self.centralwidget)
        self.c323.setGeometry(QtCore.QRect(907, 857, 42, 42))
        self.c323.setText("")
        self.c323.setScaledContents(True)
        self.c323.setObjectName("c323")
        self.c331 = Chess(self.centralwidget)
        self.c331.setGeometry(QtCore.QRect(357, 907, 42, 42))
        self.c331.setText("")
        self.c331.setScaledContents(True)
        self.c331.setObjectName("c331")
        self.c308 = Chess(self.centralwidget)
        self.c308.setGeometry(QtCore.QRect(157, 857, 42, 42))
        self.c308.setText("")
        self.c308.setScaledContents(True)
        self.c308.setObjectName("c308")
        self.c334 = Chess(self.centralwidget)
        self.c334.setGeometry(QtCore.QRect(507, 907, 42, 42))
        self.c334.setText("")
        self.c334.setScaledContents(True)
        self.c334.setObjectName("c334")
        self.c356 = Chess(self.centralwidget)
        self.c356.setGeometry(QtCore.QRect(657, 957, 42, 42))
        self.c356.setText("")
        self.c356.setScaledContents(True)
        self.c356.setObjectName("c356")
        self.c336 = Chess(self.centralwidget)
        self.c336.setGeometry(QtCore.QRect(607, 907, 42, 42))
        self.c336.setText("")
        self.c336.setScaledContents(True)
        self.c336.setObjectName("c336")
        self.c343 = Chess(self.centralwidget)
        self.c343.setGeometry(QtCore.QRect(7, 957, 42, 42))
        self.c343.setText("")
        self.c343.setScaledContents(True)
        self.c343.setObjectName("c343")
        self.c333 = Chess(self.centralwidget)
        self.c333.setGeometry(QtCore.QRect(457, 907, 42, 42))
        self.c333.setText("")
        self.c333.setScaledContents(True)
        self.c333.setObjectName("c333")
        self.c344 = Chess(self.centralwidget)
        self.c344.setGeometry(QtCore.QRect(57, 957, 42, 42))
        self.c344.setText("")
        self.c344.setScaledContents(True)
        self.c344.setObjectName("c344")
        self.c337 = Chess(self.centralwidget)
        self.c337.setGeometry(QtCore.QRect(657, 907, 42, 42))
        self.c337.setText("")
        self.c337.setScaledContents(True)
        self.c337.setObjectName("c337")
        self.c341 = Chess(self.centralwidget)
        self.c341.setGeometry(QtCore.QRect(857, 907, 42, 42))
        self.c341.setText("")
        self.c341.setScaledContents(True)
        self.c341.setObjectName("c341")
        self.c313 = Chess(self.centralwidget)
        self.c313.setGeometry(QtCore.QRect(407, 857, 42, 42))
        self.c313.setText("")
        self.c313.setScaledContents(True)
        self.c313.setObjectName("c313")
        self.c322 = Chess(self.centralwidget)
        self.c322.setGeometry(QtCore.QRect(857, 857, 42, 42))
        self.c322.setText("")
        self.c322.setScaledContents(True)
        self.c322.setObjectName("c322")
        self.c321 = Chess(self.centralwidget)
        self.c321.setGeometry(QtCore.QRect(807, 857, 42, 42))
        self.c321.setText("")
        self.c321.setScaledContents(True)
        self.c321.setObjectName("c321")
        self.c359 = Chess(self.centralwidget)
        self.c359.setGeometry(QtCore.QRect(807, 957, 42, 42))
        self.c359.setText("")
        self.c359.setScaledContents(True)
        self.c359.setObjectName("c359")
        self.c342 = Chess(self.centralwidget)
        self.c342.setGeometry(QtCore.QRect(907, 907, 42, 42))
        self.c342.setText("")
        self.c342.setScaledContents(True)
        self.c342.setObjectName("c342")
        self.c309 = Chess(self.centralwidget)
        self.c309.setGeometry(QtCore.QRect(207, 857, 42, 42))
        self.c309.setText("")
        self.c309.setScaledContents(True)
        self.c309.setObjectName("c309")
        self.c340 = Chess(self.centralwidget)
        self.c340.setGeometry(QtCore.QRect(807, 907, 42, 42))
        self.c340.setText("")
        self.c340.setScaledContents(True)
        self.c340.setObjectName("c340")
        self.c324 = Chess(self.centralwidget)
        self.c324.setGeometry(QtCore.QRect(7, 907, 42, 42))
        self.c324.setText("")
        self.c324.setScaledContents(True)
        self.c324.setObjectName("c324")
        self.c351 = Chess(self.centralwidget)
        self.c351.setGeometry(QtCore.QRect(407, 957, 42, 42))
        self.c351.setText("")
        self.c351.setScaledContents(True)
        self.c351.setObjectName("c351")
        self.c345 = Chess(self.centralwidget)
        self.c345.setGeometry(QtCore.QRect(107, 957, 42, 42))
        self.c345.setText("")
        self.c345.setScaledContents(True)
        self.c345.setObjectName("c345")
        self.c352 = Chess(self.centralwidget)
        self.c352.setGeometry(QtCore.QRect(457, 957, 42, 42))
        self.c352.setText("")
        self.c352.setScaledContents(True)
        self.c352.setObjectName("c352")
        self.c327 = Chess(self.centralwidget)
        self.c327.setGeometry(QtCore.QRect(157, 907, 42, 42))
        self.c327.setText("")
        self.c327.setScaledContents(True)
        self.c327.setObjectName("c327")
        self.c318 = Chess(self.centralwidget)
        self.c318.setGeometry(QtCore.QRect(657, 857, 42, 42))
        self.c318.setText("")
        self.c318.setScaledContents(True)
        self.c318.setObjectName("c318")
        self.c357 = Chess(self.centralwidget)
        self.c357.setGeometry(QtCore.QRect(707, 957, 42, 42))
        self.c357.setText("")
        self.c357.setScaledContents(True)
        self.c357.setObjectName("c357")
        self.c354 = Chess(self.centralwidget)
        self.c354.setGeometry(QtCore.QRect(557, 957, 42, 42))
        self.c354.setText("")
        self.c354.setScaledContents(True)
        self.c354.setObjectName("c354")
        self.c360 = Chess(self.centralwidget)
        self.c360.setGeometry(QtCore.QRect(857, 957, 42, 42))
        self.c360.setText("")
        self.c360.setScaledContents(True)
        self.c360.setObjectName("c360")
        self.c349 = Chess(self.centralwidget)
        self.c349.setGeometry(QtCore.QRect(307, 957, 42, 42))
        self.c349.setText("")
        self.c349.setScaledContents(True)
        self.c349.setObjectName("c349")
        self.c350 = Chess(self.centralwidget)
        self.c350.setGeometry(QtCore.QRect(357, 957, 42, 42))
        self.c350.setText("")
        self.c350.setScaledContents(True)
        self.c350.setObjectName("c350")
        self.c315 = Chess(self.centralwidget)
        self.c315.setGeometry(QtCore.QRect(507, 857, 42, 42))
        self.c315.setText("")
        self.c315.setScaledContents(True)
        self.c315.setObjectName("c315")
        self.c312 = Chess(self.centralwidget)
        self.c312.setGeometry(QtCore.QRect(357, 857, 42, 42))
        self.c312.setText("")
        self.c312.setScaledContents(True)
        self.c312.setObjectName("c312")
        self.c355 = Chess(self.centralwidget)
        self.c355.setGeometry(QtCore.QRect(607, 957, 42, 42))
        self.c355.setText("")
        self.c355.setScaledContents(True)
        self.c355.setObjectName("c355")
        self.c332 = Chess(self.centralwidget)
        self.c332.setGeometry(QtCore.QRect(407, 907, 42, 42))
        self.c332.setText("")
        self.c332.setScaledContents(True)
        self.c332.setObjectName("c332")
        self.c329 = Chess(self.centralwidget)
        self.c329.setGeometry(QtCore.QRect(257, 907, 42, 42))
        self.c329.setText("")
        self.c329.setScaledContents(True)
        self.c329.setObjectName("c329")
        self.c339 = Chess(self.centralwidget)
        self.c339.setGeometry(QtCore.QRect(757, 907, 42, 42))
        self.c339.setText("")
        self.c339.setScaledContents(True)
        self.c339.setObjectName("c339")
        self.c348 = Chess(self.centralwidget)
        self.c348.setGeometry(QtCore.QRect(257, 957, 42, 42))
        self.c348.setText("")
        self.c348.setScaledContents(True)
        self.c348.setObjectName("c348")
        self.c330 = Chess(self.centralwidget)
        self.c330.setGeometry(QtCore.QRect(307, 907, 42, 42))
        self.c330.setText("")
        self.c330.setScaledContents(True)
        self.c330.setObjectName("c330")
        self.c314 = Chess(self.centralwidget)
        self.c314.setGeometry(QtCore.QRect(457, 857, 42, 42))
        self.c314.setText("")
        self.c314.setScaledContents(True)
        self.c314.setObjectName("c314")
        self.c317 = Chess(self.centralwidget)
        self.c317.setGeometry(QtCore.QRect(607, 857, 42, 42))
        self.c317.setText("")
        self.c317.setScaledContents(True)
        self.c317.setObjectName("c317")
        self.c306 = Chess(self.centralwidget)
        self.c306.setGeometry(QtCore.QRect(57, 857, 42, 42))
        self.c306.setText("")
        self.c306.setScaledContents(True)
        self.c306.setObjectName("c306")
        self.c346 = Chess(self.centralwidget)
        self.c346.setGeometry(QtCore.QRect(157, 957, 42, 42))
        self.c346.setText("")
        self.c346.setScaledContents(True)
        self.c346.setObjectName("c346")
        self.c335 = Chess(self.centralwidget)
        self.c335.setGeometry(QtCore.QRect(557, 907, 42, 42))
        self.c335.setText("")
        self.c335.setScaledContents(True)
        self.c335.setObjectName("c335")
        self.c305 = Chess(self.centralwidget)
        self.c305.setGeometry(QtCore.QRect(7, 857, 42, 42))
        self.c305.setText("")
        self.c305.setScaledContents(True)
        self.c305.setObjectName("c305")

        # Label
        self.currentLabel = QtWidgets.QLabel(self.centralwidget)
        self.currentLabel.setGeometry(QtCore.QRect(7, 57, 20, 20))
        self.currentLabel.setText("")
        self.currentLabel.setScaledContents(True)
        self.currentLabel.setObjectName('currentLabel')


    def setChessImg(self, deadStones, imgNum):
        stoneImg = QtGui.QPixmap()
        print(deadStones)
        print('imgNum:', imgNum)
        if imgNum == 0:
            stoneImg.load('')
        elif imgNum == 1:
            print('Image/black_stone.svg')
            stoneImg.load('Image/black_stone.svg')
        elif imgNum == 2:
            print('Image/white_stone.svg')
            stoneImg.load('Image/white_stone.svg')

        for x, y in deadStones:
            index = ((y*19) + x)
            print('id:', index)

            if index == 0:
                self.c01.setPixmap(stoneImg)
            elif index == 1:
                self.c02.setPixmap(stoneImg)
            elif index == 2:
                self.c03.setPixmap(stoneImg)
            elif index == 3:
                self.c04.setPixmap(stoneImg)
            elif index == 4:
                self.c05.setPixmap(stoneImg)
            elif index == 5:
                self.c06.setPixmap(stoneImg)
            elif index == 6:
                self.c07.setPixmap(stoneImg)
            elif index == 7:
                self.c08.setPixmap(stoneImg)
            elif index == 8:
                self.c09.setPixmap(stoneImg)
            elif index == 9:
                self.c10.setPixmap(stoneImg)
            elif index == 10:
                self.c11.setPixmap(stoneImg)
            elif index == 11:
                self.c12.setPixmap(stoneImg)
            elif index == 12:
                self.c13.setPixmap(stoneImg)
            elif index == 13:
                self.c14.setPixmap(stoneImg)
            elif index == 14:
                self.c15.setPixmap(stoneImg)
            elif index == 15:
                self.c16.setPixmap(stoneImg)
            elif index == 16:
                self.c17.setPixmap(stoneImg)
            elif index == 17:
                self.c18.setPixmap(stoneImg)
            elif index == 18:
                self.c19.setPixmap(stoneImg)
            elif index == 19:
                self.c20.setPixmap(stoneImg)
            elif index == 20:
                self.c21.setPixmap(stoneImg)
            elif index == 21:
                self.c22.setPixmap(stoneImg)
            elif index == 22:
                self.c23.setPixmap(stoneImg)
            elif index == 23:
                self.c24.setPixmap(stoneImg)
            elif index == 24:
                self.c25.setPixmap(stoneImg)
            elif index == 25:
                self.c26.setPixmap(stoneImg)
            elif index == 26:
                self.c27.setPixmap(stoneImg)
            elif index == 27:
                self.c28.setPixmap(stoneImg)
            elif index == 28:
                self.c29.setPixmap(stoneImg)
            elif index == 29:
                self.c30.setPixmap(stoneImg)
            elif index == 30:
                self.c31.setPixmap(stoneImg)
            elif index == 31:
                self.c32.setPixmap(stoneImg)
            elif index == 32:
                self.c33.setPixmap(stoneImg)
            elif index == 33:
                self.c34.setPixmap(stoneImg)
            elif index == 34:
                self.c35.setPixmap(stoneImg)
            elif index == 35:
                self.c36.setPixmap(stoneImg)
            elif index == 36:
                self.c37.setPixmap(stoneImg)
            elif index == 37:
                self.c38.setPixmap(stoneImg)
            elif index == 38:
                self.c39.setPixmap(stoneImg)
            elif index == 39:
                self.c40.setPixmap(stoneImg)
            elif index == 40:
                self.c41.setPixmap(stoneImg)
            elif index == 41:
                self.c42.setPixmap(stoneImg)
            elif index == 42:
                self.c43.setPixmap(stoneImg)
            elif index == 43:
                self.c44.setPixmap(stoneImg)
            elif index == 44:
                self.c45.setPixmap(stoneImg)
            elif index == 45:
                self.c46.setPixmap(stoneImg)
            elif index == 46:
                self.c47.setPixmap(stoneImg)
            elif index == 47:
                self.c48.setPixmap(stoneImg)
            elif index == 48:
                self.c49.setPixmap(stoneImg)
            elif index == 49:
                self.c50.setPixmap(stoneImg)
            elif index == 50:
                self.c51.setPixmap(stoneImg)
            elif index == 51:
                self.c52.setPixmap(stoneImg)
            elif index == 52:
                self.c53.setPixmap(stoneImg)
            elif index == 53:
                self.c54.setPixmap(stoneImg)
            elif index == 54:
                self.c55.setPixmap(stoneImg)
            elif index == 55:
                self.c56.setPixmap(stoneImg)
            elif index == 56:
                self.c57.setPixmap(stoneImg)
            elif index == 57:
                self.c58.setPixmap(stoneImg)
            elif index == 58:
                self.c59.setPixmap(stoneImg)
            elif index == 59:
                self.c60.setPixmap(stoneImg)
            elif index == 60:
                self.c61.setPixmap(stoneImg)
            elif index == 61:
                self.c62.setPixmap(stoneImg)
            elif index == 62:
                self.c63.setPixmap(stoneImg)
            elif index == 63:
                self.c64.setPixmap(stoneImg)
            elif index == 64:
                self.c65.setPixmap(stoneImg)
            elif index == 65:
                self.c66.setPixmap(stoneImg)
            elif index == 66:
                self.c67.setPixmap(stoneImg)
            elif index == 67:
                self.c68.setPixmap(stoneImg)
            elif index == 68:
                self.c69.setPixmap(stoneImg)
            elif index == 69:
                self.c70.setPixmap(stoneImg)
            elif index == 70:
                self.c71.setPixmap(stoneImg)
            elif index == 71:
                self.c72.setPixmap(stoneImg)
            elif index == 72:
                self.c73.setPixmap(stoneImg)
            elif index == 73:
                self.c74.setPixmap(stoneImg)
            elif index == 74:
                self.c75.setPixmap(stoneImg)
            elif index == 75:
                self.c76.setPixmap(stoneImg)
            elif index == 76:
                self.c77.setPixmap(stoneImg)
            elif index == 77:
                self.c78.setPixmap(stoneImg)
            elif index == 78:
                self.c79.setPixmap(stoneImg)
            elif index == 79:
                self.c80.setPixmap(stoneImg)
            elif index == 80:
                self.c81.setPixmap(stoneImg)
            elif index == 81:
                self.c82.setPixmap(stoneImg)
            elif index == 82:
                self.c83.setPixmap(stoneImg)
            elif index == 83:
                self.c84.setPixmap(stoneImg)
            elif index == 84:
                self.c85.setPixmap(stoneImg)
            elif index == 85:
                self.c86.setPixmap(stoneImg)
            elif index == 86:
                self.c87.setPixmap(stoneImg)
            elif index == 87:
                self.c88.setPixmap(stoneImg)
            elif index == 88:
                self.c89.setPixmap(stoneImg)
            elif index == 89:
                self.c90.setPixmap(stoneImg)
            elif index == 90:
                self.c91.setPixmap(stoneImg)
            elif index == 91:
                self.c92.setPixmap(stoneImg)
            elif index == 92:
                self.c93.setPixmap(stoneImg)
            elif index == 93:
                self.c94.setPixmap(stoneImg)
            elif index == 94:
                self.c95.setPixmap(stoneImg)
            elif index == 95:
                self.c96.setPixmap(stoneImg)
            elif index == 96:
                self.c97.setPixmap(stoneImg)
            elif index == 97:
                self.c98.setPixmap(stoneImg)
            elif index == 98:
                self.c99.setPixmap(stoneImg)
            elif index == 99:
                self.c100.setPixmap(stoneImg)
            elif index == 100:
                self.c101.setPixmap(stoneImg)
            elif index == 101:
                self.c102.setPixmap(stoneImg)
            elif index == 102:
                self.c103.setPixmap(stoneImg)
            elif index == 103:
                self.c104.setPixmap(stoneImg)
            elif index == 104:
                self.c105.setPixmap(stoneImg)
            elif index == 105:
                self.c106.setPixmap(stoneImg)
            elif index == 106:
                self.c107.setPixmap(stoneImg)
            elif index == 107:
                self.c108.setPixmap(stoneImg)
            elif index == 108:
                self.c109.setPixmap(stoneImg)
            elif index == 109:
                self.c110.setPixmap(stoneImg)
            elif index == 110:
                self.c111.setPixmap(stoneImg)
            elif index == 111:
                self.c112.setPixmap(stoneImg)
            elif index == 112:
                self.c113.setPixmap(stoneImg)
            elif index == 113:
                self.c114.setPixmap(stoneImg)
            elif index == 114:
                self.c115.setPixmap(stoneImg)
            elif index == 115:
                self.c116.setPixmap(stoneImg)
            elif index == 116:
                self.c117.setPixmap(stoneImg)
            elif index == 117:
                self.c118.setPixmap(stoneImg)
            elif index == 118:
                self.c119.setPixmap(stoneImg)
            elif index == 119:
                self.c120.setPixmap(stoneImg)
            elif index == 120:
                self.c121.setPixmap(stoneImg)
            elif index == 121:
                self.c122.setPixmap(stoneImg)
            elif index == 122:
                self.c123.setPixmap(stoneImg)
            elif index == 123:
                self.c124.setPixmap(stoneImg)
            elif index == 124:
                self.c125.setPixmap(stoneImg)
            elif index == 125:
                self.c126.setPixmap(stoneImg)
            elif index == 126:
                self.c127.setPixmap(stoneImg)
            elif index == 127:
                self.c128.setPixmap(stoneImg)
            elif index == 128:
                self.c129.setPixmap(stoneImg)
            elif index == 129:
                self.c130.setPixmap(stoneImg)
            elif index == 130:
                self.c131.setPixmap(stoneImg)
            elif index == 131:
                self.c132.setPixmap(stoneImg)
            elif index == 132:
                self.c133.setPixmap(stoneImg)
            elif index == 133:
                self.c134.setPixmap(stoneImg)
            elif index == 134:
                self.c135.setPixmap(stoneImg)
            elif index == 135:
                self.c136.setPixmap(stoneImg)
            elif index == 136:
                self.c137.setPixmap(stoneImg)
            elif index == 137:
                self.c138.setPixmap(stoneImg)
            elif index == 138:
                self.c139.setPixmap(stoneImg)
            elif index == 139:
                self.c140.setPixmap(stoneImg)
            elif index == 140:
                self.c141.setPixmap(stoneImg)
            elif index == 141:
                self.c142.setPixmap(stoneImg)
            elif index == 142:
                self.c143.setPixmap(stoneImg)
            elif index == 143:
                self.c144.setPixmap(stoneImg)
            elif index == 144:
                self.c145.setPixmap(stoneImg)
            elif index == 145:
                self.c146.setPixmap(stoneImg)
            elif index == 146:
                self.c147.setPixmap(stoneImg)
            elif index == 147:
                self.c148.setPixmap(stoneImg)
            elif index == 148:
                self.c149.setPixmap(stoneImg)
            elif index == 149:
                self.c150.setPixmap(stoneImg)
            elif index == 150:
                self.c151.setPixmap(stoneImg)
            elif index == 151:
                self.c152.setPixmap(stoneImg)
            elif index == 152:
                self.c153.setPixmap(stoneImg)
            elif index == 153:
                self.c154.setPixmap(stoneImg)
            elif index == 154:
                self.c155.setPixmap(stoneImg)
            elif index == 155:
                self.c156.setPixmap(stoneImg)
            elif index == 156:
                self.c157.setPixmap(stoneImg)
            elif index == 157:
                self.c158.setPixmap(stoneImg)
            elif index == 158:
                self.c159.setPixmap(stoneImg)
            elif index == 159:
                self.c160.setPixmap(stoneImg)
            elif index == 160:
                self.c161.setPixmap(stoneImg)
            elif index == 161:
                self.c162.setPixmap(stoneImg)
            elif index == 162:
                self.c163.setPixmap(stoneImg)
            elif index == 163:
                self.c164.setPixmap(stoneImg)
            elif index == 164:
                self.c165.setPixmap(stoneImg)
            elif index == 165:
                self.c166.setPixmap(stoneImg)
            elif index == 166:
                self.c167.setPixmap(stoneImg)
            elif index == 167:
                self.c168.setPixmap(stoneImg)
            elif index == 168:
                self.c169.setPixmap(stoneImg)
            elif index == 169:
                self.c170.setPixmap(stoneImg)
            elif index == 170:
                self.c171.setPixmap(stoneImg)
            elif index == 171:
                self.c172.setPixmap(stoneImg)
            elif index == 172:
                self.c173.setPixmap(stoneImg)
            elif index == 173:
                self.c174.setPixmap(stoneImg)
            elif index == 174:
                self.c175.setPixmap(stoneImg)
            elif index == 175:
                self.c176.setPixmap(stoneImg)
            elif index == 176:
                self.c177.setPixmap(stoneImg)
            elif index == 177:
                self.c178.setPixmap(stoneImg)
            elif index == 178:
                self.c179.setPixmap(stoneImg)
            elif index == 179:
                self.c180.setPixmap(stoneImg)
            elif index == 180:
                self.c181.setPixmap(stoneImg)
            elif index == 181:
                self.c182.setPixmap(stoneImg)
            elif index == 182:
                self.c183.setPixmap(stoneImg)
            elif index == 183:
                self.c184.setPixmap(stoneImg)
            elif index == 184:
                self.c185.setPixmap(stoneImg)
            elif index == 185:
                self.c186.setPixmap(stoneImg)
            elif index == 186:
                self.c187.setPixmap(stoneImg)
            elif index == 187:
                self.c188.setPixmap(stoneImg)
            elif index == 188:
                self.c189.setPixmap(stoneImg)
            elif index == 189:
                self.c190.setPixmap(stoneImg)
            elif index == 190:
                self.c191.setPixmap(stoneImg)
            elif index == 191:
                self.c192.setPixmap(stoneImg)
            elif index == 192:
                self.c193.setPixmap(stoneImg)
            elif index == 193:
                self.c194.setPixmap(stoneImg)
            elif index == 194:
                self.c195.setPixmap(stoneImg)
            elif index == 195:
                self.c196.setPixmap(stoneImg)
            elif index == 196:
                self.c197.setPixmap(stoneImg)
            elif index == 197:
                self.c198.setPixmap(stoneImg)
            elif index == 198:
                self.c199.setPixmap(stoneImg)
            elif index == 199:
                self.c200.setPixmap(stoneImg)
            elif index == 200:
                self.c201.setPixmap(stoneImg)
            elif index == 201:
                self.c202.setPixmap(stoneImg)
            elif index == 202:
                self.c203.setPixmap(stoneImg)
            elif index == 203:
                self.c204.setPixmap(stoneImg)
            elif index == 204:
                self.c205.setPixmap(stoneImg)
            elif index == 205:
                self.c206.setPixmap(stoneImg)
            elif index == 206:
                self.c207.setPixmap(stoneImg)
            elif index == 207:
                self.c208.setPixmap(stoneImg)
            elif index == 208:
                self.c209.setPixmap(stoneImg)
            elif index == 209:
                self.c210.setPixmap(stoneImg)
            elif index == 210:
                self.c211.setPixmap(stoneImg)
            elif index == 211:
                self.c212.setPixmap(stoneImg)
            elif index == 212:
                self.c213.setPixmap(stoneImg)
            elif index == 213:
                self.c214.setPixmap(stoneImg)
            elif index == 214:
                self.c215.setPixmap(stoneImg)
            elif index == 215:
                self.c216.setPixmap(stoneImg)
            elif index == 216:
                self.c217.setPixmap(stoneImg)
            elif index == 217:
                self.c218.setPixmap(stoneImg)
            elif index == 218:
                self.c219.setPixmap(stoneImg)
            elif index == 219:
                self.c220.setPixmap(stoneImg)
            elif index == 220:
                self.c221.setPixmap(stoneImg)
            elif index == 221:
                self.c222.setPixmap(stoneImg)
            elif index == 222:
                self.c223.setPixmap(stoneImg)
            elif index == 223:
                self.c224.setPixmap(stoneImg)
            elif index == 224:
                self.c225.setPixmap(stoneImg)
            elif index == 225:
                self.c226.setPixmap(stoneImg)
            elif index == 226:
                self.c227.setPixmap(stoneImg)
            elif index == 227:
                self.c228.setPixmap(stoneImg)
            elif index == 228:
                self.c229.setPixmap(stoneImg)
            elif index == 229:
                self.c230.setPixmap(stoneImg)
            elif index == 230:
                self.c231.setPixmap(stoneImg)
            elif index == 231:
                self.c232.setPixmap(stoneImg)
            elif index == 232:
                self.c233.setPixmap(stoneImg)
            elif index == 233:
                self.c234.setPixmap(stoneImg)
            elif index == 234:
                self.c235.setPixmap(stoneImg)
            elif index == 235:
                self.c236.setPixmap(stoneImg)
            elif index == 236:
                self.c237.setPixmap(stoneImg)
            elif index == 237:
                self.c238.setPixmap(stoneImg)
            elif index == 238:
                self.c239.setPixmap(stoneImg)
            elif index == 239:
                self.c240.setPixmap(stoneImg)
            elif index == 240:
                self.c241.setPixmap(stoneImg)
            elif index == 241:
                self.c242.setPixmap(stoneImg)
            elif index == 242:
                self.c243.setPixmap(stoneImg)
            elif index == 243:
                self.c244.setPixmap(stoneImg)
            elif index == 244:
                self.c245.setPixmap(stoneImg)
            elif index == 245:
                self.c246.setPixmap(stoneImg)
            elif index == 246:
                self.c247.setPixmap(stoneImg)
            elif index == 247:
                self.c248.setPixmap(stoneImg)
            elif index == 248:
                self.c249.setPixmap(stoneImg)
            elif index == 249:
                self.c250.setPixmap(stoneImg)
            elif index == 250:
                self.c251.setPixmap(stoneImg)
            elif index == 251:
                self.c252.setPixmap(stoneImg)
            elif index == 252:
                self.c253.setPixmap(stoneImg)
            elif index == 253:
                self.c254.setPixmap(stoneImg)
            elif index == 254:
                self.c255.setPixmap(stoneImg)
            elif index == 255:
                self.c256.setPixmap(stoneImg)
            elif index == 256:
                self.c257.setPixmap(stoneImg)
            elif index == 257:
                self.c258.setPixmap(stoneImg)
            elif index == 258:
                self.c259.setPixmap(stoneImg)
            elif index == 259:
                self.c260.setPixmap(stoneImg)
            elif index == 260:
                self.c261.setPixmap(stoneImg)
            elif index == 261:
                self.c262.setPixmap(stoneImg)
            elif index == 262:
                self.c263.setPixmap(stoneImg)
            elif index == 263:
                self.c264.setPixmap(stoneImg)
            elif index == 264:
                self.c265.setPixmap(stoneImg)
            elif index == 265:
                self.c266.setPixmap(stoneImg)
            elif index == 266:
                self.c267.setPixmap(stoneImg)
            elif index == 267:
                self.c268.setPixmap(stoneImg)
            elif index == 268:
                self.c269.setPixmap(stoneImg)
            elif index == 269:
                self.c270.setPixmap(stoneImg)
            elif index == 270:
                self.c271.setPixmap(stoneImg)
            elif index == 271:
                self.c272.setPixmap(stoneImg)
            elif index == 272:
                self.c273.setPixmap(stoneImg)
            elif index == 273:
                self.c274.setPixmap(stoneImg)
            elif index == 274:
                self.c275.setPixmap(stoneImg)
            elif index == 275:
                self.c276.setPixmap(stoneImg)
            elif index == 276:
                self.c277.setPixmap(stoneImg)
            elif index == 277:
                self.c278.setPixmap(stoneImg)
            elif index == 278:
                self.c279.setPixmap(stoneImg)
            elif index == 279:
                self.c280.setPixmap(stoneImg)
            elif index == 280:
                self.c281.setPixmap(stoneImg)
            elif index == 281:
                self.c282.setPixmap(stoneImg)
            elif index == 282:
                self.c283.setPixmap(stoneImg)
            elif index == 283:
                self.c284.setPixmap(stoneImg)
            elif index == 284:
                self.c285.setPixmap(stoneImg)
            elif index == 285:
                self.c286.setPixmap(stoneImg)
            elif index == 286:
                self.c287.setPixmap(stoneImg)
            elif index == 287:
                self.c288.setPixmap(stoneImg)
            elif index == 288:
                self.c289.setPixmap(stoneImg)
            elif index == 289:
                self.c290.setPixmap(stoneImg)
            elif index == 290:
                self.c291.setPixmap(stoneImg)
            elif index == 291:
                self.c292.setPixmap(stoneImg)
            elif index == 292:
                self.c293.setPixmap(stoneImg)
            elif index == 293:
                self.c294.setPixmap(stoneImg)
            elif index == 294:
                self.c295.setPixmap(stoneImg)
            elif index == 295:
                self.c296.setPixmap(stoneImg)
            elif index == 296:
                self.c297.setPixmap(stoneImg)
            elif index == 297:
                self.c298.setPixmap(stoneImg)
            elif index == 298:
                self.c299.setPixmap(stoneImg)
            elif index == 299:
                self.c300.setPixmap(stoneImg)
            elif index == 300:
                self.c301.setPixmap(stoneImg)
            elif index == 301:
                self.c302.setPixmap(stoneImg)
            elif index == 302:
                self.c303.setPixmap(stoneImg)
            elif index == 303:
                self.c304.setPixmap(stoneImg)
            elif index == 304:
                self.c305.setPixmap(stoneImg)
            elif index == 305:
                self.c306.setPixmap(stoneImg)
            elif index == 306:
                self.c307.setPixmap(stoneImg)
            elif index == 307:
                self.c308.setPixmap(stoneImg)
            elif index == 308:
                self.c309.setPixmap(stoneImg)
            elif index == 309:
                self.c310.setPixmap(stoneImg)
            elif index == 310:
                self.c311.setPixmap(stoneImg)
            elif index == 311:
                self.c312.setPixmap(stoneImg)
            elif index == 312:
                self.c313.setPixmap(stoneImg)
            elif index == 313:
                self.c314.setPixmap(stoneImg)
            elif index == 314:
                self.c315.setPixmap(stoneImg)
            elif index == 315:
                self.c316.setPixmap(stoneImg)
            elif index == 316:
                self.c317.setPixmap(stoneImg)
            elif index == 317:
                self.c318.setPixmap(stoneImg)
            elif index == 318:
                self.c319.setPixmap(stoneImg)
            elif index == 319:
                self.c320.setPixmap(stoneImg)
            elif index == 320:
                self.c321.setPixmap(stoneImg)
            elif index == 321:
                self.c322.setPixmap(stoneImg)
            elif index == 322:
                self.c323.setPixmap(stoneImg)
            elif index == 323:
                self.c324.setPixmap(stoneImg)
            elif index == 324:
                self.c325.setPixmap(stoneImg)
            elif index == 325:
                self.c326.setPixmap(stoneImg)
            elif index == 326:
                self.c327.setPixmap(stoneImg)
            elif index == 327:
                self.c328.setPixmap(stoneImg)
            elif index == 328:
                self.c329.setPixmap(stoneImg)
            elif index == 329:
                self.c330.setPixmap(stoneImg)
            elif index == 330:
                self.c331.setPixmap(stoneImg)
            elif index == 331:
                self.c332.setPixmap(stoneImg)
            elif index == 332:
                self.c333.setPixmap(stoneImg)
            elif index == 333:
                self.c334.setPixmap(stoneImg)
            elif index == 334:
                self.c335.setPixmap(stoneImg)
            elif index == 335:
                self.c336.setPixmap(stoneImg)
            elif index == 336:
                self.c337.setPixmap(stoneImg)
            elif index == 337:
                self.c338.setPixmap(stoneImg)
            elif index == 338:
                self.c339.setPixmap(stoneImg)
            elif index == 339:
                self.c340.setPixmap(stoneImg)
            elif index == 340:
                self.c341.setPixmap(stoneImg)
            elif index == 341:
                self.c342.setPixmap(stoneImg)
            elif index == 342:
                self.c343.setPixmap(stoneImg)
            elif index == 343:
                self.c344.setPixmap(stoneImg)
            elif index == 344:
                self.c345.setPixmap(stoneImg)
            elif index == 345:
                self.c346.setPixmap(stoneImg)
            elif index == 346:
                self.c347.setPixmap(stoneImg)
            elif index == 347:
                self.c348.setPixmap(stoneImg)
            elif index == 348:
                self.c349.setPixmap(stoneImg)
            elif index == 349:
                self.c350.setPixmap(stoneImg)
            elif index == 350:
                self.c351.setPixmap(stoneImg)
            elif index == 351:
                self.c352.setPixmap(stoneImg)
            elif index == 352:
                self.c353.setPixmap(stoneImg)
            elif index == 353:
                self.c354.setPixmap(stoneImg)
            elif index == 354:
                self.c355.setPixmap(stoneImg)
            elif index == 355:
                self.c356.setPixmap(stoneImg)
            elif index == 356:
                self.c357.setPixmap(stoneImg)
            elif index == 357:
                self.c358.setPixmap(stoneImg)
            elif index == 358:
                self.c359.setPixmap(stoneImg)
            elif index == 359:
                self.c360.setPixmap(stoneImg)
            elif index == 360:
                self.c361.setPixmap(stoneImg)


class Chess(QtWidgets.QLabel):
    def __init__(self, centralwidget):
        super(Chess, self).__init__(centralwidget)

        self.centralwidget = centralwidget
        self.recoveryStones = []

    def mousePressEvent(self, event):
        # Audio
        fullpath = QtCore.QDir.current().absoluteFilePath('Audio/Go Clicked.mp3')
        media = QtCore.QUrl.fromLocalFile(fullpath)
        content = QtMultimedia.QMediaContent(media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(content)

        if event.buttons() == QtCore.Qt.LeftButton:
            global chessNum
            global goBoard
            global MainWindow
            global blackPreviousBoard
            global whitePreviousBoard
            turns = get_turns()

            self.color = 1 if get_turns() % 2 == 0 else 2

            x = int((self.x()-7)/50)
            y = int((self.y()-57)/50)

            # Can't overwrite the stone
            if goBoard[y][x] == 0:
                currentBoard = copy.deepcopy(goBoard)
                goBoard[y][x] = self.color

                firstCheck = self.checkAroundState(x, y)

                # Check the stones around the current stones
                print('first check:', firstCheck)
                for i, j in firstCheck:
                    if goBoard[j][i] != self.color:
                        self.EatChess(initial_x=i, initial_y=j, Pass=True)

                # Check the current stones not dead, if dead, out of the current process
                test = self.EatChessSelf(initial_x=x, initial_y=y, Pass=True)
                if test == 'dead':
                    print('不允許自殺')
                    goBoard = copy.deepcopy(currentBoard)
                else:
                    self.EatChess()

                    if (self.color == 1 and goBoard == whitePreviousBoard and turns > 3) or (
                            self.color == 2 and goBoard == blackPreviousBoard and turns > 3):
                        print('不允許打劫！')
                        self.showBoard()
                        goBoard = copy.deepcopy(currentBoard)

                        print('要還原：', self.recoveryStones)

                        if self.color == 1:
                            MainWindow.setChessImg(self.recoveryStones, 2)
                        elif self.color == 2:
                            MainWindow.setChessImg(self.recoveryStones, 1)

                        self.recoveryStones.clear()

                    else:
                        self.showBoard()
                        turns += 1
                        print('Turns:', turns)
                        set_turns(turns)

                        self.player.play()

                        if self.color == 2:
                            blackPreviousBoard = copy.deepcopy(goBoard)
                            whiteStone = QtGui.QPixmap()
                            whiteStone.load('Image/white_stone.svg')
                            self.setPixmap(whiteStone)
                            Img = QtGui.QPixmap()
                            Img.load('Image/RedLabel.png')
                            MainWindow.currentLabel.setPixmap(Img)
                            MainWindow.currentLabel.move(self.x() + 11.5, self.y() + 11.5)
                        elif self.color == 1:
                            whitePreviousBoard = copy.deepcopy(goBoard)
                            blackStone = QtGui.QPixmap()
                            blackStone.load('Image/black_stone.svg')
                            self.setPixmap(blackStone)
                            Img = QtGui.QPixmap()
                            Img.load('Image/RedLabel.png')
                            MainWindow.currentLabel.setPixmap(Img)
                            MainWindow.currentLabel.move(self.x() + 12, self.y() + 12)


    def showBoard(self):
        for raw in range(len(goBoard)):
            print(goBoard[raw], '=', blackPreviousBoard[raw], '=', whitePreviousBoard[raw])

    def EatChess(self, initial_x=0, initial_y=0, Pass=False):
        passStones = []

        for x in range(initial_x, 19):
            for y in range(initial_y, 19):
                deadStones = []
                passStonesTemp = []
                aroundStonesStatusTotal = []

                if (x, y) in passStones or goBoard[y][x] == 0: continue

                aroundStonesStatusTotal = self.deepSearch(x, y, passStonesTemp, aroundStonesStatusTotal)

                # Finally Determine
                # totalStatus is coler
                # aroundStonesStatusTotla is position
                totalStatus = [goBoard[pos[1]][pos[0]] for pos in aroundStonesStatusTotal]

                # Black
                if goBoard[y][x] == 1:
                    if 0 not in totalStatus:
                        print(totalStatus)
                        deadStones.append((x, y))
                        for i, j in aroundStonesStatusTotal:
                            if goBoard[j][i] == 1:
                                passStonesTemp.append((i, j))
                                deadStones.append((i, j))

                        self.recoveryStones += deadStones
                        self.goBoardUpdate(deadStones)
                    else:
                        for pos in passStonesTemp:
                            passStones.append(pos)

                # White
                elif goBoard[y][x] == 2:
                    if 0 not in totalStatus:
                        print(totalStatus)

                        deadStones.append((x, y))
                        for i, j in aroundStonesStatusTotal:
                            if goBoard[j][i] == 2:
                                passStonesTemp.append((i, j))
                                deadStones.append((i, j))

                        self.recoveryStones += deadStones
                        self.goBoardUpdate(deadStones)

                    else:
                        for pos in passStonesTemp:
                            passStones.append(pos)

                if Pass:
                    break
            if Pass:
                break

    def EatChessSelf(self, initial_x=0, initial_y=0, Pass=False):
        passStones = []

        for x in range(initial_x, 19):
            for y in range(initial_y, 19):
                deadStones = []
                passStonesTemp = []
                aroundStonesStatusTotal = []

                if (x, y) in passStones or goBoard[y][x] == 0: continue

                aroundStonesStatusTotal = self.deepSearch(x, y, passStonesTemp, aroundStonesStatusTotal)

                # Finally Determine
                # totalStatus is coler
                # aroundStonesStatusTotla is position
                totalStatus = [goBoard[pos[1]][pos[0]] for pos in aroundStonesStatusTotal]

                # Black
                if goBoard[y][x] == 1:
                    if 0 not in totalStatus:
                        deadStones.append((x, y))
                        for i, j in aroundStonesStatusTotal:
                            if goBoard[j][i] == 1:
                                passStonesTemp.append((i, j))
                                deadStones.append((i, j))

                        print('deadStones:', deadStones)
                        print('(x, y):', (initial_x, initial_y))
                        if (initial_x, initial_y) in deadStones:
                           return 'dead'

                        self.recoveryStones += deadStones
                        self.goBoardUpdate(deadStones)
                    else:
                        for pos in passStonesTemp:
                            passStones.append(pos)

                # White
                elif goBoard[y][x] == 2:
                    if 0 not in totalStatus:
                        deadStones.append((x, y))
                        for i, j in aroundStonesStatusTotal:
                            if goBoard[j][i] == 2:
                                passStonesTemp.append((i, j))
                                deadStones.append((i, j))

                        print('deadStones:', deadStones)
                        print('(x, y):', (initial_x, initial_y))
                        if (initial_x, initial_y) in deadStones:
                           return 'dead'

                        self.goBoardUpdate(deadStones)
                        self.recoveryStones += deadStones

                    else:
                        for pos in passStonesTemp:
                            passStones.append(pos)

                if Pass:
                    break
            if Pass:
                break

    def checkAroundState(self, x, y):
        aroundStones = []
        # x-1
        try:
            if x-1 == -1: raise
            aroundStones.append((x-1, y))
        except: pass

        # x+1
        try:
            if x+1 == 19: raise
            aroundStones.append((x+1, y))
        except: pass

        # y-1
        try:
            if y-1 == -1: raise
            aroundStones.append((x, y-1))
        except: pass

        # y+1
        try:
            if y+1 == 19: raise
            aroundStones.append((x, y+1))
        except: pass

        return aroundStones

    def deepSearch(self, x, y, passStonesTemp, aroundStonesStatusTotal):
        passStonesTemp.append((x, y))

        # Get the info of around the chess
        aroundStones = self.checkAroundState(x, y)

        # Black Stone
        if goBoard[y][x] == 1:
            checkStonesList = []
            for i, j in aroundStones:
                if (i, j) in passStonesTemp: continue

                aroundStonesStatusTotal.append((i, j))
                if goBoard[j][i] == 1:
                    checkStonesList.append((i, j))
                    passStonesTemp.append((i, j))

            for checkStones in checkStonesList:
                aroundStonesStatusTotal += self.deepSearch(checkStones[0], checkStones[1], passStonesTemp, aroundStonesStatusTotal)

        # White Stone
        elif goBoard[y][x] == 2:
            checkStonesList = []
            for i, j in aroundStones:
                if (i, j) in passStonesTemp: continue

                aroundStonesStatusTotal.append((i, j))
                if goBoard[j][i] == 2:
                    checkStonesList.append((i, j))
                    passStonesTemp.append((i, j))

            for checkStones in checkStonesList:
                aroundStonesStatusTotal += self.deepSearch(checkStones[0], checkStones[1], passStonesTemp, aroundStonesStatusTotal)

        aroundStonesStatusTotal = list(set(aroundStonesStatusTotal))
        return aroundStonesStatusTotal

    def goBoardUpdate(self, deadStones):
        for pos in deadStones:
            goBoard[pos[1]][pos[0]] = 0

        MainWindow.setChessImg(deadStones, 0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
