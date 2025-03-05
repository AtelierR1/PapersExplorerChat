import customtkinter
import os
import sys
from graphrag.cli.index import index_cli
from pathlib import Path
import subprocess
import time
import tk_async_execute as tae
import asyncio
from graphrag.logging.types import ReporterType
from indexing.indexing import start_indexing
from async_tkinter_loop import async_handler

class StdoutRedirector(object):
    def __init__(self,wedgit):
        self.wedgit = wedgit

    def write(self,string):
        self.wedgit.insert("end", string)
        self.wedgit.see("end")
        
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
        self.text_space = customtkinter.CTkTextbox(self,corner_radius=10,activate_scrollbars=True,wrap="word",height = 10,width = 60)
        self.text_space.pack(pady=10,padx=5,fill="both",expand=True)
        # ボタン
        self.save_button = customtkinter.CTkButton(self,text="Start",command=self.push_button_event)
        self.save_button.pack(pady=10,side="right",padx=10)
        
        # ウィンドウの x ボタンが押された時に呼ばれるメソッドを設定
        self.protocol("WM_DELETE_WINDOW", self.delete_window)
        
    def delete_window(self):
        if self.status == 0:
            sys.stdout = sys.__stdout__
            if self.task:
                self.task.destroy()
        self.destroy()
        
    def push_button_event(self):
        if self.status == 0:# 未実行
            self.status = 1
            stdout = StdoutRedirector(self.text_space)
            self.save_button.configure(text="Close")
            self.save_button.configure(state="disable")
            self.task = tae.async_execute(self.start_process(stdout), wait=False, visible=False, pop_up=False,callback=self.finish_process)
        elif self.status == 2:# 実行後
            self.destroy()
        
    def finish_process(self):
        self.status = 2
        self.save_button.configure(state="enable")
        self.save_button.configure(text="Close")
        self.task = None
        
    async def start_process(self,stdout):
        sys.stdout = stdout
        print("Start indexing")
        await start_indexing(Path("./ragdata"), None)
        print("Finish indexing")
        sys.stdout = sys.__stdout__
        


