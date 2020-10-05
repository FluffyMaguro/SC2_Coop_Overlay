import time
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

from SCOFunctions.MFilePath import innerPath


class ChatMessage():
    """ Class container for one message line (time, user, message) """
    def __init__(self, parent):
        self.empty = True
        self.height = 16
        self.value = (None, None, None)
        
        self.time = QtWidgets.QLabel()
        self.time.setStyleSheet('color: #999')

        self.user = QtWidgets.QLabel()
        font = parent.font()
        self.user.setFont(font)

        self.message = QtWidgets.QLabel()
        self.message.setStyleSheet('color: white')
        self.message.setWordWrap(True)
        # This is telling it that the label can use the extra horizontal space, and can exand vertically as well
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

        # self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
        #                                 QtWidgets.QSizePolicy.Fixed)) 

        # self.setMaximumHeight(500)

        self.setWindowIcon(QtGui.QIcon(innerPath('src/OverlayIcon.ico')))
        self.setWindowTitle('Twitch chat position')

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowTransparentForInput|QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.CoverWindow|QtCore.Qt.NoDropShadowWindowHint|QtCore.Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        # Setting things up
        
        font = self.font()
        font.setPointSize(int(font.pointSize()*1.3))

        # self.setFont(font)
        self.fixed = True
        self.max_messages = 15
        self.colors = ['#7878FF', '#FF5858', 'yellow', 'purple', '#DAA520', '#94C237', 'pink','#00E700','#ED551E']
        self.color_index = 0
        self.users = dict()

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scroll_area.setStyleSheet('background-color: transparent')
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setGeometry(0,0,self.width(), self.height())
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        print(help(self.scroll_area))

        self.scroll_area_contents = QtWidgets.QWidget()
        # self.scroll_area_contents.setStyleSheet('background-color: green')
        self.scroll_area.setWidget(self.scroll_area_contents)



        # self.scroll_area.setAlignment(QtCore.Qt.AlignBottom)
        # self.scroll_area.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                            # QtWidgets.QSizePolicy.Expanding)) 

        # self.main_layout = QtWidgets.QHBoxLayout()
        # self.main_layout.addWidget(self.scroll_area)
        # self.main_layout.setContentsMargins(0,0,0,0)
        # self.main_layout.setAlignment(QtCore.Qt.AlignBottom)
        # self.setLayout(self.main_layout)




        # self.scroll_area.setWidgetResizable(True)



        # self.scroll_area_contents.setGeometry(QtCore.QRect(0, 0, self.width(), self.height()))

        # self.scroll_area_contents.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                    # QtWidgets.QSizePolicy.Expanding)) 



        # self.scroll_area_layout = QtWidgets.QVBoxLayout()
        # self.scroll_area_layout.addWidget(self.scroll_area_contents)
        # self.scroll_area_layout.setContentsMargins(0,0,0,0)
        # # self.scroll_area_layout.setAlignment(QtCore.Qt.AlignBottom)
        # self.scroll_area.setLayout(self.scroll_area_layout)




        self.scroll_area_contents_layout = QtWidgets.QVBoxLayout()
        self.scroll_area_contents.setLayout(self.scroll_area_contents_layout)

        # self.scroll_area_contents_layout.setAlignment(QtCore.Qt.AlignBottom)
        # self.scroll_area_contents_layout.setContentsMargins(0,0,0,0)


        # Fill messages.
        # To be thread safe, all elements are already created, and updating will be just changing text.
        self.messages = list()
        self.layouts = list()

        for i in range(self.max_messages):
            new_widget = ChatMessage(self.scroll_area_contents)
            new_layout = QtWidgets.QHBoxLayout()
            new_layout.setAlignment(QtCore.Qt.AlignLeft)

            new_layout.addWidget(new_widget.time)
            new_layout.addWidget(new_widget.user)
            new_layout.addWidget(new_widget.message)
            # new_layout.setContentsMargins(0,0,0,0)

            self.scroll_area_contents_layout.addLayout(new_layout)
            self.messages.append(new_widget)
            self.layouts.append(new_layout)

        # DEBUG
        import random
        for i in range(8):
            self.add_message(f'user_{"ag"*random.randint(0,2)}_{i}', 'asd '*random.randint(10,100))

        # Finalize
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


        """ 
        Let's add a small delay for the message widget to expand.
        This is happening on the Twitch bot thread, so it won't interfere with the main UI.
        Otherwise we woudl use QtCore.QTimer() if we were on the main thread. 
        """
        time.sleep(0.01)
        bar = self.scroll_area.verticalScrollBar()
        bar.setValue(bar.maximum())

