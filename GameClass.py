import pygame, math, random, sys, os
from DefaultSudoku import DefaultSudoku
from UIpygame import PyUI as pyui
import pygame

class GameClass:
    def __init__(self, ui: pyui.UI):

        self.activeVariant = False
        self.ui = ui
        # Button and window that opens from the right for a friends list
        ui.makebutton(1000, 10, text="Friends", command=lambda: ui.movemenu('Friends', 'left'))
        ui.makewindowedmenu(900, 0, 300, 900, 'Friends', ID="FriendsList")

        # Adds the text at the top of each navigation menu that informs the user where they are at
        ui.maketext(100, 50, "Games")
        ui.maketext(100, 50, "Variations", menu="MineSweeper")
        ui.maketext(100, 50, "Variations", menu="Sudoku")

        # Back buttons for all the submenus
        ui.makebutton(10, 10, text="Exit", command=lambda: exit())
        ui.makebutton(10, 10, text="Back", menu="Sudoku", command=lambda: ui.menuback())
        ui.makebutton(10, 10, text="Back", menu="MineSweeper", command=lambda: ui.menuback())

        # Opens the next sub menu menu from the right of the screen
        ui.makebutton(100, 100, text="Sudoku", command=lambda: ui.movemenu('Sudoku', 'left'))
        ui.makebutton(100, 150, text="MineSweeper", command=lambda: ui.movemenu('MineSweeper', 'left'))

        # list of all the sudoku variant names in a dictionary, so it can initiate the object
        self.sudokuVariants = {"Sudoku": DefaultSudoku}
        for index, Variant in enumerate(self.sudokuVariants.keys()):
            # Buttons on the Sudoku submenu to open variants
            ui.makebutton(100, 100 + 50 * index, text=Variant, menu="Sudoku",
                          command=lambda: openSudokuVariant(Variant))


        def openSudokuVariant(Variant):
            if 'auto_generate_menu:SudokuLevelSelector' in ui.IDs:
                ui.delete(ID='auto_generate_menu:SudokuLevelSelector')
            ui.maketext(100, 50, "Levels", menu="SudokuLevelSelector")
            ui.makebutton(10, 10, ID="BackLevel", text="Back", menu="SudokuLevelSelector", command= self.ui.menuback)
            # Will eventually fetch number of levels from a database.
            for levelNum in range(2):
                func = pyui.funcer(openLevel, variant=Variant, levelNum=levelNum)
                ui.makebutton(100, 100 + 50 * levelNum, text="Level "+ str(levelNum+1), menu="SudokuLevelSelector",
                              command=func.func)
            self.ui.movemenu('SudokuLevelSelector', 'left')
            self.ui.deltatime = 60 * self.ui.timetracker

        def openLevel(variant, levelNum):
            # If a sudoku window already exists, deletes it
            if 'auto_generate_menu:SudokuGame' in ui.IDs:
                ui.delete(ID='auto_generate_menu:SudokuGame')
                ui.delete(ID="PausedMenu")
                ui.delete(ID="SettingsMenu")
            # Opens the menu for Sudoku, places a back button on it
            ui.makebutton(10, 10, ID="ExitGame", text="Back", menu="SudokuGame", command=lambda: closeSudokuVariant())
            # Initialises the class that is responsible for that particular variant
            self.activeVariant = self.sudokuVariants.get(variant)(self.ui, levelNum)
            self.ui.movemenu('SudokuGame', 'left')
            self.ui.deltatime = 60 * self.ui.timetracker

        def closeSudokuVariant():
            ui.menuback()
            self.activeVariant.close()
            self.activeVariant = False
            print(self.activeVariant)
            #print(ui.printtree(), end="\n\n\n")
    def gameLoop(self):
        # Checks if there is an active variant running
        if self.activeVariant != False:
            self.activeVariant.updateTimer()


