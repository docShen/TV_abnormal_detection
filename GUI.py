#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import tkinter
from tkinter import *
import cv2
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import Tk, font
from move_detection import Move_D
class Mytk():
    def __init__(self):
        self.win = tkinter.Tk()
        self.win.title("中央监视器异常检测系统")
        self.win.geometry("2400x1250+100+50")
        self.win.resizable(width=False, height=False)  # 防止用户调整尺寸
        self.roi_method = None

        # 创建一个listbox，添加几个元素
        self.frame0 = Frame(self.win)
        self.frame0.grid(row=0, column=0, padx=20, pady=20)

        self.label_anomal = tkinter.Label(self.frame0,justify=LEFT,text = 'INFOMATION',font=30, width=30, height=5)
        self.label_anomal.grid(row=0, column=0, padx=0, pady=0)

        self.lb = tkinter.Listbox(self.frame0, selectmode=tkinter.BROWSE,width=60,height=60)
        self.lb.grid(row=1, column=0, padx=20, pady=20)

        self.lmian = Label()
        self.lmian.grid(row=0, column=1, padx=50, pady=10)

        self.button1 = tkinter.Button(self.win, text="Start",command=self.get_roi, width=15, height=3)
        self.button1.grid(row=1, column=0, padx=10, pady=5)

        self.frame1 = Frame(self.win)
        self.frame1.grid(row=1, column=1, padx=10, pady=5)

        self.button2 = tkinter.Button(self.frame1, text="select files", command=self.select_file, width=20, height=2)
        self.button2.grid(row=0, column=3, padx=10, pady=5)

        self.text = tkinter.Text(self.frame1, width=50, height=3)
        self.text.grid(row=0, column=4, padx=0, pady=0)

        self.r = tkinter.IntVar()
        self.radio1 = tkinter.Radiobutton(self.frame1, text="yolo_detect", value= 1 , anchor='w',variable=self.r, command=self.updata1,width=10,height=1)
        self.radio1.grid(row=0, column=1, padx=10, pady=5)
        self.radio2 = tkinter.Radiobutton(self.frame1, text="manual_select", value=2 , anchor='w', variable=self.r, command=self.updata2,width=10,height=1)
        self.radio2.grid(row=0, column=2, padx=10, pady=5)
        self.win.mainloop()

    def get_roi(self):
        if self.roi_method == None:
            print('没有选择框的方式!')
        if self.roi_method != None:
            self.my_det = Move_D(self.img_path)
            self.my_det.get_bbox(yolo_box=self.roi_method)
            self.detection(self.my_det.all_frame)

    def detection(self,all_frame):
        self.lb.delete(0, END)

        for idx, f_img in enumerate(all_frame):
            origin_frame,anolist = self.my_det.move_detec(idx,f_img)
            self.video_stream(origin_frame)
            if anolist[0] != None:
                self.insert_info(anolist[0])
            if anolist[1] != None:
                self.insert_info(anolist[1])
            if anolist[2] != None:
                self.insert_info(anolist[2])

    def video_stream(self,frame):
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmian.imgtk = imgtk
        self.lmian.configure(image=imgtk)
        time.sleep(1 / (self.my_det.fps + 10))
        self.win.update()

    def insert_info(self,info):
        self.lb.insert(tkinter.END, info)

    def updata1(self):
        self.roi_method = True

    def updata2(self):
        self.roi_method = False

    def select_file(self,):
        self.img_path = filedialog.askopenfilename()
        self.text.insert(tkinter.INSERT, self.img_path)

if __name__ == '__main__':
    mytk = Mytk()
