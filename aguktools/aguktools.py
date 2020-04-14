from collections import OrderedDict
import os
import sys

from PySide import QtCore, QtGui

from aguktools import gps_csv, textreplace, renamephotos, link_echo_data, __version__, checkisis, photopoints

FILL = '>'

TOOLS = OrderedDict(
    (('Reformat TBC CSV', gps_csv.HELP['full']),
    ('Clean DC file text', 'help text'),
    ('Link EACSD photos', 'help photos'),
    ('Link Echo Sounder Data', 'help echo'),
    ('Check ISIS banks', 'help banks'),
    ('Calculate photo point bearings', 'help pp'),
    ))


def main():
    app = QtGui.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    mainwindow.statusBar().showMessage(__version__)
    sys.exit(app.exec_())


def browse_for_file(parent, title, line_edit, file_filter=None):
    curr_path = line_edit.text()
    settings = QtCore.QSettings("AGUK", "AGUK tools")
    last_path = settings.value("LAST_PATH", ".")
    in_name, _ = QtGui.QFileDialog.getOpenFileName(parent, title, dir=curr_path or last_path, filter=file_filter)
    if in_name:
        settings.setValue("LAST_PATH", os.path.dirname(in_name))
        line_edit.setText(in_name or curr_path)


def browse_for_save_file(parent, title, line_edit, file_filter=None):
    curr_path = line_edit.text()
    settings = QtCore.QSettings("AGUK", "AGUK tools")
    last_path = settings.value("LAST_PATH", ".")
    in_name, _ = QtGui.QFileDialog.getSaveFileName(parent, title, dir=curr_path or last_path, filter=file_filter)
    if in_name:
        settings.setValue("LAST_PATH", os.path.dirname(in_name))
        line_edit.setText(in_name or curr_path)


def browse_for_dir(parent, title, line_edit):
    curr_path = line_edit.text()
    settings = QtCore.QSettings("AGUK", "AGUK tools")
    last_path = settings.value("LAST_PATH", ".")
    in_name = QtGui.QFileDialog.getExistingDirectory(parent, title, dir=curr_path or last_path)
    if in_name:
        settings.setValue("LAST_PATH", in_name)
        line_edit.setText(in_name or curr_path)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('AGUK Tools')
        self.resize(500, 400)

        self.central_widget = QtGui.QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QtGui.QGridLayout()
        self.central_widget.setLayout(self.main_layout)


        self.toolbox = ToolboxListWidget()
        self.main_layout.addWidget(self.toolbox, 0, 0)

        self.help_link = QtGui.QLabel('<a href=\"https://atlanticgeomatics.github.io/aguktools/\">Help</a>')
        self.help_link.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.help_link.setOpenExternalLinks(True)
        self.main_layout.addWidget(self.help_link)
        self.main_layout.addItem(QtGui.QSpacerItem(20, 40,
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding), 2, 0)

        self.tool_pane = QtGui.QGroupBox('Run')
        self.tool_lyt = QtGui.QVBoxLayout()
        self.tool_pane.setLayout(self.tool_lyt)

        self.info_pane = QtGui.QGroupBox('Help')
        self.info_lyt = QtGui.QVBoxLayout()
        self.info_pane.setLayout(self.info_lyt)
        self.help_text = QtGui.QLabel()

        self.info_lyt.addWidget(self.help_text)
        self.info_lyt.addItem(QtGui.QSpacerItem(20, 40,
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        self.main_layout.addWidget(self.tool_pane, 0, 1, 3, 1)

        self.toolbox.itemSelectionChanged.connect(self.update_tool_pane)

        self.tool_widget = None

    def update_tool_pane(self):
        try:
            self.tool_widget.setParent(None)
        except AttributeError:
            pass

        if self.toolbox.currentItem().text() == 'Reformat TBC CSV':
            self.run_tbc_csv_tool()
        elif self.toolbox.currentItem().text() == 'Clean DC file text':
            self.run_text_replace_tool()
        elif self.toolbox.currentItem().text() == 'Link EACSD photos':
            self.run_link_eacsd_photos_tool()
        elif self.toolbox.currentItem().text() == 'Link Echo Sounder Data':
            self.run_link_echo_data_tool()
        elif self.toolbox.currentItem().text() == 'Check ISIS banks':
            self.run_isis_checker_tool()
        elif self.toolbox.currentItem().text() == 'Calculate photo point bearings':
            self.run_photo_points_tool()

    def run_tbc_csv_tool(self):
        self.tool_widget = TBCCSVTool(self)
        self.tool_lyt.addWidget(self.tool_widget)

    def run_text_replace_tool(self):
        self.tool_widget = TextReplace(self)
        self.tool_lyt.addWidget(self.tool_widget)

    def run_link_eacsd_photos_tool(self):
        self.tool_widget = LinkEACSDPhotos(self)
        self.tool_lyt.addWidget(self.tool_widget)

    def run_link_echo_data_tool(self):
        self.tool_widget = LinkEchoData(self)
        self.tool_lyt.addWidget(self.tool_widget)

    def run_isis_checker_tool(self):
        self.tool_widget = CheckISISBanks(self)
        self.tool_lyt.addWidget(self.tool_widget)

    def run_photo_points_tool(self):
        self.tool_widget = PhotoPoints(self)
        self.tool_lyt.addWidget(self.tool_widget)


class PhotoPoints(QtGui.QWidget):
    def __init__(self, parent=None):
        super(PhotoPoints, self).__init__(parent)

        self.in_lbl = QtGui.QLabel('Input photo points csv')
        self.out_lbl = QtGui.QLabel('Output csv')
        self.inpath_le = QtGui.QLineEdit()
        self.outpath_le = QtGui.QLineEdit()
        self.in_browse_file_btn = QtGui.QPushButton('Browse file')
        self.out_browse_file_btn = QtGui.QPushButton('Browse file')
        self.run_btn = QtGui.QPushButton('Run')

        layout = [
            [self.in_lbl, self.inpath_le, self.in_browse_file_btn],
            [self.out_lbl, self.outpath_le, self.out_browse_file_btn],
            [self.run_btn],
            [SPACER()]
            ]

        lyt = GridLayout(layout)
        self.setLayout(lyt)

        self.in_browse_file_btn.clicked.connect(lambda: browse_for_file(self, 'Input file', self.inpath_le))
        self.out_browse_file_btn.clicked.connect(lambda: browse_for_file(self, 'Output file', self.outpath_le))
        self.run_btn.clicked.connect(self.run)

        self.show()

    def run(self):
        in_path = self.inpath_le.text()
        out_path = self.outpath_le.text()

        self.progress_box = ProgressWidget()
        self.progress_box.show()

        try:
            if not os.path.exists(in_path):
                self.progress_box.write('{} does not exist'.format(in_path))
                self.progress_box.finish()
                return

            photopoints.resolve_photo_points(in_path, out_path, self.progress_box)

        except Exception as err:
            self.progress_box.write(err)

        self.progress_box.finish()


class CheckISISBanks(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CheckISISBanks, self).__init__(parent)

        self.in_lbl = QtGui.QLabel('Input ISIS .dat file')
        self.inpath_le = QtGui.QLineEdit()
        self.in_browse_file_btn = QtGui.QPushButton('Browse file')
        self.run_btn = QtGui.QPushButton('Run')

        layout = [
            [self.in_lbl, self.inpath_le, self.in_browse_file_btn],
            [self.run_btn],
            [SPACER()]
            ]

        lyt = GridLayout(layout)
        self.setLayout(lyt)

        self.in_browse_file_btn.clicked.connect(lambda: browse_for_file(self, 'Input file', self.inpath_le))
        self.run_btn.clicked.connect(self.run)

        self.show()

    def run(self):
        isis_path = self.inpath_le.text()

        self.progress_box = ProgressWidget()
        self.progress_box.show()

        try:
            if not os.path.exists(isis_path):
                self.progress_box.write('{} does not exist'.format(isis_path))
                self.progress_box.finish()
                return

            checkisis.check_isis_banks(open(isis_path).read(), self.progress_box)

        except Exception as err:
            self.progress_box.write(err)

        self.progress_box.finish()


class LinkEchoData(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LinkEchoData, self).__init__(parent)

        self.survey_dir_lbl = QtGui.QLabel('Input survey data folder')
        self.echo_data_dir_lbl = QtGui.QLabel('Echo data folder')
        self.prefix_lbl = QtGui.QLabel('Prefix')
        self.out_lbl = QtGui.QLabel('Output Path')
        self.survey_dir_le = QtGui.QLineEdit()
        self.echo_data_dir_le = QtGui.QLineEdit()
        self.prefix_le = QtGui.QLineEdit()
        self.out_dir_le = QtGui.QLineEdit()
        self.survey_browse_dir_btn = QtGui.QPushButton('Browse folder')
        self.echo_browse_dir_btn = QtGui.QPushButton('Browse folder')
        self.out_browse_dir_btn = QtGui.QPushButton('Browse file')
        self.run_btn = QtGui.QPushButton('Run')

        layout = [
            [self.survey_dir_lbl, self.survey_dir_le, self.survey_browse_dir_btn],
            [self.echo_data_dir_lbl, self.echo_data_dir_le, self.echo_browse_dir_btn],
            [self.out_lbl, self.out_dir_le, self.out_browse_dir_btn],
            [self.prefix_lbl, self.prefix_le, FILL],
            [self.run_btn],
            [SPACER()]
            ]

        lyt = GridLayout(layout)
        self.setLayout(lyt)

        self.survey_browse_dir_btn.clicked.connect(lambda: self.browse_for_dir('Input folder', self.survey_dir_le))
        self.echo_browse_dir_btn.clicked.connect(lambda: self.browse_for_dir('Input folder', self.echo_data_dir_le))
        self.out_browse_dir_btn.clicked.connect(lambda: self.browse_for_save_file('Output file', '*.csv', self.out_dir_le))
        self.run_btn.clicked.connect(self.run)

        self.show()

    def browse_for_dir(self, title, line_edit):
        curr_path = line_edit.text()
        in_name = QtGui.QFileDialog.getExistingDirectory(self, title)
        line_edit.setText(in_name or curr_path)

    def browse_for_save_file(self, title, ext, line_edit):
        curr_path = line_edit.text()
        in_name = QtGui.QFileDialog.getSaveFileName(self, title, '', ext)
        line_edit.setText(in_name[0] or curr_path)

    def run(self):
        survey_dir = self.survey_dir_le.text()
        echo_data_dir = self.echo_data_dir_le.text()
        out_dir = self.out_dir_le.text()
        prefix = self.prefix_le.text().strip()

        self.progress_box = ProgressWidget()
        self.progress_box.show()

        try:
            link_echo_data.link_data(survey_dir, echo_data_dir, out_dir, prefix,
                self.progress_box)
        except Exception as err:
            self.progress_box.write(str(err))

        self.progress_box.finish()


class LinkEACSDPhotos(QtGui.QWidget):
    EA_PATTERNS = {'EA Standard': 'EA', 'EA North East': 'EANE'}
    def __init__(self, parent=None):
        super(LinkEACSDPhotos, self).__init__(parent)

        self.in_lbl = QtGui.QLabel('Input EACSD')
        self.photo_dir_lbl = QtGui.QLabel('Photo directory path')
        self.out_lbl = QtGui.QLabel('Output Path')
        self.pattern_lbl = QtGui.QLabel('Pattern')

        self.inpath_le = QtGui.QLineEdit()
        self.photo_dir_le = QtGui.QLineEdit()
        self.out_dir_le = QtGui.QLineEdit()
        self.pattern_combo = QtGui.QComboBox()
        self.pattern_combo.addItems([k for k in self.EA_PATTERNS])
        self.pattern_combo.setCurrentIndex(self.pattern_combo.findText('EA Standard'))
        self.wl_chk = QtGui.QCheckBox('Export water levels')
        self.wl_chk.setChecked(True)
        self.in_browse_file_btn = QtGui.QPushButton('Browse file')
        self.in_browse_dir_btn = QtGui.QPushButton('Browse folder')
        self.out_browse_dir_btn = QtGui.QPushButton('Browse folder')
        self.run_btn = QtGui.QPushButton('Run')

        layout = [
            [self.in_lbl, self.inpath_le, self.in_browse_file_btn],
            [self.photo_dir_lbl, self.photo_dir_le, self.in_browse_dir_btn],
            [self.out_lbl, self.out_dir_le, self.out_browse_dir_btn],
            [self.pattern_lbl, self.pattern_combo],
            [self.wl_chk, FILL],
            [self.run_btn],
            [SPACER()]
            ]

        lyt = GridLayout(layout)
        self.setLayout(lyt)

        self.in_browse_file_btn.clicked.connect(lambda: browse_for_file(self, 'Input file', self.inpath_le))
        self.in_browse_dir_btn.clicked.connect(lambda: browse_for_dir(self, 'Input folder', self.photo_dir_le))
        self.out_browse_dir_btn.clicked.connect(lambda: browse_for_dir(self, 'Output folder', self.out_dir_le))
        self.run_btn.clicked.connect(self.run)

        self.show()

    def run(self):
        eacsd_path = self.inpath_le.text()
        photo_dir = self.photo_dir_le.text()
        out_dir = self.out_dir_le.text()
        pattern = self.EA_PATTERNS[self.pattern_combo.currentText()]
        export_wl = self.wl_chk.isChecked()

        self.progress_box = ProgressWidget()
        self.progress_box.show()


        try:
            if not os.path.exists(eacsd_path):
                self.progress_box.write('{} does not exist'.format(eacsd_path))
                self.progress_box.finish()
                return

            if not os.path.isdir(photo_dir):
                self.progress_box.write('{} does not exist'.format(photo_dir))
                self.progress_box.finish()
                return

            renamephotos.link_eacsd_photos(eacsd_path, photo_dir, out_dir,
                pattern, export_wl, self.progress_box)

        except Exception as err:
            self.progress_box.write(err)

        self.progress_box.finish()


class TextReplace(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TextReplace, self).__init__(parent)

        self.in_lbl = QtGui.QLabel('Input Path')
        self.replace_lbl = QtGui.QLabel('Replace Path')
        self.extension_lbl = QtGui.QLabel('Extension')
        self.inpath_le = QtGui.QLineEdit()
        self.replace_le = QtGui.QLineEdit()
        self.replace_le.setText('Z:/Survey/Survey Software/AGUK Tools/find_replace_pairs.csv')
        self.extension_le = QtGui.QLineEdit()
        self.case_sensitive_chk = QtGui.QCheckBox('Case sensitive')
        self.sniffdate_chk = QtGui.QCheckBox('Reformat dates for EACSD')
        self.in_browse_file_btn = QtGui.QPushButton('Browse file')
        self.in_browse_dir_btn = QtGui.QPushButton('Browse folder')
        self.replace_browse_btn = QtGui.QPushButton('Browse')
        self.run_btn = QtGui.QPushButton('Run')

        layout = [
            [self.in_lbl, self.inpath_le, self.in_browse_file_btn, self.in_browse_dir_btn],
            [self.replace_lbl, self.replace_le, FILL, self.replace_browse_btn],
            [self.extension_lbl, self.extension_le],
            [self.case_sensitive_chk, self.sniffdate_chk, FILL],
            [self.run_btn],
            [SPACER()]
        ]

        lyt = GridLayout(layout)
        self.setLayout(lyt)

        self.in_browse_file_btn.clicked.connect(lambda: browse_for_file(self, 'Input file', self.inpath_le))
        self.in_browse_dir_btn.clicked.connect(lambda: browse_for_dir(self, 'Input folder', self.inpath_le))
        self.replace_browse_btn.clicked.connect(lambda: browse_for_file(self, 'Text replacements', self.replace_le))
        self.run_btn.clicked.connect(self.run)

        self.extension_le.setText('.dc')

        self.show()

    def run(self):
        inpath = self.inpath_le.text()
        replacefile = self.replace_le.text()
        case_sensitive = self.case_sensitive_chk.isChecked()
        extension = self.extension_le.text()
        sniffdate = self.sniffdate_chk.isChecked()

        self.progress_box = ProgressWidget()
        self.progress_box.show()

        try:
            paths = textreplace.get_file_list(inpath, extension)
        except FileNotFoundError as err:
            self.progress_box.write('File not found:\n' + str(err))
            return

        if not paths:
            self.progress_box.write('No files found')
            return

        try:
            replace_list = textreplace.get_replace_list(replacefile)
        except FileNotFoundError as err:
            self.progress_box.write('File not found:\n' + str(err))
            return

        try:
            textreplace.replace_strings_in_file_paths(paths, replace_list,
                case_sensitive, self.progress_box, sniffdate)
        except Exception as err:
            self.progress_box.write('Error:\n' + str(err))
            return

        self.progress_box.finish()


class TBCCSVTool(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TBCCSVTool, self).__init__(parent)

        self.in_lbl = QtGui.QLabel('Input Path')
        self.out_lbl = QtGui.QLabel('Output Path')
        self.cols_lbl = QtGui.QLabel('Columns')
        self.inpath_le = QtGui.QLineEdit()
        self.outpath_le = QtGui.QLineEdit()
        self.keep_empty_chk = QtGui.QCheckBox('Retain empty rows')
        self.sniffdate_chk = QtGui.QCheckBox('Reformat dates for EACSD')
        self.columns_le = QtGui.QLineEdit()
        self.inspect_radio = QtGui.QRadioButton('Inspect')
        self.create_radio = QtGui.QRadioButton('Create')
        self.in_browse_btn = QtGui.QPushButton('Browse')
        self.out_browse_btn = QtGui.QPushButton('Browse')
        self.run_btn = QtGui.QPushButton('Run')

        layout = [
            [self.in_lbl, self.inpath_le, self.in_browse_btn],
            [self.inspect_radio, self.create_radio],
            [self.keep_empty_chk, self.sniffdate_chk, FILL],
            [self.out_lbl, self.outpath_le, self.out_browse_btn],
            [self.cols_lbl, self.columns_le],
            [self.run_btn],
            [SPACER()]
        ]

        lyt = GridLayout(layout)
        self.setLayout(lyt)

        self.inspect_radio.toggled.connect(self.toggle_output)
        self.in_browse_btn.clicked.connect(lambda: browse_for_file(self, 'Open CSV', self.inpath_le, file_filter='*.csv'))
        self.out_browse_btn.clicked.connect(lambda: browse_for_save_file(self, 'Save CSV', self.outpath_le, file_filter='*.csv'))
        self.run_btn.clicked.connect(self.run)

        self.inspect_radio.setChecked(True)
        self.show()

    def run(self):
        infile = self.inpath_le.text()
        outfile = self.outpath_le.text()
        columns = self.columns_le.text().split() or None
        inspect = self.inspect_radio.isChecked()
        keep_empty = self.keep_empty_chk.isChecked()
        sniffdate = self.sniffdate_chk.isChecked()

        self.progress_box = ProgressWidget()
        self.progress_box.show()

        try:
            seen_cols = gps_csv.reformat_csv(infile, outfile, columns, inspect,
                keep_empty, self.progress_box, sniffdate)
            if inspect:
                self.create_radio.setChecked(True)
                self.columns_le.setText(seen_cols)
        except PermissionError as err:
            self.progress_box.write('Error: {} is already open.'.format(outpath))
            return
        except Exception as err:
            self.progress_box.write('Error:\n' + str(err))
            return
        self.progress_box.finish()

    def toggle_output(self):
        if self.inspect_radio.isChecked():
            self.outpath_le.setEnabled(False)
            self.columns_le.setEnabled(False)
            self.out_browse_btn.setEnabled(False)
            self.out_lbl.setEnabled(False)
            self.cols_lbl.setEnabled(False)
        else:
            self.outpath_le.setEnabled(True)
            self.columns_le.setEnabled(True)
            self.out_browse_btn.setEnabled(True)
            self.out_lbl.setEnabled(True)
            self.cols_lbl.setEnabled(True)


class ProgressWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ProgressWidget, self).__init__(parent)

        self.lyt = QtGui.QVBoxLayout()
        self.setLayout(self.lyt)

        self.message_area = QtGui.QPlainTextEdit(self)
        self.message_area.setReadOnly(True)

        self.ok_btn = QtGui.QPushButton('Close')
        self.ok_btn.clicked.connect(self.close)
        self.ok_btn.setEnabled(False)

        self.lyt.addWidget(self.message_area)
        self.lyt.addWidget(self.ok_btn)

        self.resize(300, 200)

    @QtCore.Slot(str)
    def write(self, message=''):
        self.message_area.moveCursor(QtGui.QTextCursor.End)
        self.message_area.insertPlainText(message + '\n')
        self.message_area.moveCursor(QtGui.QTextCursor.End)

    @QtCore.Slot(str)
    def finish(self):
        self.write('\nFinished!')
        self.ok_btn.setEnabled(True)


class ToolboxListWidget(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(ToolboxListWidget, self).__init__(parent)

        for name, help_text in TOOLS.items():
            item = QtGui.QListWidgetItem(name, self)
            item.setData(QtCore.Qt.UserRole, help_text)

        font_metric = QtGui.QFontMetrics(self.font())

        self.setFixedSize(self.sizeHintForColumn(0) * 1.5,
            self.sizeHintForRow(0) * 1.2 * len(TOOLS) + 2)


def SPACER():
    return QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum,
        QtGui.QSizePolicy.Expanding)


class GridLayout(QtGui.QGridLayout):
    def __init__(self, widget_grid, parent=None):
        super(GridLayout, self).__init__(parent)

        for ri, row in enumerate(widget_grid):
            for ci, widget in enumerate(row):
                colspan = 1
                rowspan = 1
                try:
                    colspan_indicator = row[ci + 1]
                    if colspan_indicator == FILL:
                        colspan += 1
                except IndexError:
                    pass
                if isinstance(widget, QtGui.QWidget):
                    self.addWidget(widget, ri, ci, rowspan, colspan)
                elif isinstance(widget, QtGui.QLayoutItem):
                    self.addItem(widget, ri, ci)
                elif isinstance(widget, str):
                    pass