import cv2
import numpy as np
import win32gui
import win32ui
import win32con
from ctypes import windll
from PIL import Image

class WindowCapture:
    def __init__(self, window_name):
        self.window_name = window_name
        self.hwnd = self.find_window(window_name)

    def capture(self):
        hwnd = self.hwnd
        left, top, right, bot = win32gui.GetWindowRect(hwnd)
        w = right - left
        h = bot - top

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

        saveDC.SelectObject(saveBitMap)

        windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)

        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        return np.array(im)

    def find_window(self, window_name):
        hwnd = win32gui.FindWindow(None, window_name)
        if hwnd == 0:
            raise ValueError("Window '{}' not found.".format(window_name))
        return hwnd

    def capture_area(self, x, y, width, height):
        full_image = self.capture()
        return full_image[y:y + height, x:x + width]

    def preprocess_image(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (1, 1), 0)
        _, binary = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        return morph
