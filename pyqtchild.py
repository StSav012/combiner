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
from typing import Dict, List

from PyQt5.QtCore import QFile, QFileInfo, QTextStream, Qt
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QInputDialog, QMenu, QMessageBox
from pyqtgraph import PlotWidget, ViewBox, mkPen

from irtecon_file import IRTECONFile


class MDIChildPlot(PlotWidget):
    LINE_COLORS: List[str] = ['r', 'g', 'b', 'c', 'm', 'y', 'w']
    AXES_NAMES: Dict[int, str] = {2: 'bottom', 3: 'left', 4: 'right'}

    child_number: int = 1

    def __init__(self, **kwargs):
        super(MDIChildPlot, self).__init__(**kwargs)

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.is_untitled: bool = True
        self.is_modified: bool = False

        self.cur_file: str = ''

        self.curves = []

        self.plotItem2 = ViewBox()
        self.plotItem.showAxis('right')
        self.plotItem.scene().addItem(self.plotItem2)
        self.plotItem.getAxis('right').linkToView(self.plotItem2)
        self.plotItem2.setXLink(self.plotItem)
        self.plotItem.showButtons()
        self.plotItem.showGrid(x=True, y=True)

        # Handle view resizing
        def update_views():
            # view has resized; update auxiliary views to match
            self.plotItem2.setGeometry(self.plotItem.vb.sceneBoundingRect())

            # need to re-update linked axes since this was called
            # incorrectly while views had different shapes.
            # (probably this should be handled in ViewBox.resizeEvent)
            self.plotItem2.linkedViewChanged(self.plotItem.vb, self.plotItem2.XAxis)

        update_views()
        self.plotItem.vb.sigResized.connect(update_views)

        # add items to the context menu
        self.plotItem.vb.menu.addSeparator()
        self.delete_curve_menu: QMenu = QMenu('Delete')
        self.copy_curve_menu: QMenu = QMenu('Copy')
        self.paste_curve_menu: QMenu = QMenu('Paste')
        menus = {self.delete_curve_menu:
                 [('Last Curve…', self.delete_last_curve),
                  ('Curves No.…', self.delete_curves),
                  ('All Curves…', self.delete_all_curves)],
                 self.copy_curve_menu:
                 [('Last Curve…', self.copy_last_curve),
                  ('Curves No.…', self.copy_curves),
                  ('All Curves…', self.copy_all_curves)],
                 }
        for parent_menu, actions in menus.items():
            for title, callback in actions:
                new_action: QAction = QAction(title, parent_menu)
                parent_menu.addAction(new_action)
                new_action.triggered.connect(callback)
        self.plotItem.vb.menu.addMenu(self.delete_curve_menu)
        self.plotItem.vb.menu.addMenu(self.copy_curve_menu)
        self.plotItem.vb.menu.addMenu(self.paste_curve_menu)

        # hide buggy menu items
        for undesired_menu_item_index in (5, 2, 1):
            self.plotItem.subMenus.pop(undesired_menu_item_index)
        self.plotItem.subMenus[1].actions()[0].defaultWidget().children()[1].hide()

    def new_file(self):
        self.is_untitled = True
        self.cur_file = f'Plot {MDIChildPlot.child_number:d}'
        MDIChildPlot.child_number += 1
        self.setWindowTitle(self.cur_file + '[*]')
        self.setWindowModified(True)

        # self.sig.connect(self.document_was_modified)

    def load_irtecon_file(self, file_name: str):
        file = QFile(file_name)
        if not file.open(QFile.ReadOnly | QFile.Text):
            QMessageBox.warning(self, 'MDI',
                                f'Cannot read file {file_name}:\n{file.errorString()}.')
            return False

        QApplication.setOverrideCursor(Qt.WaitCursor)
        in_str = QTextStream(file).readAll()
        file_data = IRTECONFile(in_str)
        self.plotItem.setTitle(file_data.sample_name)
        self.plotItem.addLegend()
        for index, curve in enumerate(file_data.curves):
            self.curves.append(self.plotItem.plot(curve.data[..., :2],
                                                  name=curve.legend_key,
                                                  pen=mkPen(self.LINE_COLORS[index % len(self.LINE_COLORS)])))
        for ax in self.AXES_NAMES.values():
            self.plotItem.hideAxis(ax)
        for ax in file_data.axes:
            if ax.axis in self.AXES_NAMES:
                self.plotItem.showAxis(self.AXES_NAMES[ax.axis])
                self.plotItem.setLabel(self.AXES_NAMES[ax.axis], ax.name, ax.unit)
        QApplication.restoreOverrideCursor()

        self.set_current_file(file_name)

        # self.document().contentsChanged.connect(self.document_was_modified)

        return True

    def delete_last_curve(self):
        if not self.curves:
            return
        ret = QMessageBox.warning(self, 'MDI',
                                  'Do you want to delete the last curve?',
                                  QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.plotItem.legend.removeItem(self.curves[-1])
            self.curves[-1].clear()
            del self.curves[-1]
            self.is_modified = True
            self.setWindowTitle(self.user_friendly_current_file() + '[*]')
            self.setWindowModified(True)

    def delete_curves(self):
        def parse_range() -> List[int]:
            # https://stackoverflow.com/a/4248689/8554611
            result = set()
            for part in ranges.split(','):
                x = part.split('-')
                result.update(list(range(int(x[0]), int(x[-1]) + 1)))
            return sorted(result)
        if not self.curves:
            return
        ranges, ok = QInputDialog.getText(self, 'Delete Curves', 'Curves No.:')
        if ok:
            for index in reversed(parse_range()):
                index -= 1
                if index in range(len(self.curves)):
                    self.plotItem.legend.removeItem(self.curves[index])
                    self.curves[index].clear()
                    del self.curves[index]
            self.is_modified = True
            self.setWindowTitle(self.user_friendly_current_file() + '[*]')
            self.setWindowModified(True)

    def delete_all_curves(self):
        if not self.curves:
            return
        ret = QMessageBox.question(self, 'MDI',
                                   'Do you want to delete all the curves?',
                                   QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            while self.curves:
                self.plotItem.legend.removeItem(self.curves[-1])
                self.curves[-1].clear()
                del self.curves[-1]
            self.is_modified = True
            self.setWindowTitle(self.user_friendly_current_file() + '[*]')
            self.setWindowModified(True)

    def copy_last_curve(self):
        if not self.curves:
            return
        raise NotImplementedError

    def copy_curves(self, ranges: str):
        def parse_range() -> List[int]:
            # https://stackoverflow.com/a/4248689/8554611
            result = set()
            for part in ranges.split(','):
                x = part.split('-')
                result.update(list(range(int(x[0]), int(x[-1]) + 1)))
            return sorted(result)
        if not self.curves:
            return
        parse_range()
        raise NotImplementedError

    def copy_all_curves(self):
        if not self.curves:
            return
        raise NotImplementedError

    def save(self):
        if self.is_untitled:
            return self.save_as()
        else:
            return self.save_file(self.cur_file)

    def save_as(self):
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save As',
                                                   self.cur_file)
        if not file_name:
            return False

        return self.save_file(file_name)

    def save_file(self, file_name: str):
        file = QFile(file_name)

        if not file.open(QFile.WriteOnly | QFile.Text):
            QMessageBox.warning(self, 'MDI',
                                f'Cannot write file {file_name}:\n{file.errorString()}.')
            return False

        out_str = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        out_str << self.toPlainText()
        QApplication.restoreOverrideCursor()

        self.set_current_file(file_name)
        return True

    def user_friendly_current_file(self):
        def stripped_name(full_file_name):
            return QFileInfo(full_file_name).fileName()

        return stripped_name(self.cur_file)

    def current_file(self):
        return self.cur_file

    def close_event(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()

    def maybe_save(self):
        if self.document().isModified():
            ret = QMessageBox.warning(self, 'MDI',
                                      f'"{self.user_friendly_current_file()}" has been modified.\n'
                                      'Do you want to save your changes?',
                                      QMessageBox.Save | QMessageBox.Discard |
                                      QMessageBox.Cancel)
            if ret == QMessageBox.Save:
                return self.save()
            elif ret == QMessageBox.Cancel:
                return False

        return True

    def set_current_file(self, file_name):
        self.cur_file = QFileInfo(file_name).canonicalFilePath()
        self.is_untitled = False
        self.is_modified = False
        self.setWindowModified(False)
        self.setWindowTitle(self.user_friendly_current_file())
