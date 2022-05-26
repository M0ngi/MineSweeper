#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
import random
import time

class KeyboardKeys:
    KEY_UP = 16777235
    KEY_DOWN = 16777237
    KEY_RIGHT = 16777236
    KEY_LEFT = 16777234


class TimeCounter(QtCore.QObject):
    def __init__(self, ui):
        QtCore.QObject.__init__(self)

        self.ui = ui
        self.finished = QtCore.pyqtSignal()
        self.time = 0
        self.running = True

    def run(self):
        while self.running:
            time.sleep(1)
            self.time += 1
            self.ui.setTime(self.time)
            self.ui.update()


class Game(QtGui.QWidget):
    TextFont = QtGui.QFont()
    TextFont.setBold(True)
    TextFont.setPointSize(25)
    TextFont.setFamily("Arial")

    def __init__(self):
        super(Game, self).__init__()

        self.TimeCounter = TimeCounter(self)
        self.TimeThread = QtCore.QThread()
        self.TimeCounter.moveToThread(self.TimeThread)
        self.TimeThread.started.connect(self.TimeCounter.run)
        
        self.size = 9
        self.nBombs = 15

        self.BoxSize = 45
        self.startcords = (40, 50)

        self.initData()
        self.initUI()
    
    def startTimer(self):
        self.TimeCounter.running = True
        self.TimeCounter.time = 0
        self.TimeThread.start()
        return True

    def killTimer(self):
        self.TimeCounter.running = False
        self.TimeThread.terminate()
        return True
    
    def setTime(self, time):
        self.GameInfo.setText('Time: '+str(time))
        return True
    
    def initData(self):
        self.BombLocs = [[0]*self.size for _ in range(self.size)]
        self.Buttons = [[0]*self.size for _ in range(self.size)]
        self.Flags = [[0]*self.size for _ in range(self.size)]
        self.Visible = [[0]*self.size for _ in range(self.size)]

        self.Begin = False
        self.GameOver = False
        self.seconds = 0

    def initUI(self):      
        self.setGeometry(100, 100, self.BoxSize*self.size+80, self.BoxSize*self.size+90)
        self.setWindowTitle('SweepMiner Game')
        self.setMaximumSize(self.BoxSize*self.size+80, self.BoxSize*self.size+90)
        self.setMinimumSize(self.BoxSize*self.size+80, self.BoxSize*self.size+90)

        self.RestartButton = QtGui.QPushButton('Restart', self)
        self.RestartButton.setGeometry(QtCore.QRect((self.BoxSize*self.size+80)/2-30, 10, 60, 30))
        self.RestartButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.RestartButton.clicked.connect(self.RestartGame)

        self.setupButtons()
        self.setupBombs()

        self.GameInfo = QtGui.QLabel('Time: 0', self)
        self.GameInfo.setGeometry(QtCore.QRect((self.BoxSize*self.size+80)/2 + 90, 0, 100, 50))
        self.GameInfo.setFocusPolicy(QtCore.Qt.NoFocus)
        
        self.GameOverText = QtGui.QLabel('', self)
        self.GameOverText.setGeometry(QtCore.QRect((self.BoxSize*self.size+80)/2 - 150, 0, 100, 50))
        self.GameOverText.setFocusPolicy(QtCore.Qt.NoFocus)

        self.show()

    def setupButtons(self):
        for line in range(self.size):
            for row in range(self.size):
                b = QtGui.QPushButton(self)
                b.setGeometry(QtCore.QRect(self.startcords[0]+row*self.BoxSize, self.startcords[1]+line*self.BoxSize, self.BoxSize, self.BoxSize))
                b.setText(' ')
                b.clicked.connect(lambda state, cords=[row, line]: self.BombClick(cords[0], cords[1]))
                b.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
                b.customContextMenuRequested.connect(lambda state, cords=[row, line]: self.toggleFlag(cords[0], cords[1]))
                b.show()

                self.Buttons[line][row] = b
        return True

    def setupBombs(self):
        bCount = 0

        while bCount != self.nBombs:
            xy = [random.randint(0, self.size-1), random.randint(0, self.size-1)]
            while self.BombLocs[xy[1]][xy[0]] == 1:
                xy = [random.randint(0, self.size-1), random.randint(0, self.size-1)]

            self.BombLocs[xy[1]][xy[0]] = 1
            bCount += 1
        return True

    def ShowBombs(self):
        for line in range(self.size):
            for row in range(self.size):
                if self.BombLocs[line][row] == 1:
                    self.Buttons[line][row].setText('B')
        return True
    
    def toggleFlag(self, x, y):
        if self.GameOver:
            return False
        
        if self.Flags[y][x] == 1:
            self.Flags[y][x] = 0
            self.Buttons[y][x].setText('')
        else:
            self.Buttons[y][x].setText('F')
            self.Flags[y][x] = 1
        return True
        
    def BombClick(self, x, y):
        if self.GameOver:
            return False

        if self.Flags[y][x] == 1:
            return False
        
        self.Visible[y][x] = 1
        if self.BombLocs[y][x] == 1:
            if not self.Begin:
                self.startGame()

                xy = [random.randint(0, self.size-1), random.randint(0, self.size-1)]
                while self.BombLocs[xy[1]][xy[0]] == 1:
                    xy = [random.randint(0, self.size-1), random.randint(0, self.size-1)]

                self.BombLocs[xy[1]][xy[0]] = 1
                self.BombLocs[y][x] = 0

                if self.setButtonText(x, y) == 0:
                    self.showNear(x, y)

            else:
                self.GameLost()
                self.ShowBombs()
        else:
            if not self.Begin:
                self.startGame()
            
            if self.setButtonText(x, y) == 0:
                self.showNear(x, y)
        
        self.CheckGame()
        return True
    
    def startGame(self):
        self.Begin = True
        self.startTimer()
        self.setTime(0)
        self.update()
        return True
    
    def showNear(self, x, y):
        for line in range(max(0, y-1), min(self.size, y+2)):
            for row in range(max(0, x-1), min(self.size, x+2)):
                if self.Visible[line][row] == 0:
                    self.BombClick(row, line)
        return True

    def getBombCount(self, x, y):
        bCount = 0
        for line in range(max(0, y-1), min(self.size, y+2)):
            for row in range(max(0, x-1), min(self.size, x+2)):
                if self.BombLocs[line][row] == 1:
                    bCount += 1
        return bCount

    def setButtonText(self, x, y):
        bCount = self.getBombCount(x, y)

        self.Buttons[y][x].setText(str(bCount))
        return bCount

    def CheckGame(self):
        total = sum([sum(x) for x in self.Visible])
        if total + self.nBombs == self.size**2:
            self.GameWon()
            return True
        return False

    def GameEnded(caller):
        def dec(self):
            self.GameOver = True
            self.killTimer()
            caller(self)
        return dec
    
    @GameEnded
    def GameWon(self):
        self.GameOverText.setText('You won!')

    @GameEnded
    def GameLost(self):
        self.GameOverText.setText('You lost!')

    def RestartGame(self):
        for line in range(self.size):
            for row in range(self.size):
                self.Buttons[line][row].deleteLater()

        if self.TimeThread.isRunning():
            self.killTimer()
        
        self.initData()
        self.setupButtons()
        self.setupBombs()
        self.update()
        return True
    

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Game()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()