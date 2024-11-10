from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
import sys, os


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ButtonOperate:
    def __init__(self, ui):
        self.ui = ui
        # 主界面的所有按钮
        self.handlerButtton()

    def handlerButtton(self):
        # header操作
        self.headerHandler()

    def headerHandler(self):
        def addHeader():
            # 在表格末尾添加一行
            rowPosition = self.ui.headTable.rowCount()
            self.ui.headTable.insertRow(rowPosition)
        def subHeader():
            # 删除选中的行，如果没有选中行则删除最后一行
            selected_rows = self.ui.headTable.selectionModel().selectedIndexes()
            if selected_rows:
                for index in reversed(selected_rows):
                    self.ui.headTable.removeRow(index.row())
            else:
                rowPosition = self.ui.headTable.rowCount()
                self.ui.headTable.removeRow(rowPosition - 1)

        self.ui.headAddButton.clicked.connect(addHeader)
        self.ui.headSubButton.clicked.connect(subHeader)

class Stats:

    def __init__(self):
        ui_file_path = resource_path('ui/httpclient.ui')
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(ui_file)
        ui_file.close()
        # 按钮的信号和槽
        ButtonOperate(self.ui)

app = QApplication([])
stats = Stats()
stats.ui.show()
app.exec_()