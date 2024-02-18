class SudokuTile():
    def __init__(self, editable, TileID):
        self.Number = ""
        self.Notes = []
        self.editable = editable

    #Sets the number of the tile when typed
    def setNumber(self, Number):
        if self.editable:
            self.Number = Number
            return True
        else:
            return False

    #Toggles wether the value appears within notes
    def toggleNote(self, Number):
        if self.editable:
            if Number in self.Notes:
                self.Notes.remove(Number)
            else:
                self.Notes.append(Number)
            return True
        else:
            False

    # Emptys all notes
    def clearNotes(self):
        self.Notes = []

    # Used for the original sudoku to make immutable tiles
    def fixNumber(self, Number):
        self.Number=str(Number)
        self.editable = False