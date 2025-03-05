import sys
import os
import asyncio
import customtkinter
import tkinter.font as tkfont
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from search.global_search import GlobalSearchEngine
from search.local_search import LocalSearchEngine
from async_tkinter_loop.mixins import AsyncCTk
from async_tkinter_loop import async_handler, async_mainloop
from customtkinter.windows.widgets.theme import ThemeManager
from UI.api_setting_dialog import APISettingDialog
from UI.create_DB_dialog import CreateDBDialog
import tk_async_execute as tae
import asyncio
FONT_TYPE = "meiryo"

# チャットバブル
class ChatBubble(customtkinter.CTkTextbox):
    def __init__(self,master,text,fg_color,sender):
        super().__init__(master,fg_color=fg_color,text_color="black",corner_radius=10,activate_scrollbars=False,wrap="word",height = 0,width = 0)
        
        if sender == "user":
            self.configure(fg_color=fg_color)
            self.pack(side = "top",padx=(20,5),pady=2,anchor="e",fill="none",expand=False)
        else:
            self.configure(fg_color=fg_color)
            self.pack(side = "top",padx=(5,20),pady=2,anchor="w",fill="none",expand=False)
            
        self.font = tkfont.Font(font=self.cget("font"))
        self.insert("0.0",text)
        self.configure(state="disable")
        
        self.max_width = max([self._font.measure(row) for row in text.splitlines()]) + 20
        self.configure(width=self.max_width + 5)
        
        self.bind("<Configure>",self.adjust_size)
        self.adjust_size()
        
    # チャットの高さを自動調整します
    def adjust_size(self,event=None):
        display_lines = self._textbox.count("1.0","end","displaylines")[0]        
        self._textbox.configure(height=display_lines)    
     
# ローディング中のチャットバブル
class LoadingBubble(customtkinter.CTkTextbox):
    def __init__(self,master,sender):
        super().__init__(master,fg_color="lightblue",text_color="black",corner_radius=10,activate_scrollbars=False,wrap="word",height = 0,width = 0)
        
        if sender == "user":
            self.pack(side = "top",padx=(20,5),pady=2,anchor="e",fill="none",expand=False)
        else:
            self.pack(side = "top",padx=(5,20),pady=2,anchor="w",fill="none",expand=False)
            
        self.font = tkfont.Font(font=self.cget("font"))
        self.insert("0.0","...")
        self.configure(state="disable")
        
        self.max_width = self._font.measure(max("...".splitlines())) + 20
        self.configure(width=self.max_width + 5)
        
        self.bind("<Configure>",self.adjust_size)
        self.adjust_size()
        
    # チャットの高さを自動調整します
    def adjust_size(self,event=None):
        display_lines = self._textbox.count("1.0","end","displaylines")[0]        
        self._textbox.configure(height=display_lines)    

            
# チャット表示領域のGUIです  
class ChatArea(customtkinter.CTkScrollableFrame):
    def __init__(self,master,**kwargs):
        super().__init__(master,**kwargs)
        # add widgets onto the frame...
        self.chat_histories = list()
        
        # self.chat_histories.append(LoadingBubble(self,sender="bot"))
                    
    # 表示内容のリストを返します
    def get(self):
        return self.chat_histories
    
    # チャットの追加
    def add_chat(self,text,color,sender="user",):
        label = ChatBubble(self,text=text,fg_color=color,sender=sender)
        self.chat_histories.append(label)
        self._parent_canvas.yview("moveto","1.0")
         
         
class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        # メンバー変数の設定
        self.fonts = (FONT_TYPE, 15)
        # フォームサイズ設定
        self.geometry("640x480")
        self.title("Basic GUI")

        self.search_mode = "local"
        # フォームのセットアップをする
        self.setup_form()
                
        self.local_search = LocalSearchEngine()
        self.global_search = GlobalSearchEngine()
        self.local_search.build()
        self.global_search.build()

    def setup_form(self):
        # CustomTkinter のフォームデザイン設定
        customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)
        
        grid_row_index = 0
        # settingボタンの表示
        self.setting_button = customtkinter.CTkButton(master=self, text="api 設定",width=200, height=30,command=self.push_api_setting_button_event)
        self.setting_button.grid(row=grid_row_index,column = 0,padx=0, pady=0, sticky="w")
        self.grid_rowconfigure(grid_row_index, weight=0)
        self.setting_button.grid_propagate(False)
        
        # データ作成ボタンの表示
        # self.DB_create_button = customtkinter.CTkButton(master=self, text="DB作成",width=200, height=30,command=self.push_DB_create_button_event)
        # self.DB_create_button.grid(row=grid_row_index,column = 1,padx=0, pady=0, sticky="w")
        # self.grid_rowconfigure(grid_row_index, weight=0)
        # self.DB_create_button.grid_propagate(False)

        grid_row_index += 1
        # チャットメッセージ表示領域の表示
        self.chat_area = ChatArea(master=self)
        self.chat_area.grid(row=grid_row_index, column=0,columnspan = 2, padx=0, pady=0, sticky="nsew")
        self.grid_rowconfigure(grid_row_index, weight=3)
        
        grid_row_index += 1
        # 検索モードボタンの表示
        self.search_mode_label = customtkinter.CTkLabel(master=self,width=100,text="search mode",font=self.fonts)
        self.search_mode_label.grid(row=grid_row_index,column = 0,padx=0, pady=0)
        self.search_mode_SW = customtkinter.CTkSwitch(master=self, text="local",width=100,height=40, command=self.toggle_search_mode)
        self.search_mode_SW.grid(row=grid_row_index,column = 1,padx=0, pady=0,sticky="w")
        self.grid_rowconfigure(grid_row_index, weight=0)
        
        grid_row_index += 1
        # テキストボックスを表示する
        self.textbox = customtkinter.CTkTextbox(master=self, fg_color="white",text_color="black",font=self.fonts)
        self.textbox.grid(row=grid_row_index, column=0, padx=0, pady=0, sticky="nsew",columnspan=2)
        self.grid_rowconfigure(grid_row_index, weight=1, minsize=30)
        self.textbox.bind("<<Modified>>", self.on_text_changed)
        # Enterキーを送信ボタンにする
        # self.textbox.bind("<Return>", push_send_button_event)
        
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        
        grid_row_index += 1
        # 送信ボタンの表示
        self.send_button = customtkinter.CTkButton(master=self, text="send",height=30, command=self.push_send_button_event)
        self.send_button.grid(row=grid_row_index,column = 0,padx=0, pady=0, sticky="ew",columnspan=2)
        self.send_button.configure(state="disabled")
        self.send_button.configure(fg_color="gray")
        self.grid_rowconfigure(grid_row_index, weight=0)
        
    # 検索モードを切り替えたときのイベント
    def toggle_search_mode(self):
        self.search_mode = "local" if self.search_mode_SW.get() == 0 else "global"
        self.search_mode_SW.configure(text=self.search_mode)
    
    # テキストボックスが変化したときのイベント
    def on_text_changed(self,event):
        # テキストボックスに入力されるまで送信ボタンを押せなくする
        text = self.textbox.get("1.0","end-1c")
        if len(text) > 0:
            self.send_button.configure(state="normal")
            self.send_button.configure(fg_color=ThemeManager.theme["CTkButton"]["fg_color"])
        else:
            self.send_button.configure(state="disabled")
            self.send_button.configure(fg_color="gray")
        self.textbox.edit_modified(False)
    
    # API設定ボタンが押されたときのイベント
    def push_api_setting_button_event(self):    
        # ダイアログを表示
        dialog = APISettingDialog(self,"ragdata/.env")
        # モーダルにする設定
        dialog.grab_set()        # モーダルにする
        dialog.focus_set()       # フォーカスを新しいウィンドウをへ移す
        dialog.transient(self.master)   # タスクバーに表示しない
        self.wait_window(dialog)
        if dialog.return_status == 1:
            self.local_search.build()
            self.global_search.build()
    
    # DB作成ボタンが押されたときのイベント
    def push_DB_create_button_event(self):
         # ダイアログを表示
        dialog = CreateDBDialog(self)
        # モーダルにする設定
        dialog.grab_set()        # モーダルにする
        dialog.focus_set()       # フォーカスを新しいウィンドウをへ移す
        dialog.transient(self.master)   # タスクバーに表示しない
        self.wait_window(dialog)

    
    # 送信ボタンが押されたときのイベント   
    def push_send_button_event(self):
        text = self.textbox.get("1.0","end-1c")
        self.textbox.delete("1.0","end")
        self.chat_area.add_chat(text,"white","user")
        
        # botからの返信
        # await self.send_bot_message(text)
        tae.async_execute(self.send_bot_message(text),wait=True,visible=False,pop_up=False)
        return 0
        
    # botにメッセージを送信します
    async def send_bot_message(self,text):
        text = text + "\n以上の質問に、論文名以外は日本語で回答してください。"
        if self.search_mode == "global":
            res,response = await self.global_search.search(text)
            if res == -1:
                self.chat_area.add_chat("error:\n{}".format(response),"pink","bot")
            else:
                self.chat_area.add_chat("global:\n{}".format(response),"yellow","bot")
        else:
            res,response = await self.local_search.search(text)
            if res == -1:
                self.chat_area.add_chat("error:\n{}".format(response),"pink","bot")
            else:
                self.chat_area.add_chat("local:\n{}".format(response),"lightblue","bot")
        return 0
        
def exec():
    # アプリケーション実行
    app = App()
    tae.start()
    # app.async_mainloop()
    app.mainloop()
    tae.stop()
    
