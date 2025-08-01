from PySide6.QtCore import QObject, Signal, QThread
import subprocess, sys, json, os

class QueueWorker(QObject):
    status_update = Signal(str)
    finished = Signal()
    item_finished = Signal()
    item_processed = Signal(str)

    def __init__(self, queue, queue_table, delete_original, verbose=False):
        super().__init__()
        self.queue = queue
        self.queue_table = queue_table
        self.delete_original = delete_original
        self.stop_flag = False
        self.verbose = verbose

    def stop(self):
        self.stop_flag = True

    def run(self):
        from core.queue_manager import get_platform_handler
        for idx, item in enumerate(self.queue):
            if self.stop_flag:
                self.status_update.emit("Queue stopped by user.")
                break
            platform = item['platform']
            handler = get_platform_handler(platform)
            if handler:
                # Não passa o parâmetro verbose para os handlers
                handler(item, self.status_update, self.delete_original, self, sync=True)
                self.queue_table.removeRow(0)
                self.item_finished.emit()
                self.item_processed.emit(item['path'])
            else:
                self.status_update.emit(f"Platform not implemented: {platform}")
        self.finished.emit()

# Exemplo de handler adaptado para QThread

def handle_nintendo_switch_queue_item(item, status_update, delete_original=False, worker=None, sync=False):
    #status_update.emit(f"[DEBUG] Valor de delete_original recebido: {delete_original}")
    nsz_queue = [{'action': item['action'], 'path': item['path']}]
    queue_file = os.path.join(os.path.dirname(__file__), '..', 'compression', 'nsz_queue_tmp.json')
    with open(queue_file, 'w', encoding='utf-8') as f:
        json.dump(nsz_queue, f, ensure_ascii=False, indent=2)
    processor_path = os.path.join(os.path.dirname(__file__), '..', 'compression', 'nsz_queue_processor.py')
    python_exe = sys.executable
    try:
        # Executa o processo NSZ
        proc = subprocess.Popen([python_exe, processor_path, queue_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Lê a saída do processo
        for line in proc.stdout:
            if worker and worker.stop_flag:
                status_update.emit("NSZ process interrupted by user.")
                proc.terminate()
                break
            status_update.emit(line.strip())
        
        # Espera o processo terminar
        proc.wait()
        
        # Verifica o resultado
        if proc.returncode == 0:
            status_update.emit(f"Nintendo Switch queue processed: {item['action']}")
        elif proc.returncode is not None:
            status_update.emit(f"Error processing Nintendo Switch queue: código {proc.returncode}")

        # Após o término do processo, tenta deletar se sucesso
        if proc.returncode == 0 and delete_original:
            file_path = item.get('path')
            status_update.emit(f"Tentando deletar arquivo: {file_path}")
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    status_update.emit(f"Arquivo deletado: {file_path}")
                except Exception as e:
                    status_update.emit(f"Erro ao deletar arquivo: {e}")
            else:
                status_update.emit(f"Arquivo para deletar não encontrado: {file_path}")
    except Exception as e:
        status_update.emit(f"Erro ao rodar NSZ: {e}")
    finally:
        if os.path.exists(queue_file):
            os.remove(queue_file)
