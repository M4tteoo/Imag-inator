from PySide6.QtWidgets import QApplication
from app_logic import MyApp


if __name__ == "__main__":
    app = QApplication([])
    my_app = MyApp()
    my_app.show()
    app.exec()

