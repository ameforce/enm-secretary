from functools import partial
from PIL import ImageGrab
import pyautogui
import time


class ImageSearch:
    def __init__(self):
        self.pos_center = None
        self.detection_status = False

    def get_pos_center(self):
        return self.pos_center

    def get_detection_status(self):
        return self.detection_status

    def image_search_mac(self, image_name, loop_status=False, click_status=True, click_button='left', confidence=0.85):
        route = 'images/' + image_name + '.png'
        print(f'{image_name} detecting...')
        while True:
            ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
            pos = pyautogui.locateOnScreen(route, confidence=confidence, grayscale=True)
            print(f'pos: {pos}')
            if pos is not None:
                print(f'{image_name} detection successful.')
                self.detection_status = True
                pos_center = pyautogui.center(pos)
                self.pos_center = [pos_center[0] / 2, pos_center[1] / 2]
                if click_status:
                    if click_button == 'left':
                        pyautogui.leftClick(self.pos_center)
                    else:
                        pyautogui.rightClick(self.pos_center)
                break
            if not loop_status:
                break

    def image_search_windows(self, image_name: str, loop_status: bool = False, click_status: bool = True,
                             click_button: str = 'left', confidence: float = 0.95, interval: float = 0):
        self.__init__()
        route = 'images/' + image_name + '.png'
        print(f'{image_name} detecting...')
        while True:
            ImageGrab.grab = partial(ImageGrab.grab, all_screens=False)
            pos = pyautogui.locateOnScreen(route, confidence=confidence, grayscale=True)
            print(f'pos: {pos}')
            if pos is not None:
                print(f'{image_name} detection successful.')
                self.detection_status = True
                self.pos_center = pyautogui.center(pos)
                if click_status:
                    if click_button == 'left':
                        pyautogui.leftClick(self.pos_center)
                    else:
                        pyautogui.rightClick(self.pos_center)
                break
            time.sleep(interval)
            if not loop_status:
                break

    def image_search_twice(self, os_type, image_name01, image_name02, loop_status=False, click_status=True,
                           click_button='left', confidence=0.85):
        while True:
            if os_type == 'mac':
                self.image_search_mac(image_name01, False, click_status, click_button, confidence)
                if self.get_pos_center():
                    break
                else:
                    self.image_search_mac(image_name02, False, click_status, click_button, confidence)
                    if self.get_pos_center():
                        break
            elif os_type == 'windows':
                self.image_search_windows(image_name01, False, click_status, click_button, confidence)
                if self.get_pos_center():
                    break
                else:
                    self.image_search_windows(image_name02, False, click_status, click_button, confidence)
                    if self.get_pos_center():
                        break
            if not loop_status:
                break
