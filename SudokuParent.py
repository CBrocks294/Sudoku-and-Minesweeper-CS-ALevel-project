# Parent is an abstract class and should not be initialised
import math
import UIpygame.PyUI
import pygame
from UIpygame import PyUI as pyui
import sys
import time
import os


class SudokuParent:
    def __init__(self, ui: pyui.UI):
        self.prevTime = time.time()
        self.pausedTime = 0
        self.ui = ui
        self.idIndex = 0
        self.makeTable()
        self.sideMenu()
        self.makePauseMenu()
        self.makeSettingsMenu()
        self.validChars = [str(x) for x in range(10)]
        print(self.validChars)
        self.active = True
        self.paused = False
        self.timeElapsed = 0
        self.prevShifted = False

    def makeSettingsMenu(self):
        settingsMenu = self.ui.makewindowedmenu(0, 0, 800, 600, ID="SettingsMenu", menu="SettingsMenu",
                                             behindmenu="SudokuGame", anchor=("w/2", "h/2"), center=True)
        self.ui.maketext(0, 0, text="Settings", width=300, anchor=("w/2", "2*h/10"), center=True, textsize=100,
                         menu="SettingsMenu", backingcol=settingsMenu.col)
        self.ui.makebutton(0, 0, width=300, text="Continue", command=lambda: self.ui.menuback(), menu="SettingsMenu",
                           ID="Exit Settings", center=True, anchor=("4*w/5", "9*h/10"))
        self.ui.maketext(10, -50, text="Display Timer", width=300, anchor=("0", "h/2"), textsize=50,
                         menu="SettingsMenu", backingcol=settingsMenu.col)
        self.ui.makebutton(10, 0, 'Yes', toggletext='No', width=300, ID='TimerToggle', menu="SettingsMenu", anchor=("0", "h/2"), toggleable=True)
        self.ui.maketext(10, -150, text="Error Checking Level", width=300, anchor=("0", "h/2"), textsize=50,
                         menu="SettingsMenu", backingcol=settingsMenu.col)
        self.ui.makedropdown(10, -100, ['No Error Checking','Check Button', 'Highlight Errors', 'Highlight Errors and Notes'], ID='SettingsDropdown', menu="SettingsMenu",
                             anchor=("0", "h/2"))


    def makePauseMenu(self):
        pauseMenu = self.ui.makewindowedmenu(0, 0, 800, 600, ID="PausedMenu", menu="PausedMenu", behindmenu="SudokuGame", darken=230, anchor=("w/2", "h/2"),  center=True)
        self.ui.maketext(0, 0, text="Paused", width=300, anchor=("w/2", "4*h/10"), center=True, textsize=100, menu="PausedMenu", backingcol=pauseMenu.col)
        self.ui.maketext(0, 0, ID="PausedMenuTime", text="Paused", anchor=("w/2", "5*h/10"), center=True, textsize=50, menu="PausedMenu", backingcol=pauseMenu.col)
        self.ui.makebutton(-200, 0, width=300, text= "Save and Quit", command=lambda: self.saveandquit(), menu="PausedMenu", ID="SaveAndQuit", center=True, anchor=("w/2", "3*h/4"))
        self.ui.makebutton(200, 0, width=300, text="Continue", command= lambda: self.ui.menuback(), menu="PausedMenu", ID="UnpauseButton", center=True, anchor=("w/2", "3*h/4"))

    # self.ui.maketextbox(0, 0, width=30, height=30, lines=1, backingcol=(255,0,0))

    def saveandquit(self):
        self.ui.menuback()
        self.ui.IDs["ExitGame"].command()

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
        #Pause button
        self.ui.makebutton(-60, 0, "{pause}", 30, width=50, command=lambda: self.pause(), ID ="PauseButton", anchor=("w/2", "3*h/4"), center=True)
        # Settings Menu
        self.ui.makebutton(0, 0,"{settings}", 30,width =50, command=lambda: self.ui.movemenu('SettingsMenu', slide="up"), ID="OpenSettings",
                           anchor=("w/2", "3*h/4"), center=True)
        # Brings in the notes image
        notespng = pygame.image.load(os.path.join('C:\homework\comp sci\Python\python\Sudoku-and-Minesweeper-CS-ALevel-project', 'Penlogo.png'))
        # Adds the image to pyUI
        self.ui.addinbuiltimage('NotesImage', notespng)
        #draws a button with the notes image as the
        self.ui.makebutton(60, 0, "{NotesImage}", 30,width =50,toggleable=True, ID="NotesToggle",
                           anchor=("w/2", "3*h/4"), center=True)

        self.ui.IDs["SideMenu"].binditem(self.ui.IDs["SideMenuText"])
        self.ui.IDs["SideMenu"].binditem(self.ui.IDs["Timer"])
        self.ui.IDs["SideMenu"].binditem(self.ui.IDs["PauseButton"])
        self.ui.IDs["SideMenu"].binditem(self.ui.IDs["OpenSettings"])
        self.ui.IDs["SideMenu"].binditem(self.ui.IDs["NotesToggle"])

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

    def updateTimerDisplay(self, TargetText, TimeTextPrefix = ""):
        # Updates the timer displays, or leaves it blank it timer is off
        if self.ui.IDs["TimerToggle"].toggle:
            self.ui.IDs[TargetText].settext(TimeTextPrefix + "{}:{:02d}".format(int(self.timeElapsed // 60), int((self.timeElapsed // 1) % 60)))
        else:
            self.ui.IDs[TargetText].settext("")

    def updateTimer(self):
        if not self.paused:
            # Gets the current time
            currentTime = time.time()
            # Updates the total elapsed time by adding in the time since it was last updated
            self.timeElapsed += currentTime - self.prevTime
            # Sets the previous time to the current time for the next run
            self.prevTime = currentTime
            # Updates the timer on the screen
            self.updateTimerDisplay("Timer")
            # Checks if either of the shifts are pressed
            if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]:
                # Checks shift wasn't pressed on previous frame
                if self.prevShifted == False:
                    # Toggles the notes mode
                    self.ui.IDs["NotesToggle"].press()
                    # Sets that the previous frame had shifted
                    self.prevShifted = True
            # Sets that the previous frame hadnt shifted
            else: self.prevShifted = False

        else:
            self.updateTimerDisplay("PausedMenuTime", "Current Time: ")
            # Unpauses the timer if the pause menu is closed
            if self.ui.activemenu != "PausedMenu":
                self.paused = False
                # Sets a time for the timer to calculate how long since unpaused
                self.prevTime = time.time()


