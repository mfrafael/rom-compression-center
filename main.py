# Main window UI logic for ROM Compression Center
# main.py
from PySide6.QtWidgets import (
    QApplication, QWidget, QTableWidget, QListWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QCheckBox, QLabel, QTableWidgetItem, QLineEdit, QSplitter
)

from PySide6.QtCore import Qt, Signal, QThread
from core.queue_worker import QueueWorker, handle_nintendo_switch_queue_item
import os
from core import db_manager, scanner, queue_manager, utils

class RomCompressionGUI(QWidget):
    status_update = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROM Compression Center")
        self.resize(1000, 600)
        self.uncompressed_label = QLabel()
        self.compressed_label = QLabel()
        self.queue_running = False
        self.stop_queue_flag = False
        self.nsz_proc = None
        self.debug_log = None  # Will be set in init_ui
        
        # Inicializa os contadores totais para evitar erros
        self.total_uncompressed_all = 0
        self.total_uncompressed_size_all = 0
        self.total_compressed_all = 0
        self.total_compressed_size_all = 0
        
        self.init_ui()
        self.refresh_button.clicked.connect(self.refresh_rom_folder)
        self.run_button.clicked.connect(self.toggle_queue)
        self.status_update.connect(self.handle_status_update)
        self.load_roms_from_db()
        # Inicializa a visibilidade do console de debug
        self.update_debug_log_visibility()
        # self.load_queue_from_file_and_populate()
    def load_queue_from_file_and_populate(self):
        from core.queue_manager import load_queue_from_file
        queue = load_queue_from_file()
        self.queue_table.setRowCount(len(queue))
        for row, item in enumerate(queue):
            action_item = QTableWidgetItem(item['action'])
            action_item.setFlags(action_item.flags() & ~Qt.ItemIsEditable)
            name_item = QTableWidgetItem(item['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.queue_table.setItem(row, 0, action_item)
            self.queue_table.setItem(row, 1, name_item)
        
    def set_status_label(self, text):
        self.status_label.setText(text)

    def handle_status_update(self, text):
        self.set_status_label(text)
        if self.debug_log:
            self.debug_log.appendPlainText(text)
            
    def add_log(self, text):
        """
        Função centralizada para adicionar logs ao console de debug
        Todos os handlers podem usar esta função para garantir consistência
        """
        # Emite o sinal para atualizar o status e o console de debug
        self.status_update.emit(text)
            
    def update_debug_log_visibility(self):
        # Atualiza a visibilidade do console de debug com base no checkbox
        if hasattr(self, 'debug_log') and self.debug_log:
            self.debug_log.setVisible(self.verbose_checkbox.isChecked())

    def toggle_queue(self):
        if not self.queue_running:
            # Check if queue has items
            queue = queue_manager.build_queue_from_tables(
                self.table_uncompressed,
                self.table_compressed,
                self.queue_table
            )
            if not queue:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Queue Empty",
                    "There are no items in the queue. Nothing was done."
                )
                return
            # Confirmation if delete is checked
            if self.compress_checkbox.isChecked():
                from PySide6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    "Confirm Deletion",
                    "You have selected 'Delete original after queue'.\nAre you sure you want to delete the original files after processing?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            self.queue_running = True
            self.stop_queue_flag = False
            self.run_button.setText("Stop Queue")
            self.refresh_button.setEnabled(False)
            self.settings_button.setEnabled(False)
            self.queue_thread = QThread()
            # Ainda passamos o parâmetro 'verbose', mas apenas para controle interno do QueueWorker
            # Esse parâmetro não será propagado para os handlers
            self.queue_worker = QueueWorker(queue, self.queue_table, self.compress_checkbox.isChecked(), verbose=self.verbose_checkbox.isChecked())
            self.queue_worker.moveToThread(self.queue_thread)
            self.queue_worker.status_update.connect(self.handle_status_update)
            self.queue_worker.finished.connect(self.queue_finished)
            self.queue_worker.item_finished.connect(self.refresh_rom_folder)
            self.queue_worker.item_processed.connect(self.update_table_row_for_path)
            self.queue_thread.started.connect(self.queue_worker.run)
            self.queue_thread.start()
        else:
            self.stop_queue_flag = True
            self.status_label.setText("Queue stopping...")
            self.run_button.setText("Run Queue")
            if hasattr(self, 'queue_worker'):
                self.queue_worker.stop()

    def _recalculate_totals(self):
        """Recalcula os totais de ROMs e tamanho para os rótulos de resumo"""
        # Calcula totais para arquivos não comprimidos
        total_uncompressed = 0
        total_uncompressed_size = 0
        for row in range(self.table_uncompressed.rowCount()):
            if not self.table_uncompressed.isRowHidden(row):
                total_uncompressed += 1
                path_item = self.table_uncompressed.item(row, 3)
                if path_item and os.path.exists(path_item.text()):
                    try:
                        total_uncompressed_size += os.path.getsize(path_item.text())
                    except (OSError, IOError):
                        pass
        
        # Calcula totais para arquivos comprimidos
        total_compressed = 0
        total_compressed_size = 0
        for row in range(self.table_compressed.rowCount()):
            if not self.table_compressed.isRowHidden(row):
                total_compressed += 1
                path_item = self.table_compressed.item(row, 3)
                if path_item and os.path.exists(path_item.text()):
                    try:
                        total_compressed_size += os.path.getsize(path_item.text())
                    except (OSError, IOError):
                        pass
        
        # Atualiza os totais armazenados e os rótulos
        self.total_uncompressed_all = total_uncompressed
        self.total_uncompressed_size_all = total_uncompressed_size
        self.total_compressed_all = total_compressed
        self.total_compressed_size_all = total_compressed_size
        
        # Atualiza os rótulos
        self.uncompressed_label.setText(f"Uncompressed ROMs: {total_uncompressed} | Total size: {utils.get_human_size(total_uncompressed_size)}")
        self.compressed_label.setText(f"Compressed ROMs: {total_compressed} | Total size: {utils.get_human_size(total_compressed_size)}")

    def queue_finished(self):
        self.queue_running = False
        self.run_button.setText("Run Queue")
        self.status_label.setText("Queue finished.")
        self.refresh_button.setEnabled(True)
        self.settings_button.setEnabled(True)
        self.refresh_rom_folder()
        if hasattr(self, 'queue_thread'):
            self.queue_thread.quit()
            self.queue_thread.wait()
            del self.queue_worker
            del self.queue_thread

    def load_roms_from_db(self):
        # Load ROMs from database and populate tables
        details_list = db_manager.get_all_roms()  # List of dicts: file_name, platform, path, size, action
        db_manager.populate_table_db(self, details_list)
        # Atualiza os resumos usando os caminhos dos arquivos
        file_list = [d['path'] for d in details_list if 'path' in d]
        self.populate_table(file_list)

    # Now handled by db_manager.populate_table_db

    def init_ui(self):
        from PySide6.QtWidgets import (
            QHeaderView, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout,
            QProgressBar, QTableWidget, QListWidget, QCheckBox, QPushButton, QSplitter
        )
        from PySide6.QtCore import Qt

        def configure_table(table: QTableWidget):
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Select", "File Name", "Platform", "Path", "Size"])
            header = table.horizontalHeader()

            # Autosize (fixed)
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Select
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Platform
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Size

            header.setSectionResizeMode(1, QHeaderView.Stretch)      # File Name stretch
            header.setSectionResizeMode(3, QHeaderView.Stretch)      # Path stretch

            # Redimensionáveis + stretch
            header.setSectionResizeMode(1, QHeaderView.Interactive)  # File Name
            #header.setSectionResizeMode(3, QHeaderView.Interactive)  # Path

            table.setSortingEnabled(True)
            table.setSelectionMode(QTableWidget.NoSelection)

        # Tables
        self.table_uncompressed = QTableWidget()
        configure_table(self.table_uncompressed)
        self.table_uncompressed.verticalHeader().setVisible(False)

        self.table_compressed = QTableWidget()
        configure_table(self.table_compressed)
        self.table_compressed.verticalHeader().setVisible(False)

        # Queue table
        from PySide6.QtWidgets import QTableWidget, QHeaderView
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(2)
        self.queue_table.setHorizontalHeaderLabels(["Action", "File Name"])
        header = self.queue_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.queue_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.queue_table.setSelectionMode(QTableWidget.NoSelection)
        self.queue_table.verticalHeader().setVisible(False)

        # Controls
        self.compress_checkbox = QCheckBox("Delete original after queue")
        self.verbose_checkbox = QCheckBox("Show detailed log in terminal")
        self.run_button = QPushButton("Run Queue")
        self.refresh_button = QPushButton("Refresh")
        self.settings_button = QPushButton("Settings")
        self.status_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

        # Debug log window
        from PySide6.QtWidgets import QPlainTextEdit
        self.debug_log = QPlainTextEdit()
        self.debug_log.setReadOnly(True)
        self.debug_log.setMinimumHeight(120)
        self.debug_log.setPlaceholderText("Debug log output...")
        
        # Inicialmente esconde ou mostra o console de debug com base no checkbox
        # O método será chamado após a inicialização completa

        # Search
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search table...")

        search_layout = QVBoxLayout()
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))
        search_row.addWidget(self.search_edit)
        search_layout.addLayout(search_row)

        hint_label = QLabel("Tip: Use commas to search for multiple values. All values must be present in a row. Example: batman, sega")
        hint_label.setStyleSheet("color: gray; font-size: 11px;")
        search_layout.addWidget(hint_label)

        # Right panel
        from PySide6.QtWidgets import QSizePolicy
        right_layout = QVBoxLayout()
        right_layout.addLayout(search_layout)
        right_layout.addWidget(self.uncompressed_label)
        right_layout.addWidget(self.table_uncompressed)
        right_layout.addWidget(self.compressed_label)
        right_layout.addWidget(self.table_compressed)
        right_layout.setStretch(0, 0)  # Search
        right_layout.setStretch(1, 0)  # Uncompressed label
        right_layout.setStretch(2, 1)  # Uncompressed table
        right_layout.setStretch(3, 0)  # Compressed label
        right_layout.setStretch(4, 1)  # Compressed table
        right_widget = QWidget()
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_widget.setLayout(right_layout)

        # Left panel
        from PySide6.QtWidgets import QSizePolicy
        left_layout = QVBoxLayout()
        label_queue = QLabel("Selected Queue")
        label_queue.setMinimumHeight(0)
        left_layout.addWidget(label_queue)
        self.queue_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(self.queue_table)
        left_layout.setStretch(0, 0)  # Label
        left_layout.setStretch(1, 1)  # Table stretches
        left_widget = QWidget()
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_widget.setLayout(left_layout)

        # Bottom panel
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.compress_checkbox)
        bottom_layout.addWidget(self.verbose_checkbox)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.settings_button)
        bottom_layout.addWidget(self.refresh_button)
        bottom_layout.addWidget(self.run_button)

        # Main layout with splitter
        splitter = QSplitter()
        splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        splitter.setSizes([200, 800])  # Initial sizes, user can adjust

        final_layout = QVBoxLayout()
        final_layout.addWidget(splitter, stretch=1)
        final_layout.addLayout(bottom_layout)
        final_layout.addWidget(self.status_label)
        final_layout.addWidget(self.progress_bar)
        final_layout.addWidget(self.debug_log)

        self.setLayout(final_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Signals
        self.settings_button.clicked.connect(self.open_settings)
        self.search_edit.textChanged.connect(self.apply_table_search)
        self.verbose_checkbox.stateChanged.connect(self.update_debug_log_visibility)


    def refresh_rom_folder(self):
        db_manager.clear_roms()
        self.progress_bar.show()
        folder = scanner.get_rom_folder()
        from PySide6.QtWidgets import QMessageBox
        import os
        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, "ROM Folder", "No valid ROM folder selected in settings.")
            return
        details_list, file_list = scanner.scan_and_prepare_roms(folder, self.status_label, self.progress_bar)
        db_manager.insert_roms(details_list)
        self.status_label.setText(f"Scan complete. {len(file_list)} files processed.")
        self.progress_bar.hide()
        self.populate_table(file_list)

    def populate_table(self, file_list):
        import sys, os
        try:
            from compression.compression_formats import is_compressed
        except ImportError:
            import importlib.util
            comp_path = os.path.join(os.path.dirname(__file__), '..', 'compression', 'compression_formats.py')
            spec = importlib.util.spec_from_file_location('compression_formats', comp_path)
            comp_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(comp_mod)
            is_compressed = comp_mod.is_compressed
        from PySide6.QtWidgets import QCheckBox, QWidget, QHBoxLayout, QComboBox, QTableWidgetItem
        from PySide6.QtCore import Qt
        # Separa arquivos por status
        uncompressed = []
        compressed = []
        for path in file_list:
            name = os.path.basename(path)
            if is_compressed(name):
                compressed.append(path)
            else:
                uncompressed.append(path)
        # Resumo para não comprimidos
        total_uncompressed = len(uncompressed)
        total_uncompressed_size = sum(os.path.getsize(p) for p in uncompressed if os.path.exists(p))
        self.uncompressed_label.setText(f"Uncompressed ROMs: {total_uncompressed} | Total size: {utils.get_human_size(total_uncompressed_size)}")
        # Resumo para comprimidos
        total_compressed = len(compressed)
        total_compressed_size = sum(os.path.getsize(p) for p in compressed if os.path.exists(p))
        self.compressed_label.setText(f"Compressed ROMs: {total_compressed} | Total size: {utils.get_human_size(total_compressed_size)}")
        
        # Armazena os totais originais para referência
        self.total_uncompressed_all = total_uncompressed
        self.total_uncompressed_size_all = total_uncompressed_size
        self.total_compressed_all = total_compressed
        self.total_compressed_size_all = total_compressed_size
        # Preenche tabela de não comprimidos
        # Only use this for scan results (refresh), not for DB loading
        self.table_uncompressed.setRowCount(len(uncompressed))
        checkboxes_uncompressed = []
        for i, path in enumerate(uncompressed):
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, row=i: self.update_selected_queue(row, state))
            checkboxes_uncompressed.append(checkbox)
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(checkbox)
            layout.setAlignment(checkbox, Qt.AlignCenter)
            layout.setContentsMargins(0,0,0,0)
            self.table_uncompressed.setCellWidget(i, 0, widget)
            name = os.path.basename(path)
            item_name = QTableWidgetItem(name)
            item_name.setFlags(item_name.flags() & ~Qt.ItemIsEditable)
            self.table_uncompressed.setItem(i, 1, item_name)
            platform = utils.get_platform_from_path(path)
            item_platform = QTableWidgetItem(platform)
            item_platform.setFlags(item_platform.flags() & ~Qt.ItemIsEditable)
            self.table_uncompressed.setItem(i, 2, item_platform)
            item_path = QTableWidgetItem(path)
            item_path.setFlags(item_path.flags() & ~Qt.ItemIsEditable)
            self.table_uncompressed.setItem(i, 3, item_path)
            # Only get size if file exists
            if os.path.exists(path):
                size = utils.get_human_size(os.path.getsize(path))
            else:
                size = "(missing)"
            item_size = QTableWidgetItem(size)
            item_size.setFlags(item_size.flags() & ~Qt.ItemIsEditable)
            self.table_uncompressed.setItem(i, 4, item_size)
        self.checkboxes_uncompressed = checkboxes_uncompressed
        # Preenche tabela de comprimidos
        self.table_compressed.setRowCount(len(compressed))
        checkboxes_compressed = []
        for i, path in enumerate(compressed):
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, row=i: self.update_selected_queue(row, state))
            checkboxes_compressed.append(checkbox)
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.addWidget(checkbox)
            layout.setAlignment(checkbox, Qt.AlignCenter)
            layout.setContentsMargins(0,0,0,0)
            self.table_compressed.setCellWidget(i, 0, widget)
            name = os.path.basename(path)
            item_name = QTableWidgetItem(name)
            item_name.setFlags(item_name.flags() & ~Qt.ItemIsEditable)
            self.table_compressed.setItem(i, 1, item_name)
            platform = utils.get_platform_from_path(path)
            item_platform = QTableWidgetItem(platform)
            item_platform.setFlags(item_platform.flags() & ~Qt.ItemIsEditable)
            self.table_compressed.setItem(i, 2, item_platform)
            item_path = QTableWidgetItem(path)
            item_path.setFlags(item_path.flags() & ~Qt.ItemIsEditable)
            self.table_compressed.setItem(i, 3, item_path)
            if os.path.exists(path):
                size = utils.get_human_size(os.path.getsize(path))
            else:
                size = "(missing)"
            item_size = QTableWidgetItem(size)
            item_size.setFlags(item_size.flags() & ~Qt.ItemIsEditable)
            self.table_compressed.setItem(i, 4, item_size)
        self.checkboxes_compressed = checkboxes_compressed


    def update_queue_list(self):
        # Build a list of (action, name) tuples
        queue_items = []
        # COMPRESSED table: checked items = Uncompress
        for i, checkbox in enumerate(getattr(self, 'checkboxes_compressed', [])):
            if checkbox.isChecked():
                name = self.table_compressed.item(i, 1).text()
                queue_items.append(("Uncompress", name))
        # UNCOMPRESSED table: checked items = Compress
        for i, checkbox in enumerate(getattr(self, 'checkboxes_uncompressed', [])):
            if checkbox.isChecked():
                name = self.table_uncompressed.item(i, 1).text()
                queue_items.append(("Compress", name))
        # Populate the queue_table
        self.queue_table.setRowCount(len(queue_items))
        for row, (action, name) in enumerate(queue_items):
            action_item = QTableWidgetItem(action)
            action_item.setFlags(action_item.flags() & ~Qt.ItemIsEditable)
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.queue_table.setItem(row, 0, action_item)
            self.queue_table.setItem(row, 1, name_item)
        # Save queue to file every time it changes

    def update_selected_queue(self, row, state):
        self.update_queue_list()

    def open_settings(self):
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()

    def apply_table_search(self):
        search_text = self.search_edit.text().lower()
        filters = [f.strip() for f in search_text.split(',') if f.strip()]
        
        # Aplica o filtro para cada tabela e conta os itens visíveis
        total_uncompressed_visible = 0
        total_uncompressed_size_visible = 0
        total_compressed_visible = 0
        total_compressed_size_visible = 0
        
        # Tabela de ROMs não comprimidas
        for row in range(self.table_uncompressed.rowCount()):
            match = True if filters else True  # Se não há filtros, tudo deve corresponder
            for f in filters:
                found = False
                for col in range(1, self.table_uncompressed.columnCount()):
                    item = self.table_uncompressed.item(row, col)
                    if item and f in item.text().lower():
                        found = True
                        break
                if not found:
                    match = False
                    break
            
            # Oculta a linha se não corresponder ao filtro
            self.table_uncompressed.setRowHidden(row, not match)
            
            # Se a linha for visível (não oculta), adiciona ao total
            if not self.table_uncompressed.isRowHidden(row):
                total_uncompressed_visible += 1
                # Tenta obter o tamanho do arquivo se disponível
                path_item = self.table_uncompressed.item(row, 3)  # Coluna do caminho
                if path_item and os.path.exists(path_item.text()):
                    try:
                        total_uncompressed_size_visible += os.path.getsize(path_item.text())
                    except (OSError, IOError):
                        pass  # Ignora erros ao obter o tamanho do arquivo
        
        # Tabela de ROMs comprimidas
        for row in range(self.table_compressed.rowCount()):
            match = True if filters else True  # Se não há filtros, tudo deve corresponder
            for f in filters:
                found = False
                for col in range(1, self.table_compressed.columnCount()):
                    item = self.table_compressed.item(row, col)
                    if item and f in item.text().lower():
                        found = True
                        break
                if not found:
                    match = False
                    break
            
            # Oculta a linha se não corresponder ao filtro
            self.table_compressed.setRowHidden(row, not match)
            
            # Se a linha for visível (não oculta), adiciona ao total
            if not self.table_compressed.isRowHidden(row):
                total_compressed_visible += 1
                # Tenta obter o tamanho do arquivo se disponível
                path_item = self.table_compressed.item(row, 3)  # Coluna do caminho
                if path_item and os.path.exists(path_item.text()):
                    try:
                        total_compressed_size_visible += os.path.getsize(path_item.text())
                    except (OSError, IOError):
                        pass  # Ignora erros ao obter o tamanho do arquivo
        
        # Atualiza os rótulos de resumo com os novos totais
        if filters:
            # Se há filtros, mostra contagem dos itens visíveis
            self.uncompressed_label.setText(f"Uncompressed ROMs: {total_uncompressed_visible} | Total size: {utils.get_human_size(total_uncompressed_size_visible)}")
            self.compressed_label.setText(f"Compressed ROMs: {total_compressed_visible} | Total size: {utils.get_human_size(total_compressed_size_visible)}")
        else:
            # Se não há filtros, restaura a contagem original
            if hasattr(self, 'total_uncompressed_all'):
                self.uncompressed_label.setText(f"Uncompressed ROMs: {self.total_uncompressed_all} | Total size: {utils.get_human_size(self.total_uncompressed_size_all)}")
            if hasattr(self, 'total_compressed_all'):
                self.compressed_label.setText(f"Compressed ROMs: {self.total_compressed_all} | Total size: {utils.get_human_size(self.total_compressed_size_all)}")

    def update_table_row_for_path(self, file_path):
        # Atualiza apenas a linha correspondente ao arquivo processado
        need_update_totals = False
        for table in [self.table_uncompressed, self.table_compressed]:
            for row in range(table.rowCount()):
                item = table.item(row, 3)  # Coluna de path
                if item and item.text() == file_path:
                    # Exemplo: se o arquivo foi deletado, marca como (missing)
                    if not os.path.exists(file_path):
                        size_item = table.item(row, 4)
                        if size_item:
                            size_item.setText("(missing)")
                        need_update_totals = True
                    else:
                        size_item = table.item(row, 4)
                        if size_item:
                            size_item.setText(utils.get_human_size(os.path.getsize(file_path)))
                        need_update_totals = True
                    break
        
        # Se houve alteração de tamanho, recalcula os totais
        if need_update_totals:
            # Se houver filtro ativo, recalcula com o filtro
            if self.search_edit.text().strip():
                self.apply_table_search()
            else:
                self._recalculate_totals()

if __name__ == "__main__":
    app = QApplication([])
    window = RomCompressionGUI()
    window.show()
    app.exec()
