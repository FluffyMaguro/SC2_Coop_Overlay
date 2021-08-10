from PyQt5 import QtWidgets, QtGui, QtCore
from SCOFunctions.MFilePath import innerPath
from SCOFunctions.MDebugWindow import DebugWindow


class LinkTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.p = parent

        # Reset keyboard threads
        self.bt_reset_keyboard = QtWidgets.QPushButton(self)
        self.bt_reset_keyboard.setGeometry(QtCore.QRect(830, 15, 125, 25))
        self.bt_reset_keyboard.setText('Reset keyboard')
        self.bt_reset_keyboard.setToolTip('Resets keyboard threads.\nThis might fix issues if hotkeys are not reacting.')
        self.bt_reset_keyboard.clicked.connect(self.p.reset_keyboard_thread)

        # Debug
        self.bt_debug_window = QtWidgets.QPushButton(self)
        self.bt_debug_window.setGeometry(QtCore.QRect(830, 50, 125, 25))
        self.bt_debug_window.setText('Debug window')
        self.bt_debug_window.clicked.connect(self.debug_window_clicked)

        # Links
        self.fr_links = QtWidgets.QFrame(self)
        self.fr_links.setGeometry(QtCore.QRect(15, 15, 550, 235))
        self.fr_links.setAutoFillBackground(True)
        self.fr_links.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.fr_links.setFrameShadow(QtWidgets.QFrame.Plain)

        # Maguro.one
        self.img_blog = QtWidgets.QLabel(self.fr_links)
        self.img_blog.setGeometry(QtCore.QRect(30, 20, 31, 41))
        self.img_blog.setPixmap(QtGui.QPixmap(innerPath("src/maguro.jpg")))

        self.blog = QtWidgets.QLabel(self.fr_links)
        self.blog.setGeometry(QtCore.QRect(80, 20, 131, 41))
        self.blog.setText('<a href="www.maguro.one">Maguro.one</a>')

        # My discord
        self.img_discord = QtWidgets.QLabel(self.fr_links)
        self.img_discord.setGeometry(QtCore.QRect(30, 70, 41, 51))
        self.img_discord.setPixmap(QtGui.QPixmap(innerPath("src/mdiscord.png")))

        self.discord = QtWidgets.QLabel(self.fr_links)
        self.discord.setGeometry(QtCore.QRect(80, 80, 131, 31))
        self.discord.setText('<a href="https://discord.gg/FtGdhqD">My discord</a>')

        # Twitter
        self.img_twitter = QtWidgets.QLabel(self.fr_links)
        self.img_twitter.setGeometry(QtCore.QRect(30, 120, 41, 51))
        self.img_twitter.setPixmap(QtGui.QPixmap(innerPath("src/twitter.png")))

        self.twitter = QtWidgets.QLabel(self.fr_links)
        self.twitter.setGeometry(QtCore.QRect(80, 130, 160, 31))
        self.twitter.setText('<a href="https://twitter.com/FluffyMaguro">@FluffyMaguro</a>')

        # GitHub
        self.img_github = QtWidgets.QLabel(self.fr_links)
        self.img_github.setGeometry(QtCore.QRect(30, 175, 41, 41))
        self.img_github.setPixmap(QtGui.QPixmap(innerPath("src/github.png")))

        self.github = QtWidgets.QLabel(self.fr_links)
        self.github.setGeometry(QtCore.QRect(80, 175, 200, 41))
        self.github.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.github.setText('<a href="https://github.com/FluffyMaguro/SC2_Coop_overlay">Overlay on GitHub</a>')

        # Subreddit
        self.img_reddit = QtWidgets.QLabel(self.fr_links)
        self.img_reddit.setGeometry(QtCore.QRect(300, 20, 41, 41))
        self.img_reddit.setPixmap(QtGui.QPixmap(innerPath("src/reddit.png")))

        self.reddit = QtWidgets.QLabel(self.fr_links)
        self.reddit.setGeometry(QtCore.QRect(350, 20, 161, 41))
        self.reddit.setText('<a href="https://www.reddit.com/r/starcraft2coop/">Co-op subreddit</a>')

        # Forums
        self.img_battlenet = QtWidgets.QLabel(self.fr_links)
        self.img_battlenet.setGeometry(QtCore.QRect(300, 70, 41, 51))
        self.img_battlenet.setPixmap(QtGui.QPixmap(innerPath("src/sc2.png")))

        self.battlenet = QtWidgets.QLabel(self.fr_links)
        self.battlenet.setGeometry(QtCore.QRect(350, 80, 131, 31))
        self.battlenet.setText('<a href="https://us.forums.blizzard.com/en/sc2/c/co-op-missions-discussion">Co-op forums</a>')

        # Co-op discord
        self.img_coop_discord = QtWidgets.QLabel(self.fr_links)
        self.img_coop_discord.setGeometry(QtCore.QRect(300, 130, 31, 41))
        self.img_coop_discord.setPixmap(QtGui.QPixmap(innerPath("src/discord.png")))

        self.coop_discord = QtWidgets.QLabel(self.fr_links)
        self.coop_discord.setGeometry(QtCore.QRect(350, 130, 141, 31))
        self.coop_discord.setText('<a href="https://discord.gg/VQnXMdm">Co-op discord</a>')

        # Donate
        self.fr_donate = QtWidgets.QFrame(self)
        self.fr_donate.setGeometry(QtCore.QRect(15, 270, 550, 100))
        self.fr_donate.setAutoFillBackground(True)
        self.fr_donate.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.fr_donate.setFrameShadow(QtWidgets.QFrame.Plain)

        self.img_paypal = QtWidgets.QLabel(self.fr_donate)
        self.img_paypal.setGeometry(QtCore.QRect(210, 14, 200, 41))
        self.img_paypal.setPixmap(QtGui.QPixmap(innerPath("src/paypal.png")))

        self.paypal = QtWidgets.QLabel(self.fr_donate)
        self.paypal.setGeometry(QtCore.QRect(170, 47, 250, 41))
        self.paypal.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.paypal.setText('<a href="https://www.paypal.com/paypalme/FluffyMaguro">Donate if you feel generous</a>')

        # Styling
        for item in {self.blog, self.reddit, self.twitter, self.github, self.discord, self.battlenet, self.paypal, self.coop_discord}:
            item.setStyleSheet("font-size: 18px")
            item.setOpenExternalLinks(True)

    def debug_window_clicked(self):
        """ Creates, shows or hides debug window"""
        if hasattr(self.p, "DebugWindow"):
            if self.p.DebugWindow.isVisible():
                self.p.DebugWindow.hide()
            else:
                self.p.DebugWindow.show()
        else:
            self.p.DebugWindow = DebugWindow(self.p)