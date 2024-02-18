# Parent is an abstract class and should not be initialised
import math
import UIpygame.PyUI
import pygame
from UIpygame import PyUI as pyui
import sys
import time
import os
from SudokuTile import SudokuTile

class SudokuParent:
    def __init__(self, ui: pyui.UI, levelNumber:int, boxWidth=3, boxHeight=3, boxesX=3, boxesY=3, validChars=[str(x) for x in range( 10)]):
        self.levelNumber = levelNumber
        self.board = []
        self.prevTime = time.time()
        self.boxWidth = boxWidth
        self.boxHeight = boxHeight
        self.boxesX = boxesX
        self.boxesY = boxesY
        self.pausedTime = 0
        self.ui = ui
        self.idIndex = 0
        self.makeTable()
        self.sideMenu()
        self.makePauseMenu()
        self.makeSettingsMenu()
        self.validChars = validChars
        self.paused = False
        self.timeElapsed = 0
        self.prevShifted = False
        #will eventually fetch levels from a database
        self.levels = [
            ((3,"6"),(4,"8"),(6,"1"),(7,"9"),(9,"2"),(10,"6"),(13,"7"),(17,"4"),(18,"7"),(20,"1"),(22,"9"),(24,"5"),(27,"8"),(28,"2"),(32,"4"),(34,"5"),(36,"1"),(39,"6"),(41,"2"),(44,"3"),(46,"4"),(48,"9"),(52,"2"),(53,"8"),(56,"9"),(58,"4"),(60,"7"),(62,"3"),(63,"3"),(67,"5"),(70,"1"),(71,"8"),(73,"7"),(74,"4"),(76,"3"),(77,"6")),
            ((6,"5"),(9,"8"),(11,"1"),(22,"4"),(23,"3"),(34,"2"),(37,"7"),(43,"3"),(45,"8"),(48,"1"),(54,"6"),(59,"3"),(66,"4"),(69,"2"),(73,"7"),(74,"5"),(78,"6"))
            ]
        self.makeLevel()


    def makeLevel(self):
        print(self.levelNumber)
        level = self.levels[self.levelNumber]
        for pos, value in level:
            self.board[pos].fixNumber(value)
            self.ui.IDs["SudokuTextBox" + str(pos) + "_"].imgdisplay=True
            self.ui.IDs["SudokuTextBox" + str(pos) + "_"].settext('{"'+value+'" underlined=True}')
        self.ui.refreshall()



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

        def datavalidation(textID, Tile:SudokuTile):
            currentText = self.ui.IDs[textID].text
            lengthOfText = len(currentText)
            if Tile.editable:
                if not(self.ui.IDs["NotesToggle"].toggle):
                    if lengthOfText == 0:
                        #code for if they press the backspace and the notes is toggled, will set object to ""
                        Tile.setNumber("")
                        return
                    elif lengthOfText == 1:
                        # the code if entered notes mode and tries to type a note
                        if currentText in self.validChars:
                            # Toggles wether the note is there
                            if currentText in Tile.Notes:
                                self.ui.delete(textID + "Note" + currentText + "_")

                            else:
                                # put the note in the correct position
                                print("h/3*" + str((int(currentText) - 1) // 3))
                                text = self.ui.maketext(0, 0, currentText, ID= textID + "Note" + currentText + "_", anchor=(
                                "w/3*" + str((int(currentText) - 1) % 3), "h/3*" + str((int(currentText) - 1) // 3)),
                                                        textsize=20 * 9 / (self.boxWidth * self.boxesX), backingcol=self.ui.IDs[textID].col)
                                self.ui.IDs[textID].binditem(text)
                            # Toggles the tile
                            Tile.toggleNote(currentText)
                        #text has been put in a note so is now deleted from the big text box
                        self.ui.IDs[textID].settext('')
                        return

                    else:
                        #the code if entered note mode and tried to type a note in a square that already has a number
                        #sets the number back to itself
                        self.ui.IDs[textID].settext(Tile.Number)
                        return

                else:
                    if lengthOfText == 0:
                        #code for if they press the backspace and notes isn't toggled, will delete the number from tile class
                        Tile.setNumber("")
                        return
                    elif lengthOfText == 1:
                        # If the enter a single number into a square that had no number
                        if currentText in self.validChars:
                            Tile.setNumber(currentText)
                            # Remove notes
                            Tile.clearNotes()
                            while len(self.ui.IDs[textID].bounditems) > 1:
                                self.ui.delete(self.ui.IDs[textID].bounditems[-1].ID)
                        else:
                            # If the new character isnt valid, returns to the old character
                            self.ui.IDs[textID].settext(Tile.Number)
                        return
                    else:
                        #the code to replace a number if you type a new number
                        if currentText[1] in self.validChars:
                            Tile.setNumber(currentText[1])
                        self.ui.IDs[textID].settext(Tile.Number)

            else:
                # tile is uneditable and will be set to its number value
                self.ui.IDs[textID].settext(Tile.Number)



        # Makes a 2d list of all the sub 3x3 squares in the sudoku grid
        squareXsize = int(240 / self.boxesX)
        squareYsize = int(240 / self.boxesY)
        TableData = []
        for _ in range(self.boxesY):
            TableX = []
            for _ in range(self.boxesX):
                TextBoxGrid = []
                for _ in range(self.boxHeight):
                    TextBoxLine = []
                    for _ in range(self.boxWidth):
                        # Creates the data for the 3x3 grids in a sudoku table
                        Tile = SudokuTile(True, "SudokuTextBox" + str(self.idIndex) + "_")
                        self.board.append(Tile)
                        func = pyui.funcer(datavalidation, textID="SudokuTextBox" + str(self.idIndex) + "_", Tile=Tile)
                        TextBoxLine.append(self.ui.maketextbox(0, 0, ID="SudokuTextBox" + str(self.idIndex) + "_",
                                                               width=270 / self.boxesX / self.boxWidth, height=270 / self.boxesY / self.boxHeight, lines=1,
                                                               textcenter=True, textsize=100*9/(self.boxWidth*self.boxesX),
                                                               backingcol=(255, 0, 0),
                                                               commandifkey=True,
                                                               command=func.func))
                        self.idIndex = self.idIndex + 1
                    TextBoxGrid.append(TextBoxLine)
                SubTableData = self.ui.maketable(0, 0, data=TextBoxGrid,
                                                 menu="SudokuGame", boxwidth=squareXsize, boxheight=squareYsize,
                                                 scaleby="vertical")
                # Adds the 3x3 grid to to the x axis
                TableX.append(SubTableData)
            TableData.append(TableX)

        # Puts the 2d list of 3x3 grids into a larger grid making up the sudoku table, also does scaling and centering
        # of the table

        self.ui.maketable(0, 0, ID="SudokuTable", data=TableData, menu="SudokuGame", boxwidth=self.boxWidth * squareXsize + 1*(self.boxesX + 1),
                          boxheight= self.boxHeight * squareYsize + 1*(self.boxesY + 1), linesize=5, scaleby="vertical", scalesize=True,
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


