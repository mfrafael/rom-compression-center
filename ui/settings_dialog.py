# Dialog de configurações para ROM Compression Center
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_config.yaml")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(400, 200)
        self.config = load_config()
        self.init_ui()


    def init_ui(self):
        from PySide6.QtWidgets import QListWidget, QTableWidget, QTableWidgetItem
        layout = QVBoxLayout()

        # Linha para pasta padrão + botão de escolha
        folder_layout = QHBoxLayout()
        self.default_folder_edit = QLineEdit(self.config.get("default_folder", ""))
        choose_btn = QPushButton("Choose...")
        choose_btn.clicked.connect(self.choose_folder)
        folder_layout.addWidget(self.default_folder_edit)
        folder_layout.addWidget(choose_btn)

        layout.addWidget(QLabel("Default ROM Folder:"))
        layout.addLayout(folder_layout)

        # Campo de lista de pastas ignoradas (QListWidget)
        layout.addWidget(QLabel("Ignored Folders:"))
        from PySide6.QtWidgets import QListWidget
        self.ignored_list = QListWidget()
        ignored = self.config.get("ignored_folders", [])
        for folder in ignored:
            self.ignored_list.addItem(folder)
        layout.addWidget(self.ignored_list)

        ignored_btn_layout = QHBoxLayout()
        add_ignored_btn = QPushButton("Add")
        del_ignored_btn = QPushButton("Delete")
        add_ignored_btn.clicked.connect(self.add_ignored_folder)
        del_ignored_btn.clicked.connect(self.delete_ignored_folder)
        ignored_btn_layout.addWidget(add_ignored_btn)
        ignored_btn_layout.addWidget(del_ignored_btn)
        layout.addLayout(ignored_btn_layout)

        self.advanced_checkbox = QCheckBox("Enable advanced mode")
        self.advanced_checkbox.setChecked(self.config.get("advanced_mode", False))
        layout.addWidget(self.advanced_checkbox)

        # Checkbox to ignore any folder named TEXTURES
        self.ignore_textures_checkbox = QCheckBox("Ignore all folders named 'TEXTURES'")
        self.ignore_textures_checkbox.setChecked(self.config.get("ignore_textures", True))
        layout.addWidget(self.ignore_textures_checkbox)

        # Checkbox to ignore system files (.ini, etc)
        self.ignore_system_files_checkbox = QCheckBox("Ignore system files (.ini, etc)")
        self.ignore_system_files_checkbox.setChecked(self.config.get("ignore_system_files", True))
        layout.addWidget(self.ignore_system_files_checkbox)

        # Botões
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.save)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def add_ignored_folder(self):
        from PySide6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Select folder to ignore", "")
        if folder:
            self.ignored_list.addItem(folder)

    def delete_ignored_folder(self):
        selected = self.ignored_list.selectedIndexes()
        for index in sorted(selected, reverse=True):
            self.ignored_list.takeItem(index.row())

    def save(self):
        self.config["default_folder"] = self.default_folder_edit.text()
        self.config["advanced_mode"] = self.advanced_checkbox.isChecked()
        self.config["ignore_textures"] = self.ignore_textures_checkbox.isChecked()
        self.config["ignore_system_files"] = self.ignore_system_files_checkbox.isChecked()
        # Salva lista de ignorados
        ignored = []
        if hasattr(self, "ignored_list"):
            for i in range(self.ignored_list.count()):
                item = self.ignored_list.item(i)
                if item:
                    ignored.append(item.text())
        self.config["ignored_folders"] = ignored
        save_config(self.config)
        self.accept()

    def choose_folder(self):
        from PySide6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Select ROM Folder", self.default_folder_edit.text())
        if folder:
            self.default_folder_edit.setText(folder)

    def save(self):
        self.config["default_folder"] = self.default_folder_edit.text()
        self.config["advanced_mode"] = self.advanced_checkbox.isChecked()
        self.config["ignore_textures"] = self.ignore_textures_checkbox.isChecked()
        self.config["ignore_system_files"] = self.ignore_system_files_checkbox.isChecked()
        # Salva lista de ignorados
        ignored = []
        if hasattr(self, "ignored_list"):
            for i in range(self.ignored_list.count()):
                item = self.ignored_list.item(i)
                if item:
                    ignored.append(item.text())
        self.config["ignored_folders"] = ignored
        save_config(self.config)
        self.accept()
# Settings dialog UI component for ROM Compression Center