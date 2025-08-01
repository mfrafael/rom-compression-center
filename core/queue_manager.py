import os
QUEUE_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'queue.json')

def save_queue_to_file(queue):
    try:
        with open(QUEUE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[queue_manager] Failed to save queue: {e}")

def load_queue_from_file():
    if os.path.exists(QUEUE_FILE_PATH):
        try:
            with open(QUEUE_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[queue_manager] Failed to load queue: {e}")
    return []
import subprocess
import sys
import json
import os
import time
import threading

def run_queue(table_uncompressed, table_compressed, queue_table, status_label, delete_original=False, gui=None):
    queue = build_queue_from_tables(table_uncompressed, table_compressed, queue_table)
    platform_handlers = {
        'Nintendo Switch': handle_nintendo_switch_queue_item,
        # Adicione outras plataformas aqui
    }
    def queue_worker():
        for idx, item in enumerate(queue):
            if gui and getattr(gui, 'stop_queue_flag', False):
                status_label.setText("Queue stopped by user.")
                if gui:
                    gui.queue_finished()
                break
            platform = item['platform']
            handler = platform_handlers.get(platform)
            if handler:
                result = handler(item, status_label, delete_original, gui, sync=True)
                queue_table.removeRow(0)
            else:
                status_label.setText(f"Platform not implemented: {platform}")
        else:
            if gui:
                gui.queue_finished()
    thread = threading.Thread(target=queue_worker)
    thread.start()


def handle_nintendo_switch_queue_item(item, status_label, delete_original=False, gui=None, sync=False):
    nsz_queue = [{'action': item['action'], 'path': item['path']}]
    queue_file = os.path.join(os.path.dirname(__file__), '..', 'compression', 'nsz_queue_tmp.json')
    with open(queue_file, 'w', encoding='utf-8') as f:
        json.dump(nsz_queue, f, ensure_ascii=False, indent=2)
    processor_path = os.path.join(os.path.dirname(__file__), '..', 'compression', 'nsz_queue_processor.py')
    python_exe = sys.executable
    def run_nsz():
        try:
            proc = subprocess.Popen([python_exe, processor_path, queue_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if gui:
                gui.nsz_proc = proc
            for line in proc.stdout:
                if gui and getattr(gui, 'stop_queue_flag', False):
                    if gui:
                        gui.status_update_signal.emit("NSZ process interrupted by user.")
                    proc.terminate()
                    break
                if gui:
                    gui.status_update_signal.emit(line.strip())
            proc.wait()
            if proc.returncode == 0:
                if gui:
                    gui.status_update_signal.emit(f"Nintendo Switch queue processed: {item['action']}")
                if delete_original and os.path.exists(item['path']):
                    try:
                        os.remove(item['path'])
                        if gui:
                            gui.status_update_signal.emit(f"Arquivo deletado: {item['path']}")
                    except Exception as e:
                        if gui:
                            gui.status_update_signal.emit(f"Erro ao deletar arquivo: {e}")
            elif proc.returncode is not None:
                if gui:
                    gui.status_update_signal.emit(f"Error processing Nintendo Switch queue: código {proc.returncode}")
        except Exception as e:
            if gui:
                gui.status_update_signal.emit(f"Erro ao rodar NSZ: {e}")
        finally:
            if gui:
                gui.nsz_proc = None
            if os.path.exists(queue_file):
                os.remove(queue_file)
    if sync:
        run_nsz()
    else:
        thread = threading.Thread(target=run_nsz)
        thread.start()

def build_queue_from_tables(table_uncompressed, table_compressed, queue_table):
    queue = []
    for row in range(queue_table.rowCount()):
        action = queue_table.item(row, 0).text()
        name = queue_table.item(row, 1).text()
        found = False
        for table in [table_uncompressed, table_compressed]:
            for i in range(table.rowCount()):
                if table.item(i, 1).text() == name:
                    path = table.item(i, 3).text()
                    plat = table.item(i, 2).text()
                    queue.append({'action': action, 'name': name, 'path': path, 'platform': plat})
                    found = True
                    break
            if found:
                break
    save_queue_to_file(queue)
    return queue


def group_queue_by_platform_and_action(queue):
    from collections import defaultdict
    platform_groups = defaultdict(list)
    for item in queue:
        platform_groups[item['platform']].append(item)
    action_groups = {platform: defaultdict(list) for platform in platform_groups}
    for platform, items in platform_groups.items():
        for item in items:
            action_groups[platform][item['action']].append(item)
    return action_groups

def stop_nsz_process(gui):
    import time
    proc = getattr(gui, 'nsz_proc', None)
    if proc and proc.poll() is None:
        try:
            proc.terminate()
            time.sleep(1)  # Aguarda 1 segundo para encerrar
            if proc.poll() is None:
                proc.kill()
                gui.status_label.setText("NSZ process killed.")
            else:
                gui.status_label.setText("NSZ process terminated.")
        except Exception as e:
            gui.status_label.setText(f"Erro ao terminar NSZ: {e}")
    gui.nsz_proc = None

