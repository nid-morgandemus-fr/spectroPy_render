#!/usr/bin/env python3
"""
spectroPy_render.py
Multiplatform tool (GUI + CLI) with interactive preview, audio playback and FFmpeg export.
"""

import argparse
import os
import sys
import subprocess
import re
import traceback
import json
import numpy as np

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                 QHBoxLayout, QFormLayout, QLabel, QLineEdit,
                                 QPushButton, QComboBox, QDoubleSpinBox, QSpinBox,
                                 QCheckBox, QFileDialog, QMessageBox, QScrollArea,
                                 QTextEdit, QGroupBox, QSplitter)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
    from PyQt6.QtGui import QFont, QKeySequence, QDesktopServices

    import matplotlib
    matplotlib.use('QtAgg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    import matplotlib.pyplot as plt
    import librosa
    import librosa.display
    import sounddevice as sd
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install dependencies: pip install PyQt6 matplotlib librosa sounddevice")
    sys.exit(1)

class Translator:
    def __init__(self, locale_dir, language="fr"):
        self.locale_dir = locale_dir
        self.language = language
        self.translations = {}
        self.load_language(language)
    
    def load_language(self, language):
        self.language = language
        lang_file = os.path.join(self.locale_dir, f"{language}.json")
        
        if os.path.exists(lang_file):
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        else:
            print(f"Warning: Language file {lang_file} not found. Using defaults.")
            self.translations = {}
    
    def t(self, key, **kwargs):
        """Translate a key with optional format arguments"""
        text = self.translations.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text
    
    def get_available_languages(self):
        """Get list of available languages"""
        languages = []
        if os.path.exists(self.locale_dir):
            for file in os.listdir(self.locale_dir):
                if file.endswith('.json'):
                    languages.append(file.replace('.json', ''))
        return sorted(languages)

PARAMS_CONFIG = {
    "size": {"label_key": "size", "type": "text", "default": "1920x1080"},
    "mode": {"label_key": "mode", "type": "combo", "options": ["combined", "separate"], "default": "combined"},
    "color": {"label_key": "color", "type": "combo",
              "options": ["fiery", "rainbow", "intensity", "magma", "viridis", "cool", "plasma", "green", "blue"],
              "default": "fiery"},
    "scale": {"label_key": "scale", "type": "combo", "options": ["log", "lin", "sqrt", "cbrt"], "default": "log"},
    "fscale": {"label_key": "fscale", "type": "combo", "options": ["log", "lin"], "default": "log"},
    "win_func": {"label_key": "win_func", "type": "combo",
                 "options": ["hann", "blackman", "hamming", "rect", "bartlett", "flattop", "welch", "nuttall"],
                 "default": "hann"},
    "gain": {"label_key": "gain", "type": "double_spin", "min": 0.1, "max": 100.0, "step": 0.1, "default": 1.0},
    "start": {"label_key": "start", "type": "spin", "min": 0, "max": 192000, "default": 0},
    "stop": {"label_key": "stop", "type": "spin", "min": 0, "max": 192000, "default": 0},
    "drange": {"label_key": "drange", "type": "spin", "min": 10, "max": 200, "default": 120},
    "legend": {"label_key": "legend", "type": "check", "default": True},
    "preview_duration": {"label_key": "preview_duration", "type": "spin", "min": 5, "max": 600, "default": 60}
}

COLORMAP_MAP = {
    "fiery": "afmhot",
    "rainbow": "rainbow",
    "intensity": "gray",
    "magma": "magma",
    "viridis": "viridis",
    "cool": "cool",
    "plasma": "plasma",
    "green": "Greens",
    "blue": "Blues"
}

PLAY_STYLE = "background-color: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"
STOP_STYLE = "background-color: #dc3545; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"


def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def build_ffmpeg_cmd(input_file, output_file, params):
    filter_opts = []
    for key, val in params.items():
        if key == "legend":
            val = "1" if val else "0"
        elif key == "start" or key == "stop":
            val = int(val) if val else 0
        elif key == "drange":
            val = int(val)
        filter_opts.append(f"{key}={val}")
    filter_str = "showspectrumpic=" + ":".join(filter_opts)
    return ["ffmpeg", "-y", "-i", input_file, "-lavfi", filter_str, output_file]


class FFmpegWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def run(self):
        try:
            process = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            returncode = process.wait()

            if returncode == 0:
                self.finished.emit(True, "Spectrogram generated successfully!")
            else:
                self.finished.emit(False, f"FFmpeg returned error (code {returncode})")

        except Exception as e:
            self.finished.emit(False, f"Error:\n{str(e)}")


def run_cli(args):
    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' does not exist.")
        sys.exit(1)
    if not check_ffmpeg():
        print("Error: FFmpeg not found.")
        sys.exit(1)

    params = {key: getattr(args, key) for key in PARAMS_CONFIG.keys()}
    cmd = build_ffmpeg_cmd(args.input, args.output, params)
    print(f"Execution: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Success: '{args.output}'")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg Error:\n{e.stderr}")
        sys.exit(1)


class MainWindow(QMainWindow):
    def __init__(self, cli_args, translator):
        super().__init__()
        self.translator = translator
        self.setWindowTitle(self.translator.t("app_title"))
        self.resize(1200, 800)

        self.setStyleSheet("""
            QWidget { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; }
            QGroupBox { font-weight: bold; border: 1px solid #cccccc; border-radius: 5px; margin-top: 10px; padding-top: 10px; }
            QPushButton { background-color: #0078d7; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #1084d9; }
            QPushButton#HelpBtn { background-color: #ffc107; color: #000000; font-weight: bold; padding: 6px 12px; border-radius: 4px; }
            QPushButton#HelpBtn:hover { background-color: #ffb300; }
            QPushButton#GenerateBtn { background-color: #28a745; font-size: 11pt; }
            QPushButton#GenerateBtn:hover { background-color: #218838; }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { padding: 5px; border: 1px solid #cccccc; border-radius: 3px; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        header_layout = QHBoxLayout()
        title_label = QLabel(self.translator.t("header_title"))
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.help_btn = QPushButton(self.translator.t("help_button"))
        self.help_btn.setObjectName("HelpBtn")
        self.help_btn.clicked.connect(self.open_documentation)
        header_layout.addWidget(self.help_btn)

        main_layout.addLayout(header_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)

        file_group = QGroupBox(self.translator.t("file_group_title"))
        file_layout = QFormLayout()

        self.input_edit = QLineEdit()
        self.input_edit.setText(cli_args.input if cli_args.input else "")
        input_browse_btn = QPushButton(self.translator.t("browse_button"))
        input_browse_btn.clicked.connect(self.browse_input)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_browse_btn)
        file_layout.addRow(self.translator.t("audio_label"), input_layout)

        self.output_edit = QLineEdit()
        self.output_edit.setText(cli_args.output if cli_args.output else "")
        output_browse_btn = QPushButton(self.translator.t("browse_button"))
        output_browse_btn.clicked.connect(self.browse_output)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_browse_btn)
        file_layout.addRow(self.translator.t("output_label"), output_layout)

        self.play_btn = QPushButton(self.translator.t("play_button"))
        self.play_btn.setStyleSheet(PLAY_STYLE)
        self.play_btn.clicked.connect(self.toggle_playback)
        file_layout.addRow("", self.play_btn)

        file_group.setLayout(file_layout)
        left_layout.addWidget(file_group)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.param_layout = QFormLayout(scroll_widget)
        self.param_widgets = {}

        for key, config in PARAMS_CONFIG.items():
            row_layout = QHBoxLayout()
            if config["type"] == "text":
                widget = QLineEdit()
                widget.setText(str(config["default"]))
            elif config["type"] == "combo":
                widget = QComboBox()
                widget.addItems(config["options"])
                widget.setCurrentText(str(config["default"]))
            elif config["type"] == "spin":
                widget = QSpinBox()
                widget.setRange(config["min"], config["max"])
                widget.setValue(config["default"])
            elif config["type"] == "double_spin":
                widget = QDoubleSpinBox()
                widget.setRange(config["min"], config["max"])
                widget.setSingleStep(config["step"])
                widget.setValue(config["default"])
            elif config["type"] == "check":
                widget = QCheckBox()
                widget.setChecked(config["default"])

            self.param_widgets[key] = widget
            if hasattr(widget, 'valueChanged'):
                widget.valueChanged.connect(self.schedule_preview_update)
            elif hasattr(widget, 'currentTextChanged'):
                widget.currentTextChanged.connect(self.schedule_preview_update)
            elif hasattr(widget, 'toggled'):
                widget.toggled.connect(self.schedule_preview_update)
            elif hasattr(widget, 'textChanged'):
                widget.textChanged.connect(self.schedule_preview_update)

            row_layout.addWidget(widget)
            self.param_layout.addRow(self.translator.t("params." + config["label_key"]) + " :", row_layout)

        scroll_area.setWidget(scroll_widget)
        left_layout.addWidget(scroll_area)
        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)

        preview_group = QGroupBox(self.translator.t("preview_group_title"))
        preview_layout = QVBoxLayout(preview_group)

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        preview_layout.addWidget(self.toolbar)
        preview_layout.addWidget(self.canvas)
        right_layout.addWidget(preview_group)
        splitter.addWidget(right_widget)

        splitter.setSizes([400, 800])
        main_layout.addWidget(splitter, 1)

        action_layout = QVBoxLayout()

        self.generate_btn = QPushButton(self.translator.t("generate_button"))
        self.generate_btn.setObjectName("GenerateBtn")
        self.generate_btn.setMinimumHeight(45)
        self.generate_btn.clicked.connect(self.generate_spectrogram)
        action_layout.addWidget(self.generate_btn)

        main_layout.addLayout(action_layout)

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMaximumHeight(100)
        self.log_edit.append(self.translator.t("ready_message"))
        main_layout.addWidget(self.log_edit)

        self.preview_timer = None
        self.audio_data = None
        self.audio_sr = None
        self.is_playing = False
        self.play_stream = None

        if not check_ffmpeg():
            self.log_edit.append(f"<span style='color:orange;'>{self.translator.t('ffmpeg_not_found')}</span>")

        self.doc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"documentation_{self.translator.language}.md")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F1:
            self.open_documentation()
        else:
            super().keyPressEvent(event)

    def open_documentation(self):
        if os.path.exists(self.doc_path):
            doc_url = QUrl.fromLocalFile(self.doc_path)
            QDesktopServices.openUrl(doc_url)
        else:
            QMessageBox.warning(
                self,
                self.translator.t("help_not_found_title"),
                self.translator.t("help_not_found_message", path=self.doc_path)
            )

    def browse_input(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.translator.t("select_audio_title"), "",
                                                   self.translator.t("audio_files_filter"))
        if file_path:
            self.input_edit.setText(file_path)
            if not self.output_edit.text():
                base_name = os.path.splitext(file_path)[0]
                self.output_edit.setText(base_name + "_spectrogram.png")
            self.update_preview()

    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(self, self.translator.t("save_spectrogram_title"), "", 
                                                   self.translator.t("png_files_filter"))
        if file_path:
            self.output_edit.setText(file_path)

    def schedule_preview_update(self):
        if self.preview_timer is not None:
            self.killTimer(self.preview_timer)
        self.preview_timer = self.startTimer(500)

    def timerEvent(self, event):
        if self.preview_timer is not None:
            self.killTimer(self.preview_timer)
            self.preview_timer = None
        self.update_preview()

    def update_preview(self):
        input_file = self.input_edit.text().strip()
        if not input_file or not os.path.exists(input_file):
            return

        self.log_edit.append(self.translator.t("calculating_preview"))
        QApplication.processEvents()

        try:
            self.fig.clear()
            self.ax = self.fig.add_subplot(111)

            win_func = self.param_widgets["win_func"].currentText()
            fscale = self.param_widgets["fscale"].currentText()
            scale = self.param_widgets["scale"].currentText()
            color = self.param_widgets["color"].currentText()
            gain = self.param_widgets["gain"].value()
            drange = self.param_widgets["drange"].value()
            start_freq = self.param_widgets["start"].value()
            stop_freq = self.param_widgets["stop"].value()
            show_legend = self.param_widgets["legend"].isChecked()
            preview_duration = self.param_widgets["preview_duration"].value()

            if preview_duration > 120:
                self.log_edit.append(f"<span style='color:orange;'>{self.translator.t('high_duration_warning', duration=preview_duration)}</span>")

            fscale_map = {"log": "log", "lin": "linear"}
            fscale_mpl = fscale_map.get(fscale, "log")

            y, sr = librosa.load(input_file, sr=None, duration=float(preview_duration), mono=True)
            y = y * gain

            n_fft = 2048
            hop_length = 512
            D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length, window=win_func)

            if scale == "log":
                S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
            elif scale == "lin":
                S_db = np.abs(D)
            elif scale == "sqrt":
                S_db = np.sqrt(np.abs(D))
            elif scale == "cbrt":
                S_db = np.cbrt(np.abs(D))
            else:
                S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

            cmap = COLORMAP_MAP.get(color, "magma")

            img = librosa.display.specshow(S_db, sr=sr, hop_length=hop_length,
                                           x_axis='time', y_axis=fscale_mpl,
                                           cmap=cmap, ax=self.ax)

            if scale == "log":
                max_db = np.max(S_db)
                img.set_clim(max_db - drange, max_db)

            if start_freq > 0:
                self.ax.set_ylim(bottom=start_freq)
            if stop_freq > 0:
                self.ax.set_ylim(top=stop_freq)

            self.ax.set(title=f"Preview ({preview_duration}s) - {os.path.basename(input_file)}",
                        ylabel="Frequency (Hz)", xlabel="Time (s)")

            if show_legend:
                fmt = "%+2.0f dB" if scale == "log" else None
                self.fig.colorbar(img, ax=self.ax, format=fmt, label="Intensity")

            self.fig.tight_layout()
            self.canvas.draw()
            self.log_edit.append(f"<span style='color:green;'>{self.translator.t('preview_updated')}</span>")

        except Exception as e:
            error_msg = traceback.format_exc()
            self.log_edit.append(f"<span style='color:red;'>{self.translator.t('preview_error', error=error_msg)}</span>")

    def toggle_playback(self):
        if self.is_playing:
            self.stop_playback()
        else:
            self.start_playback()

    def start_playback(self):
        input_file = self.input_edit.text().strip()
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, self.translator.t("error_title"), self.translator.t("no_audio_file"))
            return

        try:
            if self.is_playing:
                self.stop_playback()

            self.log_edit.append(self.translator.t("loading_audio"))
            QApplication.processEvents()
            self.audio_data, self.audio_sr = librosa.load(input_file, sr=None, mono=False)

            if self.audio_data.dtype != np.float32:
                self.audio_data = self.audio_data.astype(np.float32)

            if len(self.audio_data.shape) == 1:
                audio_to_play = self.audio_data
            else:
                audio_to_play = self.audio_data.T

            self.play_stream = sd.play(audio_to_play, self.audio_sr)
            self.is_playing = True
            self.play_btn.setText(self.translator.t("stop_button"))
            self.play_btn.setStyleSheet(STOP_STYLE)
            self.log_edit.append(f"<span style='color:blue;'>{self.translator.t('playing')}</span>")

        except Exception as e:
            QMessageBox.critical(self, self.translator.t("playback_error_title"), 
                               self.translator.t("playback_error_message", error=str(e)))
            self.is_playing = False

    def stop_playback(self):
        try:
            sd.stop()
            if self.play_stream is not None:
                self.play_stream.close()
                self.play_stream = None
        except Exception:
            pass

        self.is_playing = False
        self.play_btn.setText(self.translator.t("play_button"))
        self.play_btn.setStyleSheet(PLAY_STYLE)
        self.log_edit.append(f"<span style='color:blue;'>{self.translator.t('stopped')}</span>")

    def generate_spectrogram(self):
        input_file = self.input_edit.text().strip()
        output_file = self.output_edit.text().strip()

        if not input_file or not output_file:
            QMessageBox.warning(self, self.translator.t("error_title"), self.translator.t("specify_files_error"))
            return
        if not os.path.exists(input_file):
            QMessageBox.warning(self, self.translator.t("error_title"), 
                              self.translator.t("input_not_found", path=input_file))
            return
        if not check_ffmpeg():
            QMessageBox.critical(self, self.translator.t("error_title"), self.translator.t("ffmpeg_required"))
            return

        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", input_file],
                capture_output=True, text=True, check=True
            )
            duration = float(result.stdout.strip())
            minutes = int(duration // 60)
            secondes = int(duration % 60)
            duree_texte = f"{minutes}min {secondes}s"
        except Exception:
            duree_texte = "unknown"

        self.log_edit.append(f"<span style='color:orange;'>{self.translator.t('generating_ffmpeg', duration=duree_texte)}</span>")
        self.generate_btn.setEnabled(False)

        params = {}
        for key, widget in self.param_widgets.items():
            if isinstance(widget, QCheckBox):
                params[key] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                params[key] = widget.currentText()
            elif isinstance(widget, QLineEdit):
                params[key] = widget.text()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                params[key] = widget.value()

        cmd = build_ffmpeg_cmd(input_file, output_file, params)

        self.worker = FFmpegWorker(cmd)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.start()

    def on_generation_finished(self, success, message):
        self.generate_btn.setEnabled(True)
        if success:
            self.log_edit.append(f"<span style='color:green;'>{self.translator.t('generation_success', message=message)}</span>")
            QMessageBox.information(self, self.translator.t("success_title"), message)
        else:
            self.log_edit.append(f"<span style='color:red;'>{self.translator.t('generation_error', message=message)}</span>")
            QMessageBox.critical(self, self.translator.t("error_title"), message)

    def closeEvent(self, event):
        if self.is_playing:
            self.stop_playback()
        event.accept()


def setup_cli_parser():
    parser = argparse.ArgumentParser(description="Bioacoustics spectrogram generator (GUI + CLI).")
    parser.add_argument("--gui", action="store_true", help="Force GUI launch")
    parser.add_argument("--lang", type=str, default="fr", help="Language: fr or en")
    parser.add_argument("-i", "--input", help="Input audio file")
    parser.add_argument("-o", "--output", help="Output image file")

    for key, config in PARAMS_CONFIG.items():
        arg_name = f"--{key.replace('_', '-')}"
        if config["type"] in ["spin", "double_spin"]:
            arg_type = float if config["type"] == "double_spin" else int
            parser.add_argument(arg_name, type=arg_type, default=config["default"])
        elif config["type"] == "check":
            dest_name = key
            parser.add_argument(arg_name, action="store_true", default=config["default"], dest=dest_name)
            parser.add_argument(f"--no-{key.replace('_', '-')}", action="store_false", dest=dest_name)
        else:
            parser.add_argument(arg_name, type=str, default=config["default"])
    return parser


def main():
    parser = setup_cli_parser()
    args = parser.parse_args()

    locale_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locale")
    translator = Translator(locale_dir, args.lang)

    if args.input or args.output:
        if not args.input or not args.output:
            print("Error: --input (-i) and --output (-o) are required in CLI mode.")
            sys.exit(1)
        run_cli(args)
    else:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        window = MainWindow(args, translator)
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
