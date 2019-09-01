# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from gameManager import *


class chess(QtWidgets.QLabel):
    def __init__(self, centralwidget, goBoard, turns):
        super(chess, self).__init__(centralwidget)
        super().__init__(a, b)
        self.centralwidget = centralwidget
        self.goBoard = goBoard

    def mousePressEvent(self, event):
        turns = get_turns()

        if event.buttons() == QtCore.Qt.LeftButton:
            blackStone = QtGui.QPixmap()
            blackStone.load('Image/black_stone.svg')
            whiteStone = QtGui.QPixmap()
            whiteStone.load('Image/white_stone.svg')

            if turns % 2 == 0:
                self.setPixmap(blackStone)
            else:
                self.setPixmap(whiteStone)

            x = int((self.x()-10)/50)
            y = int((self.y()-60)/50)

            if turns % 2 == 0:
                self.goBoard[y][x] = 1
            else:
                self.goBoard[y][x] = 2

            turns += 1
            self.EatChess()
            self.showBoard()
            set_turns(turns)

    def showBoard(self):
        for raw in self.goBoard:
            print(raw)

    def EatChess(self, initial_x=0, initial_y=0):
        passStones = []

        for x in range(initial_x, 19):
            for y in range(initial_y, 19):
                deadStones = []
                passStonesTemp = []
                aroundStonesStatusTotal = []

                if (x, y) in passStones or self.goBoard[y][x] == 0: continue

                aroundStonesStatusTotal = self.deepSearch(x, y, passStonesTemp, aroundStonesStatusTotal)
                print('周圍狀態（同塊）:', aroundStonesStatusTotal)

                # Finally Determine
                # totalStatus is coler
                # aroundStonesStatusTotla is position
                totalStatus = [self.goBoard[pos[1]][pos[0]] for pos in aroundStonesStatusTotal]

                # Black
                if self.goBoard[y][x] == 1:
                    if 0 not in totalStatus:
                        deadStones.append((x, y))
                        for i, j in aroundStonesStatusTotal:
                            if self.goBoard[j][i] == 1:
                                passStonesTemp.append((i, j))
                                deadStones.append((i, j))

                        self.goBoardUpdate(deadStones)

                    else:
                        for pos in passStonesTemp:
                            passStones.append(pos)

                # White
                elif self.goBoard[y][x] == 2:
                    if 0 not in totalStatus:
                        deadStones.append((x, y))
                        for i, j in aroundStonesStatusTotal:
                            if self.goBoard[j][i] == 2:
                                passStonesTemp.append((i, j))
                                deadStones.append((i, j))

                        self.goBoardUpdate(deadStones)

                    else:
                        for pos in passStonesTemp:
                            passStones.append(pos)

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
            if x+1 == 19: raise
            aroundStones.append((x, y+1))
        except: pass

        return aroundStones

    def deepSearch(self, x, y, passStonesTemp, aroundStonesStatusTotal):
        passStonesTemp.append((x, y))

        # Get the info of around the chess
        aroundStones = self.checkAroundState(x, y)
        print('周圍座標:', aroundStones)

        # Black Stone
        if self.goBoard[y][x] == 1:
            checkStonesList = []
            for i, j in aroundStones:
                if (i, j) in passStonesTemp: continue

                aroundStonesStatusTotal.append((i, j))
                if self.goBoard[j][i] == 1:
                    checkStonesList.append((i, j))
                    passStonesTemp.append((i, j))

            for checkStones in checkStonesList:
                aroundStonesStatusTotal += self.deepSearch(checkStones[0], checkStones[1], passStonesTemp, aroundStonesStatusTotal)

        # White Stone
        elif self.goBoard[y][x] == 2:
            checkStonesList = []
            for i, j in aroundStones:
                if (i, j) in passStonesTemp: continue

                aroundStonesStatusTotal.append((i, j))
                if self.goBoard[j][i] == 2:
                    checkStonesList.append((i, j))
                    passStonesTemp.append((i, j))

            for checkStones in checkStonesList:
                aroundStonesStatusTotal += self.deepSearch(checkStones[0], checkStones[1], passStonesTemp, aroundStonesStatusTotal)

        aroundStonesStatusTotal = list(set(aroundStonesStatusTotal))
        return aroundStonesStatusTotal

    def goBoardUpdate(self, deadStones):
        for pos in deadStones:
            self.goBoard[pos[1]][pos[0]] = 0
