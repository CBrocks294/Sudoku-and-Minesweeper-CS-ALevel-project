# Parent is an abstract class and should not be initialised
import math

import UIpygame.PyUI
import pygame
from UIpygame import PyUI as pyui
import sys
import time


class SudokuParent:
    def __init__(self, ui: pyui.UI):
        self.prevTime = time.time()
        self.pausedTime = 0
        self.ui = ui
        self.idIndex = 0
        self.makeTable()
        self.sideMenu()
        self.validChars = [str(x) for x in range(10)]
        print(self.validChars)
        self.active = True
        self.paused = False
        self.timeElapsed = 0
        pauseMenu = self.ui.makewindowedmenu(0, 0, 800, 600, menu="PausedMenu", behindmenu="SudokuGame", darken=230, anchor=("w/2", "h/2"),  center=True)
        self.ui.maketext(0, 0, text="Paused", anchor=("w/2", "4*h/10"), center=True, textsize=100, menu="PausedMenu", backingcol=pauseMenu.col)
        self.ui.maketext(0, 0, ID="PausedMenuTime", text="Paused", anchor=("w/2", "5*h/10"), center=True, textsize=50, menu="PausedMenu", backingcol=pauseMenu.col)
        self.ui.makebutton(-100, 0, text= "Unpause", command=lambda: self.pause(), menu="PausedMenu", ID="UnpauseGame", center=True, anchor=("w/2", "3*h/4"))
        self.ui.makebutton(100, 0, text="Unpause2", command=lambda: self.pause(), menu="PausedMenu", ID="PauseButton", center=True, anchor=("w/2", "3*h/4"))

    # self.ui.maketextbox(0, 0, width=30, height=30, lines=1, backingcol=(255,0,0))
    def pause(self):
        currentTime = time.time()
        # Updates the total elapsed time by adding in the time since it was last updated
        self.timeElapsed += currentTime - self.prevTime
        # Sets the previous time to the current time for the next run
        self.prevTime = currentTime
        self.paused = True

        # Makes a window and blurs the side screen
        self.ui.movemenu("PausedMenu", slide="up")


    def sideMenu(self):

        # Makes the rectangle that the buttons are displayed on
        self.ui.makerect(0, 0, width=200, height=200, menu="SudokuGame", ID="SideMenu", center=True,
                         anchor=('10*w/12', 'h/2'))
        # Finds the background colour of the menu the text sits on to set as the background
        backingColour = self.ui.IDs["SideMenu"].col
        # Puts the text to say menus
        self.ui.maketext(0, 0, "Menus", ID="SideMenuText", menu="SudokuGame", textsize=50, textcenter=True, center=True
                         , layer=2, anchor=("w/2", "h/4"), backingcol=backingColour)
        self.ui.maketext(0, 0, "00:00", ID="Timer", menu="SudokuGame", textsize=50, textcenter=True, center=True
                         , layer=2, anchor=("w/2", "h/2"), backingcol=backingColour)
        self.ui.makebutton(0, 0, " ", command=lambda: self.pause(), ID ="PauseButton", anchor=("w/2", "3*h/4"))

        self.ui.IDs["SideMenu"].binditem(self.ui.IDs["SideMenuText"])
        self.ui.IDs["SideMenu"].binditem(self.ui.IDs["Timer"])
        self.ui.IDs["SideMenu"].binditem(self.ui.IDs["PauseButton"])

    def makeTable(self):

        def datavalidation(textID):
            while len(self.ui.IDs[textID].text) >= 1:
                if self.ui.IDs[textID].text[-1] in self.validChars:
                    self.ui.IDs[textID].settext(self.ui.IDs[textID].text[-1])
                    return
                else:
                    self.ui.IDs[textID].settext(self.ui.IDs[textID].text[0:-1])

        # Makes a 2d list of all the sub 3x3 squares in the sudoku grid
        squaresize = 80
        TableData = []
        for _ in range(3):
            TableX = []
            for _ in range(3):
                TextBoxGrid = []
                for _ in range(3):
                    TextBoxLine = []
                    for _ in range(3):
                        # Creates the data for the 3x3 grids in a sudoku table
                        func = pyui.funcer(datavalidation, textID="SudokuTextBox" + str(self.idIndex) + "_")
                        TextBoxLine.append(self.ui.maketextbox(0, 0, ID="SudokuTextBox" + str(self.idIndex) + "_",
                                                               width=30, height=30, lines=1,
                                                               textcenter=True, textsize=100, textoffsety=10,
                                                               backingcol=(255, 0, 0),
                                                               commandifkey=True,
                                                               command=func.func))
                        self.idIndex = self.idIndex + 1
                    TextBoxGrid.append(TextBoxLine)
                SubTableData = self.ui.maketable(0, 0, data=TextBoxGrid,
                                                 menu="SudokuGame", boxwidth=squaresize, boxheight=squaresize,
                                                 scaleby="vertical")
                # Adds the 3x3 grid to to the x axis
                TableX.append(SubTableData)
            TableData.append(TableX)

        # Puts the 2d list of 3x3 grids into a larger grid making up the sudoku table, also does scaling and centering
        # of the table

        self.ui.maketable(0, 0, ID="SudokuTable", data=TableData, menu="SudokuGame", boxwidth=3 * squaresize + 8,
                          boxheight=3 * squaresize + 8, linesize=5, scaleby="vertical", scalesize=True,
                          anchor=('5*w/12', 'h/2'), center=True)

    def close(self):
        pass

    def updateTimer(self):
        if not self.paused:
            # Gets the current time
            currentTime = time.time()
            # Updates the total elapsed time by adding in the time since it was last updated
            self.timeElapsed += currentTime - self.prevTime
            # Sets the previous time to the current time for the next run
            self.prevTime = currentTime
            # Updates the timer on the screen
            self.ui.IDs["Timer"].settext("{}:{:02d}".format(int(self.timeElapsed // 60), int((self.timeElapsed // 1) % 60)))
        else:
            self.ui.IDs["PausedMenuTime"].settext("Current Time: {}:{:02d}".format(int(self.timeElapsed // 60), int((self.timeElapsed // 1) % 60)))
            #Unpauses the timer if the pause menu is closed
            if self.ui.activemenu!="PausedMenu":
                self.paused=False
                #sets a time for the timer to calculate how long since unpaused
                self.prevTime = time.time()

