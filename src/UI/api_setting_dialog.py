import customtkinter
from dotenv import load_dotenv
import os

class APISettingDialog(customtkinter.CTkToplevel):
    def __init__(self,master,env_file_path):
        super().__init__(master)
        self.return_status = 0
        
        self.env_file_path = env_file_path
        
        
        load_dotenv(self.env_file_path,override=True)
        
        # ウィンドウの設定
        self.title("APIキー設定")
        self.geometry("640x380")
        self.wm_minsize(380,460)
        
        # APIキー設定
        api_key_label = customtkinter.CTkLabel(self,text="API Key",anchor="w")
        api_key_label.pack(fill="x",anchor="w",padx=10)
        self.api_key_entry = customtkinter.CTkEntry(self)
        self.api_key_entry.insert(0,os.environ["AZURE_OPENAI_API_KEY"])
        self.api_key_entry.pack(fill="x",padx=10,pady=(0,5))
        # エンドポイント設定
        endpoint_label = customtkinter.CTkLabel(self,text="Endpoint",anchor="w")
        endpoint_label.pack(fill="x",anchor="w",padx=10)
        self.endpoint_entry = customtkinter.CTkEntry(self)
        self.endpoint_entry.insert(0,os.environ["OPENAI_ENDPOINT"])
        self.endpoint_entry.pack(fill="x",padx=10,pady=(0,5))
        # モデル名設定(LLM)
        llm_model_name_label = customtkinter.CTkLabel(self,text="LLM model name",anchor="w")
        llm_model_name_label.pack(fill="x",anchor="w",padx=10)
        self.llm_model_name_entry = customtkinter.CTkEntry(self)
        self.llm_model_name_entry.insert(0,os.environ["GRAPHRAG_LLM_MODEL"])
        self.llm_model_name_entry.pack(fill="x",padx=10,pady=(0,5))
        # モデル名設定(Emedding)
        embed_model_name_label = customtkinter.CTkLabel(self,text="Embedding model name",anchor="w")
        embed_model_name_label.pack(fill="x",anchor="w",padx=10)
        self.embed_model_name_entry = customtkinter.CTkEntry(self)
        self.embed_model_name_entry.insert(0,os.environ["GRAPHRAG_EMBEDDING_MODEL"])
        self.embed_model_name_entry.pack(fill="x",padx=10,pady=(0,5))
        # HTTPプロキシ設定
        http_proxy_label = customtkinter.CTkLabel(self,text="HTTP proxy",anchor="w")
        http_proxy_label.pack(fill="x",anchor="w",padx=10)
        self.http_proxy_entry = customtkinter.CTkEntry(self)
        self.http_proxy_entry.insert(0,os.environ["HTTP_PROXY"])
        self.http_proxy_entry.pack(fill="x",padx=10,pady=(0,5))
        
        # 保存ボタン
        self.save_button = customtkinter.CTkButton(self,text="Save",command=self.push_save_button_event)
        self.save_button.pack(pady=10,side="right",padx=10)
        # self.api_key = custom
        
    def push_save_button_event(self):
        with open(self.env_file_path,"w") as f:
            f.write(f"AZURE_OPENAI_API_KEY=\"{self.api_key_entry.get()}\"\n")
            f.write(f"OPENAI_ENDPOINT=\"{self.endpoint_entry.get()}\"\n")
            f.write(f"GRAPHRAG_LLM_MODEL=\"{self.llm_model_name_entry.get()}\"\n")
            f.write(f"GRAPHRAG_EMBEDDING_MODEL=\"{self.embed_model_name_entry.get()}\"\n")
            f.write(f"OPENAI_API_TYPE=\"azure\"\n")
            f.write(f"HTTP_PROXY=\"{self.http_proxy_entry.get()}\"\n")
            f.write(f"HTTPS_PROXY=\"{self.http_proxy_entry.get()}\"\n")
            f.write(f"API_VERSION = \"2024-02-15-preview\"\n")
        self.destroy()
        self.return_status = 1