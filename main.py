#!/usr/bin/env python
# -*- coding: utf-8 -*-

############################################################################
#
#  Copyright (C) 2004-2005 Trolltech AS. All rights reserved.
#
#  This file is part of the example classes of the Qt Toolkit.
#
#  This file may be used under the terms of the GNU General Public
#  License version 2.0 as published by the Free Software Foundation
#  and appearing in the file LICENSE.GPL included in the packaging of
#  self file.  Please review the following information to ensure GNU
#  General Public Licensing requirements will be met:
#  http://www.trolltech.com/products/qt/opensource.html
#
#  If you are unsure which license is appropriate for your use, please
#  review the following information:
#  http://www.trolltech.com/products/qt/licensing.html or contact the
#  sales department at sales@trolltech.com.
#
#  This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
#  WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
############################################################################

from PyQt5.QtCore import QPoint, QSettings, QSignalMapper, QSize, Qt, QFileInfo
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QMainWindow, QMdiArea, QMessageBox, qApp, QStyle

from plain_text_import_dialog import PlainTextImportDialog
from pyqtchild import MDIChildPlot


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.update_menus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped.connect(self.set_active_sub_window)

        self.newAct = QAction(self)
        self.newAct.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        # self.newAct.setIcon(QIcon(':/images/new.png'))
        self.newAct.setIconText('New')
        self.newAct.setShortcut(QKeySequence.New)
        self.newAct.setStatusTip('Create a new file')
        self.newAct.triggered.connect(self.new_file)

        self.openAct = QAction(self)
        self.openAct.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.openAct.setIconText('Open...')
        self.openAct.setShortcut(QKeySequence.Open)
        self.openAct.setStatusTip('Open an existing file')
        self.openAct.triggered.connect(self.open)

        self.saveAct = QAction(self)
        self.saveAct.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.saveAct.setIconText('Save')
        self.saveAct.setShortcut(QKeySequence.Save)
        self.saveAct.setStatusTip('Save the document to disk')
        self.saveAct.triggered.connect(self.save)

        self.saveAsAct = QAction(self)
        self.saveAsAct.setIconText('Save As...')
        self.saveAsAct.setShortcut(QKeySequence.SaveAs)
        self.saveAsAct.setStatusTip('Save the document under a new name')
        self.saveAsAct.triggered.connect(self.save_as)

        self.exitAct = QAction(self)
        self.exitAct.setIconText('Exit')
        self.exitAct.setShortcut(QKeySequence.Quit)
        self.exitAct.setStatusTip('Exit the application')
        self.exitAct.triggered.connect(qApp.closeAllWindows)

        self.cutAct = QAction(self)
        # self.cutAct.setIcon(QIcon(':/images/cut.png'))
        self.cutAct.setIconText('Cut')
        self.cutAct.setShortcut(QKeySequence.Cut)
        self.cutAct.setStatusTip("Cut the current selection's contents to the clipboard")
        self.cutAct.triggered.connect(self.cut)

        self.copyAct = QAction(self)
        # self.copyAct.setIcon(QIcon(':/images/copy.png'))
        self.copyAct.setIconText('Copy')
        self.copyAct.setShortcut(QKeySequence.Copy)
        self.copyAct.setStatusTip("Copy the current selection's contents to the clipboard")
        self.copyAct.triggered.connect(self.copy)

        self.pasteAct = QAction(self)
        # self.pasteAct.setIcon(QIcon(':/images/paste.png'))
        self.pasteAct.setIconText('Paste')
        self.pasteAct.setShortcut(QKeySequence.Paste)
        self.pasteAct.setStatusTip("Paste the clipboard's contents into the current selection")
        self.pasteAct.triggered.connect(self.paste)

        self.closeAct = QAction(self)
        self.closeAct.setIconText('Close')
        self.closeAct.setShortcut('Ctrl+W')
        self.closeAct.setStatusTip("Close the active window")
        self.closeAct.triggered.connect(self.mdiArea.closeActiveSubWindow)

        self.closeAllAct = QAction(self)
        self.closeAllAct.setIconText('Close All')
        self.closeAllAct.setStatusTip('Close all the windows')
        self.closeAllAct.triggered.connect(self.mdiArea.closeAllSubWindows)

        self.tileAct = QAction(self)
        self.tileAct.setIconText('Tile')
        self.tileAct.setStatusTip('Tile the windows')
        self.tileAct.triggered.connect(self.mdiArea.tileSubWindows)

        self.cascadeAct = QAction(self)
        self.cascadeAct.setIconText('Cascade')
        self.cascadeAct.setStatusTip('Cascade the windows')
        self.cascadeAct.triggered.connect(self.mdiArea.cascadeSubWindows)

        self.nextAct = QAction(self)
        self.nextAct.setIconText('Next')
        self.nextAct.setShortcut(QKeySequence.NextChild)
        self.nextAct.setStatusTip('Move the focus to the next window')
        self.nextAct.triggered.connect(self.mdiArea.activateNextSubWindow)

        self.previousAct = QAction(self)
        self.previousAct.setIconText('Previous')
        self.previousAct.setShortcut(QKeySequence.PreviousChild)
        self.previousAct.setStatusTip('Move the focus to the previous window')
        self.previousAct.triggered.connect(self.mdiArea.activatePreviousSubWindow)

        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QAction(self)
        self.aboutAct.setIconText('About')
        self.aboutAct.setStatusTip("Show the application's About box")
        self.aboutAct.triggered.connect(self.about)

        self.aboutQtAct = QAction(self)
        self.aboutQtAct.setIconText('About Qt')
        self.aboutQtAct.setStatusTip("Show the Qt library's About box")
        self.aboutQtAct.triggered.connect(qApp.aboutQt)

        self.fileMenu = self.menuBar().addMenu('File')
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        action = self.fileMenu.addAction('Switch layout direction')
        action.triggered.connect(self.switch_layout_direction)
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu('Edit')
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)

        self.windowMenu = self.menuBar().addMenu('Window')
        self.update_window_menu()
        self.windowMenu.aboutToShow.connect(self.update_window_menu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu('Help')
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.file_tool_bar = self.addToolBar('File')
        self.file_tool_bar.addAction(self.newAct)
        self.file_tool_bar.addAction(self.openAct)
        self.file_tool_bar.addAction(self.saveAct)

        self.edit_tool_bar = self.addToolBar('Edit')
        self.edit_tool_bar.addAction(self.cutAct)
        self.edit_tool_bar.addAction(self.copyAct)
        self.edit_tool_bar.addAction(self.pasteAct)

        self.statusBar().showMessage('Ready')

        self.update_menus()

        self.settings = QSettings('SavSoft', 'Combiner')

        self.last_directory: str = ''
        self.read_settings()

        self.setWindowTitle('MDI')
        self.setUnifiedTitleAndToolBarOnMac(True)

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.active_mdi_child():
            event.ignore()
        else:
            self.write_settings()
            event.accept()

    def new_file(self):
        child = self.create_mdi_child()
        child.new_file()
        child.show()

    def open(self):
        filters = ['IRTECON files (*.grd)', 'Plain text files (*.csv *.tsv *.dat *.txt)']
        file_name, _ = QFileDialog.getOpenFileName(self, filter=';;'.join(filters),
                                                   directory=self.last_directory,
                                                   options=QFileDialog.DontUseNativeDialog)
        if file_name:
            child = self.create_mdi_child()
            if QFileInfo(file_name).suffix() == 'grd':
                if child.load_irtecon_file(file_name):
                    self.statusBar().showMessage('File loaded', 2000)
                    self.last_directory = QFileInfo(file_name).dir().absolutePath()
                    child.show()
                else:
                    child.close()
            else:
                print(PlainTextImportDialog(file_name).exec())
                raise NotImplementedError

    def save(self):
        if self.active_mdi_child() and self.active_mdi_child().save():
            self.statusBar().showMessage('File saved', 2000)

    def save_as(self):
        if self.active_mdi_child() and self.active_mdi_child().save_as():
            self.statusBar().showMessage('File saved', 2000)

    def cut(self):
        if self.active_mdi_child():
            self.active_mdi_child().cut()

    def copy(self):
        if self.active_mdi_child():
            self.active_mdi_child().copy()

    def paste(self):
        if self.active_mdi_child():
            self.active_mdi_child().paste()

    def about(self):
        QMessageBox.about(self, 'About MDI',
                          'The <b>MDI</b> example demonstrates how to write multiple '
                          'document interface applications using Qt.')

    def update_menus(self):
        has_mdi_child = (self.active_mdi_child() is not None)
        self.saveAct.setEnabled(has_mdi_child)
        self.saveAsAct.setEnabled(has_mdi_child)
        self.pasteAct.setEnabled(has_mdi_child)
        self.closeAct.setEnabled(has_mdi_child)
        self.closeAllAct.setEnabled(has_mdi_child)
        self.tileAct.setEnabled(has_mdi_child)
        self.cascadeAct.setEnabled(has_mdi_child)
        self.nextAct.setEnabled(has_mdi_child)
        self.previousAct.setEnabled(has_mdi_child)
        self.separatorAct.setVisible(has_mdi_child)

    def update_window_menu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.mdiArea.subWindowList()
        self.separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = f'{i + 1:d} {child.user_friendly_current_file()}'
            if i < 9:
                text = '' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child == self.active_mdi_child())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def create_mdi_child(self):
        child = MDIChildPlot()
        self.mdiArea.addSubWindow(child)
        return child

    def read_settings(self):
        pos = self.settings.value('pos', QPoint(200, 200))
        self.move(pos)
        size = self.settings.value('size', QSize(400, 400))
        self.resize(size)
        self.last_directory = self.settings.value('directory', '')

    def write_settings(self):
        self.settings.setValue('pos', self.pos())
        self.settings.setValue('size', self.size())
        self.settings.setValue('directory', self.last_directory)

    def active_mdi_child(self):
        active_sub_window = self.mdiArea.activeSubWindow()
        if active_sub_window:
            return active_sub_window.widget()
        return None

    def switch_layout_direction(self):
        if self.layoutDirection() == Qt.LeftToRight:
            qApp.setLayoutDirection(Qt.RightToLeft)
        else:
            qApp.setLayoutDirection(Qt.LeftToRight)

    def set_active_sub_window(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
