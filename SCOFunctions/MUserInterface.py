from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QKeySequenceEdit
 
 
class CustomKeySequenceEdit(QKeySequenceEdit):
    def __init__(self, parent=None):
        super(CustomKeySequenceEdit, self).__init__(parent)
 
    def keyPressEvent(self, QKeyEvent):
        super(CustomKeySequenceEdit, self).keyPressEvent(QKeyEvent)
        value = self.keySequence()
        self.setKeySequence(QKeySequence(value))