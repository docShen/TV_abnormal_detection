import copy
import time
import cv2 as cv
import numpy as np
# from draw_rectangle import *
from yolo_demo import detect

import copy
import cv2
import numpy as np

WIN_NAME = 'draw_rect'


class Rect(object):
    def __init__(self):
        self.tl = (0, 0)
        self.br = (0, 0)

    def regularize(self):
        """
        make sure tl = TopLeft point, br = BottomRight point
        """
        pt1 = (min(self.tl[0], self.br[0]), min(self.tl[1], self.br[1]))
        pt2 = (max(self.tl[0], self.br[0]), max(self.tl[1], self.br[1]))
        self.tl = pt1
        self.br = pt2


class DrawRects(object):
    def __init__(self, image, color, thickness=1):
        self.original_image = image
        self.image_for_show = image.copy()
        self.color = color
        self.thickness = thickness
        self.rects = []
        self.current_rect = Rect()
        self.left_button_down = False

        self.xy_list = []
        self.xy_afer_list = []

    @staticmethod
    def __clip(value, low, high):
        """
        clip value between low and high

        Parameters
        ----------
        value: a number
            value to be clipped
        low: a number
            low limit
        high: a number
            high limit

        Returns
        -------
        output: a number
            clipped value
        """
        output = max(value, low)
        output = min(output, high)
        return output

    def shrink_point(self, x, y):
        """
        shrink point (x, y) to inside image_for_show

        Parameters
        ----------
        x, y: int, int
            coordinate of a point

        Returns
        -------
        x_shrink, y_shrink: int, int
            shrinked coordinate
        """
        height, width = self.image_for_show.shape[0:2]
        x_shrink = self.__clip(x, 0, width)
        y_shrink = self.__clip(y, 0, height)
        return (x_shrink, y_shrink)

    def append(self):
        """
        add a rect to rects list
        """
        self.rects.append(copy.deepcopy(self.current_rect))

    def pop(self):
        """
        pop a rect from rects list
        """
        rect = Rect()
        if self.rects:
            rect = self.rects.pop()
        return rect

    def reset_image(self):
        """
        reset image_for_show using original image
        """
        self.image_for_show = self.original_image.copy()

    def draw(self):
        """
        draw rects on image_for_show
        """
        for rect in self.rects:
            cv2.rectangle(self.image_for_show, rect.tl, rect.br,
                          color=self.color, thickness=self.thickness)

    def draw_current_rect(self):
        """
        draw current rect on image_for_show
        """
        cv2.rectangle(self.image_for_show,
                      self.current_rect.tl, self.current_rect.br,
                      color=self.color, thickness=self.thickness)

    def onmouse_draw_rect(self, event, x, y, flags, draw_rects):
        if event == cv2.EVENT_LBUTTONDOWN:
            # pick first point of rect
            self.xy_list.append([x, y])
            print('pt1: x = %d, y = %d' % (x, y))
            draw_rects.left_button_down = True
            draw_rects.current_rect.tl = (x, y)
        if draw_rects.left_button_down and event == cv2.EVENT_MOUSEMOVE:
            # pick second point of rect and draw current rect
            draw_rects.current_rect.br = draw_rects.shrink_point(x, y)
            draw_rects.reset_image()
            draw_rects.draw()
            draw_rects.draw_current_rect()
        if event == cv2.EVENT_LBUTTONUP:
            # finish drawing current rect and append it to rects list
            draw_rects.left_button_down = False
            draw_rects.current_rect.br = draw_rects.shrink_point(x, y)
            print('pt2: x = %d, y = %d' % (draw_rects.current_rect.br[0],
                                           draw_rects.current_rect.br[1]))
            self.xy_afer_list.append([draw_rects.current_rect.br[0], draw_rects.current_rect.br[1]])
            draw_rects.current_rect.regularize()
            draw_rects.append()
        if (not draw_rects.left_button_down) and event == cv2.EVENT_RBUTTONDOWN:
            # pop the last rect in rects list
            draw_rects.pop()
            draw_rects.reset_image()
            draw_rects.draw()


def absdiff_demo(image_1, image_2, sThre, gas_kel_size=3):
    gray_image_1 = cv.cvtColor(image_1, cv.COLOR_BGR2GRAY)  # 灰度化
    gray_image_1 = cv.GaussianBlur(gray_image_1, (gas_kel_size, gas_kel_size), 0)  # 高斯滤波
    gray_image_2 = cv.cvtColor(image_2, cv.COLOR_BGR2GRAY)
    gray_image_2 = cv.GaussianBlur(gray_image_2, (gas_kel_size, gas_kel_size), 0)
    d_frame = cv.absdiff(gray_image_1, gray_image_2)
    ret, d_frame = cv.threshold(d_frame, sThre, 255, cv.THRESH_BINARY)
    return d_frame


def move_detec(capture, sThre, step=1, show=False, gas_kel_size=3,yolo_box = True):
    '''

    Args:
        capture: 输入视频流
        sThre: 二值化阈值（越低，检测越敏感）

    Returns:
        返回带有每一帧运动预测的数组

    '''
    frame_count = int(capture.get(cv.CAP_PROP_FRAME_COUNT))
    frame_height = capture.get(cv.CAP_PROP_FRAME_HEIGHT)
    frame_width = capture.get(cv.CAP_PROP_FRAME_WIDTH)
    fps = capture.get(5)  # 帧率
    print(
        '总帧数 {0}帧, 宽度 {1}  高度{2}  FPS {3} ，视频时长 {4} 秒'.format(frame_count, frame_width, frame_height, fps,
                                                                           np.round(frame_count / fps, 2)))
    detect_list = []  # return
    all_frame = []
    for f in range(frame_count + 1):
        ret, frame = capture.read()
        if ret == True:
            all_frame.append(frame)  # get ndarry frame
    roi_left_list = []
    roi_right_list = []
    if yolo_box:

        get_frame_img = all_frame[0]  #用第0帧来取框
        get_frame_img_path = './测试数据/get_frame_img.jpg'
        cv.imwrite(get_frame_img_path,get_frame_img)
        # yolo取框
        img,bbox = detect(img_path=get_frame_img_path)
        roi_num = int(bbox.shape[0])
        for b in bbox:
            roi_left_list.append([int(b[0]),int(b[1])])
            roi_right_list.append([int(b[2]),int(b[3])])

    else:
        '''
        用第1帧来确定roi区域
        '''
        image = all_frame[0]
        draw_rects = DrawRects(image, (0, 255, 0), 2)
        cv2.namedWindow(WIN_NAME, 0)
        cv2.setMouseCallback(WIN_NAME, draw_rects.onmouse_draw_rect, draw_rects)
        while True:
            cv2.imshow(WIN_NAME, draw_rects.image_for_show)
            key = cv2.waitKey(30)
            if key == 27:  # ESC
                break
        cv2.destroyAllWindows()
        assert len(draw_rects.xy_list) == len(draw_rects.xy_afer_list), '矩形宽出错！'
        roi_left_list = draw_rects.xy_list
        roi_right_list = draw_rects.xy_afer_list
        roi_num = len(draw_rects.xy_afer_list)

    t1 = time.time()
    for idx, f_img in enumerate(all_frame):
        frame_this = f_img

        roi_img_list = []
        for r in range(roi_num):
            if r == 0:
                origin_frame = frame_this
            frame_this = origin_frame[roi_left_list[r][1]:roi_right_list[r][1],
                         roi_left_list[r][0]:roi_right_list[r][0], :]

            if idx + step >= len(all_frame):
                break
            frame_next = all_frame[idx + step]
            frame_next = frame_next[roi_left_list[r][1]:roi_right_list[r][1], roi_left_list[r][0]:roi_right_list[r][0],
                         :]

            d_frame = absdiff_demo(frame_this, frame_next, sThre, gas_kel_size)

            roi_img_list.append([frame_next, d_frame])

        # 推理阶段
        if show:
            for roi_id, roi_img in enumerate(roi_img_list):
                frame_area = roi_img[1].size
                move_pxl_num = np.sum((roi_img[1] == 255))
                moving_ratio = np.round(move_pxl_num / frame_area, 4)  # 计算运动比例
                show_roi = copy.deepcopy(roi_img[0])
                cv.putText(show_roi, 'move_lambda'+str(moving_ratio), (5, 20), cv.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 1)

                if moving_ratio <= 0.001:

                    # 转灰度图为了检测黑屏
                    show_roi_gray = cv.cvtColor(show_roi, cv.COLOR_BGR2GRAY)
                    show_roi_gray = cv.GaussianBlur(show_roi_gray, (gas_kel_size, gas_kel_size), 0)  # 高斯滤波
                    _, show_roi_gray = cv.threshold(show_roi_gray, 60, 255, cv.THRESH_BINARY)
                    # cv.imshow(f'roi_gray{roi_id}',show_roi_gray)

                    #蓝屏检测
                    if (np.sum(show_roi[:,:,0] > 128) / frame_area) > 0.5 and (np.sum(show_roi[:,:,1:] < 128) / (frame_area * 2)) > 0.5:
                        cv.putText(show_roi, 'bule!!!!!', (5, 70), cv.FONT_HERSHEY_COMPLEX, 1,
                                   (255, 0, 0), 2)
                    # 黑屏检测
                    if np.round(np.sum(show_roi_gray == 0 ) / frame_area,4) > 0.5:
                        cv.putText(show_roi, 'black!!!!!', (5, 50), cv.FONT_HERSHEY_COMPLEX, 1,
                                   (0, 0, 0), 2)
                    # 静止检测
                    cv.putText(show_roi, 'static!' , (5, 30), cv.FONT_HERSHEY_COMPLEX, 1,
                               (0, 0, 255), 2)

                # cv.imshow(f'input_frame_{roi_id}', show_roi)
                origin_frame[roi_left_list[roi_id][1]:roi_right_list[roi_id][1],
                roi_left_list[roi_id][0]:roi_right_list[roi_id][0], :] = show_roi
            cv.imshow("origin_frame_detect",origin_frame)
            cv.waitKey(int((1 / fps) * 800))  # 按照FPS显示图片

    print('共计时间：', time.time() - t1)
    return detect_list


if __name__ == '__main__':
    
    # capture_video = cv.VideoCapture("/home/coolshen/Desktop/data/my_data/数据2/9屏16（静帧、黑屏）.mp4")

    capture_video = cv.VideoCapture("/home/coolshen/Desktop/data/my_data/数据2/9屏14（蓝屏）.mp4")

    sThre = 15  # sThre表示像素阈值

    detect_out = move_detec(capture_video, sThre, step=3, show=True, gas_kel_size=7 , yolo_box = True)