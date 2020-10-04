import datetime
import threading
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets


class ChatMessage(QtWidgets.QWidget):
    """ """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.empty = True
        self.height = 16
        self.value = (None, None, None)
        self.setStyleSheet('color: white')
        self.setGeometry(0, 0, 500, self.height)
        self.setMinimumHeight(self.height)
        self.setMaximumHeight(self.height)

        self.time = QtWidgets.QLabel(self)
        self.time.setGeometry(0, 0, 40, self.height)
        self.time.setStyleSheet('color: #999')

        self.user = QtWidgets.QLabel(self)
        self.user.setGeometry(40, 0, 140, self.height)

        self.message = QtWidgets.QLabel(self)
        self.message.setGeometry(120, 0, 200, 60)
        self.message.setWordWrap(True)

        for item in {self.time, self.user, self.message}:
            item.setAlignment(QtCore.Qt.AlignVCenter)


    def update(self, user, message, color):
        if user == None:
            return
        self.empty = False
        self.value = (user, message, color)

        self.time.setText(datetime.datetime.now().strftime('%H:%M'))
        self.user.setText(user)
        self.user.setStyleSheet(f'color: {color}; font-weight: bold')
        self.message.setText(f": {message}")
        self.message.setGeometry(55+int(len(user)*6), 0, 450, self.height)


class ChatWidget(QtWidgets.QWidget):
    """ Widget showing chat messages"""

    def __init__(self, geometry=None, parent=None):
        super().__init__(parent)

        if geometry == None:
            self.setGeometry(700, 300, 500, 500)
        else:
            self.setGeometry(*geometry)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowTransparentForInput|QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.CoverWindow|QtCore.Qt.NoDropShadowWindowHint|QtCore.Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        # Setting things up
        self.fixed = True
        font = self.font()
        font.setPointSize(int(font.pointSize()*1.4))
        self.setFont(font)
        self.max_messages = 15
        self.colors = ['#7878FF', '#FF5858', 'yellow', 'purple', '#DAA520', '#94C237', 'pink','#00E700','#ED551E']
        self.color_index = 0
        self.users = dict()

        # Adding layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignBottom)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # Fill messages.
        # To be thread safe, all elements are already created, and updating will be just changing text.
        self.messages = list()
        for i in range(self.max_messages):
            new_widget = ChatMessage(parent=self)
            self.layout.addWidget(new_widget)
            self.messages.append(new_widget)

        # DEBUG
        import random
        for i in range(8):
            self.add_message(f'user_{"ag"*random.randint(0,2)}_{i}', 'asd'*random.randint(10,20))

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
