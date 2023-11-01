import tkinter as tk
from tkinter import ttk, filedialog
import time
import os
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

def configure_style():
    style = ttk.Style()

    # Defina o fundo amarelo
    style.configure("Treeview", background="white")

    # Defina a cor da fonte em vermelho
    style.configure("Treeview", foreground="red")

    # Defina a fonte em negrito
    style.configure("Treeview", font=('Helvetica', 11, 'bold'))

def sort_column(tree, col, reverse):
    data = [(tree.set(item, col), item) for item in tree.get_children('')]
    data.sort(reverse=reverse)
    for item in data:
        tree.move(item[1], '', 'end')
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

class MonitorHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            self.log_event("Arquivo modificado", event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.log_event("Arquivo criado", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.log_event("Arquivo removido", event.src_path)

    def on_moved(self, event):
        self.log_event(f"Arquivo movido de {event.src_path} para {event.dest_path}")

    def log_event(self, message, path=None):
        data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        usuario = get_username()
        if path:
            treeview.insert('', 'end', values=(data_hora, usuario, message, path))
        else:
            treeview.insert('', 'end', values=(data_hora, usuario, message, ""))

def get_username():
    if os.name == 'posix':
        return 'Usuário Desconhecido'
    elif os.name == 'nt':
        import getpass
        return getpass.getuser()
    else:
        return 'Usuário Desconhecido'

def start_monitoring(diretorio, treeview):
    event_handler = MonitorHandler()
    event_handler.treeview = treeview
    observer = Observer()
    observer.schedule(event_handler, path=diretorio, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def browse_for_directory():
    diretorio = filedialog.askdirectory()
    if diretorio:
        selected_directory_label.config(text=f"Selecionado: {diretorio}")
        thread = threading.Thread(target=start_monitoring, args=(diretorio, treeview))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    # Crie a janela Tkinter
    root = tk.Tk()
    root.title("Monitor de Alterações em Arquivos")

    # Configure o estilo
    configure_style()

    # Crie o cabeçalho da tabela
    columns = ("Data/Hora", "Usuário", "Ação", "Arquivo")
    treeview = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        treeview.heading(col, text=col, command=lambda c=col: sort_column(treeview, c, False))
        treeview.column(col, width=200)  # Defina a largura das colunas conforme necessário
    treeview.pack(fill="both", expand=True)

    # Crie um botão para selecionar a pasta a ser monitorada
    select_directory_button = tk.Button(root, text="Selecionar Pasta", command=browse_for_directory)
    select_directory_button.pack()

    # Label para exibir a pasta selecionada
    selected_directory_label = tk.Label(root, text="")
    selected_directory_label.pack()

    # Inicie a interface gráfica
    root.mainloop()
