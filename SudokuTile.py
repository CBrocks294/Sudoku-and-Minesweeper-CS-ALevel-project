class SudokuTile():
    def __init__(self, editable):
        self.Number = 0
        self.Notes = []
        self.editable = editable

    def setNumber(self, Number):
        if self.editable:
            self.Number = Number
            return True
        else:
            return False
    def toggleNote(self, Number):
        if self.editable:
            if Number in self.Notes:
                self.Notes.remove(Number)
            else:
                self.Notes.append(Number)
            return True
        else:
            False