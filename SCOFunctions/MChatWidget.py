import datetime
import threading
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

from SCOFunctions.MFilePath import innerPath


class ChatMessage():
    """ Class container for one message """
    def __init__(self, parent):
        self.empty = True
        self.height = 16
        self.value = (None, None, None)
        
        self.time = QtWidgets.QLabel(parent)
        self.time.setStyleSheet('color: #999')

        self.user = QtWidgets.QLabel(parent)
        font = parent.font()
        self.user.setFont(font)

        self.message = QtWidgets.QLabel(parent)
        self.message.setStyleSheet('color: white')
        self.message.setWordWrap(True)
        # This is telling it that the label can use the extra horizontal space
        self.message.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                        QtWidgets.QSizePolicy.MinimumExpanding)) 

        for item in {self.time,self.user,self.message}:
            item.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)


    def update(self, user, message, color):
        """ Update with new data"""
        if user == None:
            return
        self.empty = False
        self.value = (user, message, color)

        self.time.setText(datetime.datetime.now().strftime('%H:%M '))
        self.user.setText(user)
        self.user.setStyleSheet(f'color: {color}; font-weight: bold')
        self.message.setText(f": {message}")


class ChatWidget(QtWidgets.QWidget):
    """ Widget showing chat messages"""

    def __init__(self, geometry=None, parent=None):
        super().__init__(parent)

        if geometry == None:
            self.setGeometry(700, 300, 500, 500)
        else:
            self.setGeometry(*geometry)

        self.setWindowIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        self.setWindowTitle('Twitch chat position')

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowTransparentForInput|QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.CoverWindow|QtCore.Qt.NoDropShadowWindowHint|QtCore.Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        # Setting things up
        self.fixed = True
        font = self.font()
        font.setPointSize(int(font.pointSize()*1.3))
        self.setFont(font)
        self.max_messages = 15
        self.colors = ['#7878FF', '#FF5858', 'yellow', 'purple', '#DAA520', '#94C237', 'pink','#00E700','#ED551E']
        self.color_index = 0
        self.users = dict()

        # Adding layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignBottom)
        self.layout.setSpacing(0)
        # self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        # Fill messages.
        # To be thread safe, all elements are already created, and updating will be just changing text.
        self.messages = list()
        self.layouts = list()

        for i in range(self.max_messages):
            new_widget = ChatMessage(self)
            new_layout = QtWidgets.QHBoxLayout()
            # new_layout.setAlignment(QtCore.Qt.AlignLeft)

            new_layout.addWidget(new_widget.time)
            new_layout.addWidget(new_widget.user)
            new_layout.addWidget(new_widget.message)
            # new_layout.setContentsMargins(0,0,0,0)

            self.layout.addLayout(new_layout)
            self.messages.append(new_widget)
            self.layouts.append(new_layout)

        # DEBUG
        import random
        for i in range(8):
            self.add_message(f'user_{"ag"*random.randint(0,2)}_{i}', 'asd '*random.randint(10,100))

        self.show()


    def get_user_color(self, user):
        """ Returns a color for a user. Assigns new if the user is new."""
        if not user in self.users:
            self.users[user] = self.colors[self.color_index]
            self.color_index += 1
            self.color_index = self.color_index if self.color_index < len(self.colors) else 0

        return self.users[user]


    def add_message(self, user, message):
        """ Adds a message to the widget"""
        color = self.get_user_color(user)

        # Go from the top
        for idx, widget in enumerate(self.messages):
            if idx < self.max_messages - 1:
                # Update upper widget with data from the one down
                next_widget = self.messages[idx+1]               
                widget.update(*next_widget.value)
            else:
                # When we reach bottom, update with our data
                widget.update(user, message, color)
