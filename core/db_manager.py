def populate_table_db(gui, details_list):
    """Fill tables in GUI using only DB data, never access disk."""
    from compression.compression_formats import is_compressed
    from PySide6.QtWidgets import QCheckBox, QWidget, QHBoxLayout, QTableWidgetItem
    from PySide6.QtCore import Qt
    uncompressed = []
    compressed = []
    for d in details_list:
        name = d['file_name']
        path = d['path']
        platform = d['platform']
        size = d['size']
        if is_compressed(name):
            compressed.append((name, platform, path, size))
        else:
            uncompressed.append((name, platform, path, size))
    # Fill uncompressed table
    gui.table_uncompressed.setRowCount(len(uncompressed))
    checkboxes_uncompressed = []
    for i, row in enumerate(uncompressed):
        checkbox = QCheckBox()
        checkbox.stateChanged.connect(lambda state, row=i: gui.update_selected_queue(row, state))
        checkboxes_uncompressed.append(checkbox)
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(checkbox)
        layout.setAlignment(checkbox, Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        gui.table_uncompressed.setCellWidget(i, 0, widget)
        item_name = QTableWidgetItem(row[0])
        item_name.setFlags(item_name.flags() & ~Qt.ItemIsEditable)
        gui.table_uncompressed.setItem(i, 1, item_name)
        item_platform = QTableWidgetItem(row[1])
        item_platform.setFlags(item_platform.flags() & ~Qt.ItemIsEditable)
        gui.table_uncompressed.setItem(i, 2, item_platform)
        item_path = QTableWidgetItem(row[2])
        item_path.setFlags(item_path.flags() & ~Qt.ItemIsEditable)
        gui.table_uncompressed.setItem(i, 3, item_path)
        item_size = QTableWidgetItem(row[3])
        item_size.setFlags(item_size.flags() & ~Qt.ItemIsEditable)
        gui.table_uncompressed.setItem(i, 4, item_size)
    gui.checkboxes_uncompressed = checkboxes_uncompressed
    # Fill compressed table
    gui.table_compressed.setRowCount(len(compressed))
    checkboxes_compressed = []
    for i, row in enumerate(compressed):
        checkbox = QCheckBox()
        checkbox.stateChanged.connect(lambda state, row=i: gui.update_selected_queue(row, state))
        checkboxes_compressed.append(checkbox)
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(checkbox)
        layout.setAlignment(checkbox, Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        gui.table_compressed.setCellWidget(i, 0, widget)
        item_name = QTableWidgetItem(row[0])
        item_name.setFlags(item_name.flags() & ~Qt.ItemIsEditable)
        gui.table_compressed.setItem(i, 1, item_name)
        item_platform = QTableWidgetItem(row[1])
        item_platform.setFlags(item_platform.flags() & ~Qt.ItemIsEditable)
        gui.table_compressed.setItem(i, 2, item_platform)
        item_path = QTableWidgetItem(row[2])
        item_path.setFlags(item_path.flags() & ~Qt.ItemIsEditable)
        gui.table_compressed.setItem(i, 3, item_path)
        item_size = QTableWidgetItem(row[3])
        item_size.setFlags(item_size.flags() & ~Qt.ItemIsEditable)
        gui.table_compressed.setItem(i, 4, item_size)
    gui.checkboxes_compressed = checkboxes_compressed
def get_all_roms():
    """Return all ROMs as list of dicts with keys: file_name, platform, path, size, action."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT file_name, platform, path, size, action FROM roms")
    rows = c.fetchall()
    conn.close()
    # Return as list of dicts for compatibility
    return [
        {
            'file_name': row[0],
            'platform': row[1],
            'path': row[2],
            'size': row[3],
            'action': row[4]
        }
        for row in rows
    ]

import os
import sqlite3

DB_PATH = "core/roms.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS roms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            platform TEXT,
            path TEXT,
            size TEXT,
            action TEXT
        )
    """)
    conn.commit()
    conn.close()


def load_table_from_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT file_name, platform, path, size, action FROM roms")
    rows = c.fetchall()
    conn.close()
    return rows


def insert_roms(details_list):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for detail in details_list:
        c.execute("INSERT INTO roms (file_name, platform, path, size, action) VALUES (?, ?, ?, ?, ?)", detail)
    conn.commit()
    conn.close()


def clear_roms():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM roms")
    conn.commit()
    conn.close()
