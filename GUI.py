#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tkinter
from tkinter import *
import cv2
from PIL import Image, ImageTk
from tkinter import filedialog

class Mytk():
    def __init__(self):
        self.win = tkinter.Tk()
        self.win.title("yudanqu")
        self.win.geometry("1100x600+200+50")
        self.win.resizable(width=False, height=False)  # 防止用户调整尺寸

        self.roi_method = None

        # 创建一个listbox，添加几个元素
        self.lb = tkinter.Listbox(self.win, selectmode=tkinter.BROWSE,width=30,height=20)
        self.lb.grid(row=0, column=0, padx=20, pady=20)

        self.lmian = Label()
        self.lmian.grid(row=0, column=1, padx=50, pady=10)

        self.button1 = tkinter.Button(self.win, text="开始", width=10, height=2)
        self.button1.grid(row=1, column=0, padx=10, pady=5)

        self.frame1 = Frame(self.win)
        self.frame1.grid(row=1, column=1, padx=10, pady=5)

        self.button2 = tkinter.Button(self.frame1, text="选择文件夹", command=self.select_file, width=10, height=1)
        self.button2.grid(row=0, column=3, padx=10, pady=5)

        self.text = tkinter.Text(self.frame1, width=50, height=1)
        self.text.grid(row=0, column=4, padx=0, pady=0)

        self.r = tkinter.IntVar()
        self.radio1 = tkinter.Radiobutton(self.frame1, text="yolo_detect", value=1, variable=self.r, command=self.updata1)
        self.radio1.grid(row=0, column=1, padx=10, pady=5)
        self.radio2 = tkinter.Radiobutton(self.frame1, text="manual_select", value=2, variable=self.r, command=self.updata2)
        self.radio2.grid(row=0, column=2, padx=10, pady=5)


        frame = cv2.imread(f'img.png')
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmian.imgtk = imgtk
        self.lmian.configure(image=imgtk)

        self.win.mainloop()

    def insert_info(self,):
        for item in ["good", "nice", "handsome", "aaa", "bbb", "ccc", "ddd"]:
        # 按顺序添加
            self.lb.insert(tkinter.END, item)

    def updata1(self):
        self.roi_method = 'yolo'

    def updata2(self):
        self.roi_method = 'manual'

    def select_file(self,):
        self.img_path = filedialog.askopenfilename()
        self.str = self.img_path
        self.text.insert(tkinter.INSERT, self.str)

if __name__ == '__main__':
    mytk = Mytk()
