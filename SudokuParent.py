# Parent is an abstract class and should not be initialised
import copy
import math
import UIpygame.PyUI
import pygame
from UIpygame import PyUI as pyui
import sys
import time
import os
from SudokuTile import SudokuTile

class SudokuParent:
    def __init__(self, ui: pyui.UI, levelNumber:int, boxWidth=3, boxHeight=3, boxesX=3, boxesY=3, validChars=[str(x) for x in range(1,10)]):
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
        # Adds the solve and hint buttons.
        self.makeAdditionalButtons()
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
        self.previousConflictNumbers = set()
        self.previousConflictNotes = set()
        self.renderingErrorCheckButton = False
        self.currentHint = None

    def makeAdditionalButtons(self):
        self.ui.makebutton(10, 60, width=130, ID="ShowHint", text="Hint", menu="SudokuGame", command=lambda: self.displayHint())
        self.ui.makebutton(10, 110, width = 130, ID="SolveBoard", text="Solve", menu="SudokuGame", command=lambda: self.displaySolve())
        self.ui.makebutton(10, 160, width=130, ID="ShowErrors", text="Errors", menu="SudokuGame",enabled=False, command=lambda: self.highlightConflicts(False))

    def displayHint(self):
        hint, solvable = self.hint()
        if solvable:
            self.ui.IDs["SudokuTextBox" + str(hint) + "_"].col = (0,255,0)
            self.ui.IDs["SudokuTextBox" + str(hint) + "_"].refresh()
            self.currentHint = hint
        else:
            notSolvable = self.ui.maketext(0,0,"Board is not solvable", maxwidth=300, menu="SudokuGame", killtime=3, center=True, anchor=("w/2", "1.2*h"))
            self.ui.IDs["SideMenu"].binditem(notSolvable)
    def displaySolve(self):
        board, solvable = self.solve()
        if solvable:
            for index, Tile in enumerate(board):
                self.ui.IDs["SudokuTextBox" + str(index) + "_"].text = Tile.Number
                self.ui.IDs["SudokuTextBox" + str(index) + "_"].refresh()
            self.board = board
            return
        else:
            notSolvable = self.ui.maketext(0, 0, "Board is not solvable", maxwidth=300, menu="SudokuGame", killtime=3,
                                           center=True, anchor=("w/2", "1.2*h"))
            self.ui.IDs["SideMenu"].binditem(notSolvable)

    def findRowAndColumn(self, index):
        # Takes the index of a board tile and returns the row and column of that tile
        row = self.boxHeight * (index // (self.boxesX*self.boxHeight*self.boxWidth)) + (index // self.boxWidth) % self.boxHeight
        column = self.boxWidth * ((index // (self.boxWidth*self.boxHeight)) % self.boxesX) + (index % self.boxWidth)
        return(row,column)

    def findIndex(self, row, column):
        # Takes a row and column and returns the index on the board
        index = (self.boxWidth * (row % self.boxHeight) + self.boxesX*self.boxHeight*self.boxWidth * (row // self.boxHeight)
                + (column) % self.boxWidth + self.boxWidth * self.boxHeight * ((column) // self.boxWidth))
        return index

    def possibleValues(self, index):
        # A list of all the possible values of a tile exclusing values that are in the row, column or grid

        #First we get the row and column of the tile we are checking. This is used later to itterate over the row and column
        row, column = self.findRowAndColumn(index)
        # Creates a list of all the values, we copy it so when possible values are removed doesnt effect the object variable
        possibleValues = copy.copy(self.validChars)

        # check the current grid for values
        # pos is the positon in the subgrid
        for pos in range(self.boxWidth*self.boxHeight):
            # The try will remove the value from possible Values if it's still there
            try:
                # Goes through the subtile grid and removes any values from the possible value list that is there
                possibleValues.remove(self.board[(index // (self.boxWidth*self.boxHeight)) * (self.boxWidth*self.boxHeight) + pos].Number)
            except ValueError:
                # If the number has already been removed, or the tile is empty
                pass
        # pos here is how far along the row to check
        for pos in range(self.boxWidth*self.boxesX):
            try:
                # Goes through the subtile grid and removes any values from the possible value list that is there
                possibleValues.remove(self.board[self.findIndex(row, pos)].Number)
            except ValueError:
                # If the number has already been removed, or the tile is empty
                pass
        for pos in range(self.boxHeight*self.boxesY):
            try:
                # Goes through the subtile grid and removes any values from the possible value list that is there
                possibleValues.remove(self.board[self.findIndex(pos, column)].Number)
            except ValueError:
                # If the number has already been removed, or the tile is empty
                pass
        return possibleValues

    def assignHeuristic(self):
        # Copys the board so we can edit the notes without effecting the players board
        testBoard = copy.deepcopy(self.board)
        # This will store the tile with the best heuristic, and keep track of its value
        # Finds the list of all the possible values for each tile. Storing the tile and list where the list length the shortest
        for index, tile in enumerate(testBoard):
            # Checks it's a tile that needs solving
            if tile.Number == "":
                possibleVals = self.possibleValues(index)
                # If a tile has no possible values unsolvable is true
                if len(possibleVals) == 0:
                    return None, False
                # Will store possible values in notes
                tile.Notes = possibleVals

        # Tries each possible value for the best tile. If the end condition is reached leaves the recursion.
        return testBoard, True

    def conflicts(self):
        # Set to avoid duplicates and allows for the xor operation later
        numberIndexes = set()
        duplicateNotes = set()
        # Checks every tile on the board for conflicts
        for index, tile in enumerate(self.board):
            # The row and column of the value currently being checked
            row, column = self.findRowAndColumn(index)
            # Tile can only conflict if it isnt empty
            if tile.Number != "":
                # Checks the row the tile is on
                for checkRow in range(self.boxHeight*self.boxesY):
                    # The tile doesn't check itself as if it has a collision we will add it when we check the other tile
                    if checkRow != row:
                        # value to check
                        checkIndex = self.findIndex(checkRow, column)
                        if self.board[checkIndex].Number == tile.Number:
                            # If a tile in the row matches the tile we are currently checking we add the tile in the
                            # row to the list
                            numberIndexes.add(checkIndex)
                        if tile.Number in self.board[checkIndex].Notes:
                            # We also check the notes of all the tiles in the row
                            duplicateNotes.add((checkIndex, tile.Number))

                for checkColumn in range(self.boxWidth*self.boxesX):
                    # Same as the checkRow loop but for columns
                    # Makes sure we aren't comparing the tile to itself
                    if checkColumn != column:
                        # Position to compare
                        checkIndex = self.findIndex(row, checkColumn)
                        if self.board[checkIndex].Number == tile.Number:
                            # If tile matches add it to the set of repeated tiles
                            numberIndexes.add(checkIndex)
                        if tile.Number in self.board[checkIndex].Notes:
                            # Also adds the position and number of any notes that collide
                            duplicateNotes.add((checkIndex, tile.Number))

                # Iterates over the box
                for checkTile in range(self.boxWidth * self.boxHeight):
                    # The top left tile index of the box + the number we are checking.
                    checkIndex = (index // (self.boxWidth * self.boxHeight)) * (self.boxWidth * self.boxHeight) + checkTile
                    # Don't compare tile to itself
                    if checkIndex != index:
                        # If the tile matches we add it to the collisions set
                        if self.board[checkIndex].Number == tile.Number:
                            numberIndexes.add(checkIndex)
                        # If the note matches we add it to the note collisions set
                        if tile.Number in self.board[checkIndex].Notes:
                            duplicateNotes.add((checkIndex, tile.Number))
        return numberIndexes, duplicateNotes

    def hint(self):
        # Gets a board where all the notes are the possible values
        board, solvable = self.assignHeuristic()
        # If the board is not in a solvable state returns None
        if not(solvable):
            return None, False
        # Sores the board so the first values have the fewest possible values
        board.sort(key = lambda tile: len(tile.Notes))
        # Remove any tiles where the notes are zero as the tile is solved
        bestTiles = list(filter(lambda tile: len(tile.Notes) > 0, board))
        # If the board isn't solved and a hit is possible returns the index
        if len(bestTiles) != 0:
            return(bestTiles[0].intIndex, True)
        return None, False

    def backtracking(self, board):
        # First we find the tile with the lowest heuteristic
        orderedBoard = sorted(board,key=lambda tile: len(tile.Notes))
        bestTiles = list(filter(lambda tile: tile.Number == "", orderedBoard))
        # If all the tiles are solved return the board, the end condition
        if len(bestTiles) == 0:
            return(board, True)
        bestTile = bestTiles[0]
        # Finds the row and column of tile we are trialing.
        row, column = self.findRowAndColumn(bestTile.intIndex)
        # Index of the top left corner of the box
        checkIndex = (bestTile.intIndex // (self.boxWidth * self.boxHeight)) * (self.boxWidth * self.boxHeight)
        # Once it has the best value it tries each possible value
        for trialVal in bestTile.Notes:
            # Copys board so we don't edit the previous layers recursion.
            testBoard = copy.deepcopy(board)
            # Goes through the row of the copy of the board and removes any values from notes that match the value being tried
            for checkRow in range(self.boxWidth * self.boxesX):
                # Doesn't check the row if the box is the box we are currently editing
                if checkRow == row:
                    continue
                # If the value is in any notes of the box on the row we toggle it to remove it. If the notes is them
                # empty we return as their is no possible solution
                if trialVal in testBoard[self.findIndex(checkRow, column)].Notes:
                    testBoard[self.findIndex(checkRow, column)].toggleNote(trialVal)
                    if len(testBoard[self.findIndex(checkRow, column)].Notes) == 0:
                        return None, False
            # Same as the check row loop above but for the columns
            for checkColumn in range(self.boxHeight * self.boxesY):
                if checkColumn == column:
                    continue
                if trialVal in testBoard[self.findIndex(row, checkColumn)].Notes:
                    testBoard[self.findIndex(row, checkColumn)].toggleNote(trialVal)
                    if len(testBoard[self.findIndex(row, checkColumn)].Notes) == 0:
                        return None, False
            # Same as the checkColumn and checkRow loop except for sub boxes
            for checkTile in range(self.boxWidth * self.boxHeight):
                if checkIndex + checkTile == bestTile.intIndex:
                    continue
                if trialVal in testBoard[checkIndex + checkTile].Notes:
                    testBoard[checkIndex + checkTile].toggleNote(trialVal)
                    if len(testBoard[checkIndex + checkTile].Notes) == 0:
                        return None, False
            # If the board hasn't returned its still solvable so we set the value to our trial value and recursively
            # call itself with the new board.
            testBoard[bestTile.intIndex].setNumber(trialVal)
            testBoard[bestTile.intIndex].clearNotes()
            finalBoard, solved =  self.backtracking(testBoard)
            # If solved is true the board works so we exit. If not we try the next trial value
            if solved:
                return finalBoard, True
        # If we check every trial value and none of them produce a valid board one of the earlier guesses is wrong,
        # or the board is not solvable so we backtrack
        return None, False

    def solve(self):
        # Assigns the heurteristic to the board
        board, solvable = self.assignHeuristic()
        # If the board is potentially solvable as it has no tiles with no possible values, calls backtracking
        if solvable:
            return self.backtracking(board)
        else:
            return None, False

    def highlightConflicts(self, checkNotes):
        # Takes a list of numbers and notes that conflict
        conflictingNumbers, conflictingNotes = self.conflicts()
        # XOR the conflicts with the previous conflicts, anything that is returned requires toggling
        changeInConflicts = self.previousConflictNumbers ^ conflictingNumbers
        # Loop over the conflicts that require toggling
        for conflict in changeInConflicts:
            # If the conflcit no longer exists it will be in the previous conflict set
            if conflict in self.previousConflictNumbers:
                #self.ui.IDs["SudokuTextBox" + str(conflict) + "_"].textcol = self.ui.Style.defaults['textcol']
                # Sets the text back to black
                self.ui.IDs["SudokuTextBox" + str(conflict) + "_"].textcol = (0,0,0)
            else:
                # Sets the text to red
                self.ui.IDs["SudokuTextBox" + str(conflict) + "_"].textcol = (255,0,0)
            # Refreshes the text object so the colour is applied
            self.ui.IDs["SudokuTextBox" + str(conflict) + "_"].refresh()
        # Sets previous conflicts to the new conflicts
        self.previousConflictNumbers = conflictingNumbers


        # If the check notes is true we do the same logic as the Numbers above but on the notes
        if checkNotes:
            changeInNoteConflicts = self.previousConflictNotes ^ conflictingNotes
            for conflict in changeInNoteConflicts:
                if conflict in self.previousConflictNotes:
                    # Try except as the note could be deleted and would appear in the previousConflictNotes so checks
                    try:
                        # The notes conflicts are tuples (pos, value) so the ID of the text is slighly different.
                        # self.ui.IDs["SudokuTextBox" + str(conflict) + "_"].textcol = self.ui.Style.defaults['textcol']
                        self.ui.IDs["SudokuTextBox" + str(conflict[0]) + "_Note" + conflict[1] + "_"].textcol = (0, 0, 0)
                    except:
                        continue
                else:
                    self.ui.IDs["SudokuTextBox" + str(conflict[0]) + "_Note" + conflict[1] + "_"].textcol = (255, 0, 0)
                self.ui.IDs["SudokuTextBox" + str(conflict[0]) + "_Note" + conflict[1] + "_"].refresh()
            self.previousConflictNotes = conflictingNotes



    def makeLevel(self):
        level = self.levels[self.levelNumber]
        for pos, value in level:
            self.board[pos].fixNumber(value)
            self.ui.IDs["SudokuTextBox" + str(pos) + "_"].imgdisplay=True
            self.ui.IDs["SudokuTextBox" + str(pos) + "_"].settext('{"'+value+'" underlined=True}')
        # noteBoard = self.assignHeuristic()[0]
        # for pos, x in enumerate(noteBoard):
        #    for n in x.Notes:
        #        text = self.ui.maketext(0, 0, str(n), ID= "Note" + str(n) + "_", anchor=(
        #            "w/3*" + str((int(n) - 1) % 3), "h/3*" + str((int(n) - 1) // 3)),
        #                                textsize=20 * 9 / (self.boxWidth * self.boxesX))
        #        self.ui.IDs["SudokuTextBox" + str(pos) + "_"].binditem(text)

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
            # Stops the hint tile being green
            if self.currentHint != None:
                self.ui.IDs["SudokuTextBox" + str(self.currentHint) + "_"].col = pyui.Style.defaults['col']
                self.ui.IDs["SudokuTextBox" + str(self.currentHint) + "_"].refresh()
                self.currentHint = None

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
                            # If the new character isn't valid, returns to the old character
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
                        Tile = SudokuTile(True, str(self.idIndex))
                        self.board.append(Tile)
                        func = pyui.funcer(datavalidation, textID="SudokuTextBox" + str(self.idIndex) + "_", Tile=Tile)
                        TextBoxLine.append(self.ui.maketextbox(0, 0, ID="SudokuTextBox" + str(self.idIndex) + "_",
                                                               width=270 / self.boxesX / self.boxWidth, height=270 / self.boxesY / self.boxHeight, lines=1,
                                                               textcenter=True, textsize=90*9/(self.boxWidth*self.boxesX),
                                                               commandifkey=True,
                                                               command=func.func))
                        self.idIndex = self.idIndex + 1
                    TextBoxGrid.append(TextBoxLine)
                SubTableData = self.ui.maketable(0, 0, data=TextBoxGrid, backingcol=(0,0,0),
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
    def clearConflicts(self):
        for removeError in self.previousConflictNumbers:
            self.ui.IDs["SudokuTextBox" + str(removeError) + "_"].textcol = (0, 0, 0)
            self.ui.IDs["SudokuTextBox" + str(removeError) + "_"].refresh()
        self.previousConflictNumbers = set()
        self.clearConflictNotes()
    def clearConflictNotes(self):
        for removeNoteError in self.previousConflictNotes:
            try:
                # The notes conflicts are tuples (pos, value) so the ID of the text is slighly different.
                self.ui.IDs["SudokuTextBox" + str(removeNoteError[0]) + "_Note" + removeNoteError[1] + "_"].textcol \
                    = (0, 0, 0)
                self.ui.IDs["SudokuTextBox" + str(removeNoteError[0]) + "_Note" + removeNoteError[1] + "_"].refresh()
            except:
                continue
        self.previousConflictNotes = set()

    def updateErrors(self):
        removedConflicts = self.previousConflictNumbers - self.conflicts()[0]
        for removeError in removedConflicts:
            self.ui.IDs["SudokuTextBox" + str(removeError) + "_"].textcol = (0, 0, 0)
            self.ui.IDs["SudokuTextBox" + str(removeError) + "_"].refresh()
        self.previousConflictNumbers -= removedConflicts



    def gameLogic(self):
        self.errorCheckingLogic()
        self.updateTimer()

    def errorCheckingLogic(self):
        errorChecking = self.ui.IDs['SettingsDropdown'].active
        if errorChecking == "Check Button":
            self.updateErrors()
            self.clearConflictNotes()
            if not(self.renderingErrorCheckButton):
                self.ui.IDs["ShowErrors"].enabled = True
                self.renderingErrorCheckButton = True
            return
        if self.renderingErrorCheckButton:
            self.ui.IDs["ShowErrors"].enabled = False
            self.renderingErrorCheckButton = False

        if errorChecking == "Highlight Errors":
            self.highlightConflicts(False)
            if len(self.previousConflictNotes) != 0:
                self.clearConflictNotes()
            return
        elif errorChecking == 'Highlight Errors and Notes':
            self.highlightConflicts(True)
            return

        if errorChecking == "No Error Checking" and (len(self.previousConflictNumbers)!= 0
                                                       or len(self.previousConflictNotes) != 0):
            self.clearConflicts()



