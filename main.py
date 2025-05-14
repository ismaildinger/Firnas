from arayuz.main_gui import DefenseUI
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DefenseUI()
    window.show()
    sys.exit(app.exec_())