import customtkinter
import os
import sys
from graphrag.cli.index import index_cli
from pathlib import Path
import subprocess
import time
import tk_async_execute as tae
import asyncio
import subprocess
import sys
import queue
import threading
import ctypes
import time
class CreateDBDialog(customtkinter.CTkToplevel):
    def __init__(self,master):
        super().__init__(master)
        self.status = 0
        self.task = None
        # ウィンドウの設定
        self.title("DBの作成")
        self.geometry("640x380")
        self.wm_minsize(380,460)
        
        # テキスト表示
        api_key_label = customtkinter.CTkLabel(self,text="csvファイルをragdata/input内に格納してください",anchor="w")
        api_key_label.pack(fill="x",anchor="w",padx=10)
        
        api_key_label = customtkinter.CTkLabel(self,text="Startボタンを押すとDB作成が始まります。(時間がかかります)",anchor="w")
        api_key_label.pack(fill="x",anchor="w",padx=10)
        
        # テキストボックス
        self.text_space = customtkinter.CTkTextbox(self,corner_radius=10,activate_scrollbars=True,wrap="word",height = 10)
        self.text_space.pack(pady=10,padx=5,fill="both",expand=True)
        # ボタン
        self.save_button = customtkinter.CTkButton(self,text="Start",command=self.push_button_event)
        self.save_button.pack(pady=10,side="right",padx=10)
        
        # ウィンドウの x ボタンが押された時に呼ばれるメソッドを設定
        self.protocol("WM_DELETE_WINDOW", self.delete_window)
    
    # x ボタンが押された時に呼ばれるメソッド
    def delete_window(self):
        # プロセスが終了していない場合は強制終了
        if self.proc.poll() is None:
            self.proc.kill()
        # 配列実行しているスレッドを終了
        if self.task is not None:
            while self.process_alive:
                self.task.update()
                time.sleep(0.1)
            self.task.destroy()
        self.destroy()
    
    # Start/Closeボタンのクリック
    def push_button_event(self):
        #②回目の実行は閉じる
        if self.status == 1:
            self.delete_window()
            return
        self.status = 1
        self.save_button.configure(text="Close")
        self.save_button.configure(state="disabled")
        # プロセスを実行して、標準出力を受け取るようのスレッドを起動する
        cmd = [sys.executable,"-m","graphrag","index","--root","./ragdata","--reporter","print"]
        self.proc = subprocess.Popen(" ".join(cmd),shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=os.getcwd())
        self.task = tae.async_execute(self.print_process(), wait=False, visible=False, pop_up=False)
        
    # 標準出力を受け取るスレッド
    async def print_process(self):
        self.process_alive = True
        stdout_queue = queue.Queue()
        self.thread = threading.Thread(target=self.process_stdout_thread,args=(self.proc.stdout,stdout_queue))
        self.thread.start()
        while True:
            # キューから受け取った出力をテキストボックスに出力する
            if not stdout_queue.empty():
                line = stdout_queue.get()
                tae.tk_execute(self.text_space.insert,"end", line)
                tae.tk_execute(self.text_space.see,"end")
            # プロセスが終了していれば抜ける
            if stdout_queue.empty() and self.proc.poll() is not None:
                break
        tae.tk_execute(self.save_button.configure,state="normal")
        ctypes.pythonapi.PyThreadState_SetAsyncExc(
            self.thread.ident, ctypes.py_object(SystemExit)
        )
        self.process_alive = False
        
    # 受け取った標準出力をキューにためる
    def process_stdout_thread(self,stdout,stdout_queue):
        while True:
            for line in iter(stdout.readline, b''):
                if len(line) > 0:
                    line = line.decode(errors="replace")
                    stdout_queue.put(line)


