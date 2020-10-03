import datetime
import threading
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets


class ChatMessage(QtWidgets.QWidget):
    """ """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.empty = True
        self.height = 11
        self.setStyleSheet('color: white')
        self.setGeometry(0, 0, 500, self.height)
        self.setMinimumHeight(self.height)
        self.setMaximumHeight(self.height)

        self.time = QtWidgets.QLabel(self)
        self.time.setGeometry(0, 0, 40, self.height)
        self.time.setStyleSheet('color: #999')
        self.user = QtWidgets.QLabel(self)
        self.user.setGeometry(38, 0, 140, self.height)
        self.message = QtWidgets.QLabel(self)
        self.message.setGeometry(120, 0, 450, 60)
        self.message.setWordWrap(True)


    def update(self, user, message, color):
        self.empty = False
        self.value = (user, message, color)

        self.time.setText(datetime.datetime.now().strftime('%H:%M'))
        self.user.setText(user)
        self.user.setStyleSheet(f'color: {color}; font-weight: bold')
        self.message.setText(f": {message}")
        self.message.setGeometry(53+int(len(user)*6), 0, 450, self.height)


class ChatWidget(QtWidgets.QWidget):
    """ Widget showing chat messages"""

    def __init__(self, max_messages=15, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 500, 500)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowTransparentForInput|QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.CoverWindow|QtCore.Qt.NoDropShadowWindowHint|QtCore.Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        # Setting things up
        font = self.font()
        font.setPointSize(int(font.pointSize()*1.3))
        self.setFont(font)
        self.max_messages = max_messages
        self.colors = ['#7878FF', '#FF5858', 'yellow', 'purple', '#DAA520', '#94C237', 'pink','#00E700','#ED551E']
        self.color_index = 0
        self.users = dict()

        # Adding layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignBottom)
        self.setLayout(self.layout)

        # Fill messages.
        # To be thread safe, all elements are already created, and updating will be just changing text.
        self.messages = list()
        for i in range(self.max_messages):
            new_widget = ChatMessage(parent=self)
            self.layout.addWidget(new_widget)
            self.messages.append(new_widget)

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
        print(f'adding message {message}')

        # In case messages aren't fully filled, add to the end

        # !! REMAKE ITERATION
        # I want to update from down
        if self.messages[self.max_messages-1].empty:
            for idx in range(len(self.messages),-1):
                if widget.empty:
                    widget.update(user, message, color)
                    return

        # Otherwise move text upwards
        for idx, widget in enumerate(self.messages):
            if idx == self.max_messages - 1:
                widget.update(user, message, color)
                return
            else:
                widget.update(*self.messages[idx+1].value)