# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Dict, Final, List, Tuple, Union

from PyQt5.QtCore import QAbstractTableModel, QCoreApplication, QModelIndex, QVariant, Qt
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox, \
    QFormLayout, QFrame, QGridLayout, QLineEdit, QSpinBox, QTableView


class PlainTextImportDialog(QDialog):
    class TableModel(QAbstractTableModel):
        ROW_BATCH_COUNT: Final[int] = 10

        def __init__(self, parent=None):
            super().__init__(parent)
            self._data: List[Tuple[Union[str, int, float], ...]] = []
            self._header: Dict[int, Union[str, int, float]] = dict()
            self._rows_loaded: int = self.ROW_BATCH_COUNT

        def rowCount(self, parent=None):
            if self._data is None:
                return 0
            return len(self._data)

        def columnCount(self, parent=None):
            if self._data is None:
                return 0
            return len(self._header)

        def data(self, index, role=Qt.DisplayRole):
            if index.isValid():
                if role == Qt.DisplayRole:
                    return QVariant(str(self._data[index.row()][index.column()]))
            return QVariant()

        def set_data(self, new_data: List[Tuple[Union[str, int, float], ...]]):
            self._data = new_data

        def headerData(self, col, orientation, role=None):
            if orientation == Qt.Horizontal and role == Qt.DisplayRole:
                return self._header[col]
            return None

        def setHeaderData(self, section: int, orientation: Qt.Orientation, value, role: int = ...) -> bool:
            if orientation == Qt.Horizontal and role == Qt.DisplayRole and 0 <= section < len(self._header):
                self._header[section] = value
                return True
            return False

        def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:
            self.beginResetModel()
            data_column: Final[int] = {0: 1, 1: 3, 2: 5, 3: 7}[column]
            self._data.sort(key=lambda l: l[data_column], reverse=bool(order != Qt.AscendingOrder))
            self.endResetModel()

        def canFetchMore(self, index=QModelIndex()):
            return len(self._data) > self._rows_loaded

        def fetchMore(self, index=QModelIndex()):
            # https://sateeshkumarb.wordpress.com/2012/04/01/paginated-display-of-table-data-in-pyqt/
            reminder: int = len(self._data) - self._rows_loaded
            items_to_fetch: int = min(reminder, self.ROW_BATCH_COUNT)
            self.beginInsertRows(QModelIndex(), self._rows_loaded, self._rows_loaded + items_to_fetch - 1)
            self._rows_loaded += items_to_fetch
            self.endInsertRows()

    def __init__(self, file_name: str):
        super(PlainTextImportDialog, self).__init__()

        self._translate = QCoreApplication.translate

        self.setWindowModality(Qt.ApplicationModal)
        self.resize(594, 546)

        self.main_layout = QGridLayout(self)

        self.table_preview = QTableView(self)
        self.table_preview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_preview.setAlternatingRowColors(True)
        self.table_preview_model = self.TableModel()
        self.table_preview.setModel(self.table_preview_model)

        self.main_layout.addWidget(self.table_preview, 0, 0, 1, 1)

        self.frame_settings = QFrame(self)
        self.frame_settings.setFrameShape(QFrame.StyledPanel)
        self.frame_settings.setFrameShadow(QFrame.Raised)
        self.layout_settings = QGridLayout(self.frame_settings)

        self.frame_column_naming = QFrame(self.frame_settings)
        self.layout_column_naming = QFormLayout(self.frame_column_naming)

        self.text_column_prefix = QLineEdit(self.frame_column_naming)
        self.layout_column_naming.addRow(self._translate('PlainTextImportDialog', 'Column prefix:'),
                                         self.text_column_prefix)

        self.text_column_suffix = QLineEdit(self.frame_column_naming)
        self.layout_column_naming.addRow(self._translate('PlainTextImportDialog', 'Column suffix:'),
                                         self.text_column_suffix)

        self.layout_settings.addWidget(self.frame_column_naming, 3, 1, 1, 1)

        self.frame_skip = QFrame(self.frame_settings)
        self.layout_skip = QFormLayout(self.frame_skip)

        self.spin_skip_rows_before_header = QSpinBox(self.frame_skip)
        self.spin_skip_rows_before_header.setMaximum(999)
        self.layout_skip.addRow(self._translate('PlainTextImportDialog', 'Skip rows before header:'),
                                self.spin_skip_rows_before_header)

        self.check_has_header = QCheckBox(self.frame_skip)
        self.layout_skip.setWidget(1, QFormLayout.SpanningRole, self.check_has_header)
        self.check_has_units = QCheckBox(self.frame_skip)
        self.layout_skip.setWidget(2, QFormLayout.SpanningRole, self.check_has_units)

        self.spin_skip_rows_after_header = QSpinBox(self.frame_skip)
        self.spin_skip_rows_after_header.setMaximum(999)
        self.layout_skip.addRow(self._translate('PlainTextImportDialog', 'Skip rows after header:'),
                                self.spin_skip_rows_after_header)

        self.spin_skip_rows_at_bottom = QSpinBox(self.frame_skip)
        self.spin_skip_rows_at_bottom.setMaximum(999)
        self.layout_skip.addRow(self._translate('PlainTextImportDialog', 'Skip rows at bottom:'),
                                self.spin_skip_rows_at_bottom)

        self.text_skip_columns = QLineEdit(self.frame_skip)
        self.layout_skip.addRow(self._translate('PlainTextImportDialog', 'Skip columns:'), self.text_skip_columns)

        self.layout_settings.addWidget(self.frame_skip, 2, 0, 2, 1)

        self.layout_preview_rows = QFormLayout()
        self.spin_preview_rows = QSpinBox(self.frame_settings)
        self.spin_preview_rows.setMinimum(1)
        self.spin_preview_rows.setProperty('value', 10)
        self.layout_preview_rows.addRow(self._translate('PlainTextImportDialog', 'Rows in the preview:'),
                                        self.spin_preview_rows)

        self.layout_settings.addLayout(self.layout_preview_rows, 1, 0, 1, 1)
        self.frame_separators = QFrame(self.frame_settings)

        self.layout_separators = QFormLayout(self.frame_separators)
        self.combo_separator = QComboBox(self.frame_separators)
        self.combo_separator.setEditable(True)
        self.combo_separator.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.combo_separator.addItem(self._translate('PlainTextImportDialog', 'comma (,)'))
        self.combo_separator.addItem(self._translate('PlainTextImportDialog', 'semicolon (;)'))
        self.combo_separator.addItem(self._translate('PlainTextImportDialog', 'space'))
        self.combo_separator.addItem(self._translate('PlainTextImportDialog', 'tab'))
        self.combo_separator.addItem(self._translate('PlainTextImportDialog', 'space or tab'))
        self.layout_separators.addRow(self._translate('PlainTextImportDialog', 'Separator:'), self.combo_separator)

        self.check_combine_separators = QCheckBox(self.frame_separators)
        self.layout_separators.setWidget(1, QFormLayout.SpanningRole, self.check_combine_separators)

        self.combo_comment = QComboBox(self.frame_separators)
        self.combo_comment.setEditable(True)
        self.combo_comment.setCurrentText('#')
        self.combo_comment.addItems(('#', ';', '%', '!'))
        self.layout_separators.addRow(self._translate('PlainTextImportDialog', 'Comment:'), self.combo_comment)

        self.combo_text_start = QComboBox(self.frame_separators)
        self.combo_text_start.setEditable(True)
        self.combo_text_start.setCurrentText("'")
        self.combo_text_start.addItems(('"', "'", '«', '„', '“', '‘', '`'))
        self.layout_separators.addRow(self._translate('PlainTextImportDialog', 'Text start:'), self.combo_text_start)

        self.combo_text_end = QComboBox(self.frame_separators)
        self.combo_text_end.setEditable(True)
        self.combo_text_end.setCurrentText("'")
        self.combo_text_end.addItems(('"', "'", '»', '”', '’', '`'))
        self.layout_separators.addRow(self._translate('PlainTextImportDialog', 'Text end:'), self.combo_text_end)

        self.layout_settings.addWidget(self.frame_separators, 1, 1, 2, 1)
        self.main_layout.addWidget(self.frame_settings, 2, 0, 1, 1)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Open)

        self.main_layout.addWidget(self.buttonBox, 5, 0, 1, 1)

        self.setWindowTitle(self._translate('PlainTextImportDialog', 'Plain Text Import'))
        self.text_skip_columns.setPlaceholderText(self._translate('PlainTextImportDialog', 'e.g., 1, 2, 4-6'))
        self.check_has_units.setText(self._translate('PlainTextImportDialog',
                                                     'The units are placed just after the header'))
        self.check_has_header.setText(self._translate('PlainTextImportDialog', 'The file has a header'))
        self.check_combine_separators.setText(self._translate('PlainTextImportDialog', 'Combine separators'))
        self.combo_comment.setToolTip(self._translate('PlainTextImportDialog',
                                                      'This marks comment lines. Separate multiple marks with spaces.'))

        self.adjustSize()

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        # QMetaObject.connectSlotsByName(self)

        self._file_name: Path = Path(file_name)

    # def try_loading(self):
    #     if not self._file_name.exists():
    #         self.table_preview.set


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    print(PlainTextImportDialog('/home/stsav012/Projects/degree work 3/data/histograms/histogram data cw+ '
                                'γ=0.0010 i_osc=1.0000 i_bias=0.5000 ω=1.3900 α=0.1000 T_max=900, phase.csv').exec())
