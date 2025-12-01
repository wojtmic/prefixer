from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QStatusBar
from PyQt6.QtCore import QThread
import sys
from .dialog import SelectGameDialog
from prefixer.core import steam

class PrefixerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Prefixer')
        self.setMinimumSize(1280, 720)

        self.pfx_path = ''
        self.binary_path = ''
        self.configinfo = ''
        self.game_path = ''

        self.menu_bar()

    def menu_bar(self):
        self.setStatusBar(QStatusBar(self))
        bar = self.menuBar()

        file_menu = bar.addMenu('&File')

        select_game_action = QAction('&Select game', self)
        select_game_action.setStatusTip('Select the target game')
        select_game_action.triggered.connect(self.select_game)

        file_menu.addAction(select_game_action)

    def select_game(self):
        dialog = SelectGameDialog()
        dialog.exec()

        data = dialog.selected_data # pfx_path, configInfo, binaryPath, game['appid']

        self.pfx_path = data[0]
        self.configinfo = data[1]
        self.binary_path = data[2]
        self.game_path = steam.get_installdir(data[3])

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = PrefixerWindow()
    window.show()

    sys.exit(app.exec())
