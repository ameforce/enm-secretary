from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QLineEdit, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt

# from selenium.webdriver.common.by import By

from screeninfo import get_monitors
from libs.b64decoder import b64decoder
from libs.imagesearch import imagesearch
from pynput import keyboard
from winreg import *
import pyautogui
import pyperclip
import win32gui
import random
import string
import time
import sys
import os


class DataManagement:
    def __init__(self):
        self.hkey_type = HKEY_CURRENT_USER
        self.path = r'SOFTWARE\ENMSoft\ENMSecretary'
        self.key_name = None
        self.ascii_check_range = 126
        self.rand_range = 128
        self.__data = ''
        self.DATA_SEPARATOR = "@Data Separator#"

    def encryption_data(self, resource: str = None):
        encrypted_resource = []
        resource = resource.split(self.DATA_SEPARATOR)

        running_count = 0
        for element in resource:
            for char in element:
                char = char + '@enm#'
                encrypted_char = []
                rand_num = random.randint(1, self.rand_range)
                for semi_char in char:
                    semi_char = chr(ord(semi_char) + rand_num)
                    encrypted_char.append(semi_char)
                encrypted_resource.append(''.join(encrypted_char))
            running_count += 1
            if running_count != len(resource):
                encrypted_resource.append(self.DATA_SEPARATOR)
        self.__data = ''.join(encrypted_resource)

    def decryption_data(self):
        decrypted_resource = []
        running_count = 0
        for resource in self.__data.split(self.DATA_SEPARATOR):
            new_resource = []
            for i in range(len(resource) // 6):
                split_data = []
                for j in range(6):
                    split_data.append(resource[i*6+j])
                new_resource.append(split_data)

            for raw_data in new_resource:
                max_range = self.rand_range
                raw_data_min_num = min(ord(raw_char) for raw_char in raw_data[0:6])
                if raw_data_min_num < self.rand_range:
                    max_range = raw_data_min_num
                for i in range(max_range):
                    decrypting_data = []
                    for raw_char in raw_data:
                        decrypting_data.append(chr(ord(raw_char) - i))
                    if ''.join(decrypting_data[1:6]) == '@enm#':
                        decrypted_resource.append(decrypting_data[0])
                        break
            running_count += 1
            if running_count != len(self.__data.split(self.DATA_SEPARATOR)):
                decrypted_resource.append(self.DATA_SEPARATOR)
        return ''.join(decrypted_resource)

    def read_data(self):
        reg_handle = ConnectRegistry(None, self.hkey_type)
        try:
            reg_key = OpenKey(reg_handle, self.path, 0, KEY_READ)
            value = QueryValueEx(reg_key, self.key_name)
            CloseKey(reg_key)
            self.__data = value[0]
            return True
        except WindowsError:
            return False

    def save_data(self):
        reg_handle = ConnectRegistry(None, self.hkey_type)
        CreateKey(self.hkey_type, self.path)
        reg_key = OpenKey(reg_handle, self.path, 0, KEY_WRITE)
        try:
            SetValueEx(reg_key, self.key_name, 0, REG_SZ, self.__data)
        except EnvironmentError:
            print('레지스트리 쓰기에 문제가 발생했습니다.')
        CloseKey(reg_key)
        return True


class AutomaticPayment:
    def __init__(self):
        self.payment_type_list = ['smilepay', 'naverpay', 'skpay', 'paycopay', 'coupangpay']
        self.dm = DataManagement()

        for payment_type in self.payment_type_list:
            self.dm.key_name = payment_type
            if not self.dm.read_data():
                self.initial_setting(payment_type)

    def initial_setting(self, payment_type: str):
        print(f'[{payment_type}]의 초기 설정이 되어 있지 않습니다.')
        while True:
            print(f'[{payment_type}]의 결제 비밀번호를 입력해주세요: ', end='')
            input_resource = input('')

            try:
                int(input_resource)
                break
            except ValueError:
                print('결제 비밀번호는 숫자만 입력할 수 있습니다.')

        self.dm.key_name = payment_type
        self.dm.encryption_data(input_resource)
        self.dm.save_data()

    def common_logic(self, payment_type: str):
        if payment_type == 'smilepay':
            window_text_list = ['G마켓 - 주문서', '옥션 - 주문서', 'G9 - 주문서']
        elif payment_type == 'naverpay':
            window_text_list = ['네이버페이']
        elif payment_type == 'skpay':
            window_text_list = ['주문/결제 - 11번가']
        elif payment_type == 'paycopay':
            window_text_list = ['PAYCO']
        elif payment_type == 'coupangpay':
            window_text_list = ['COLOR OF YOUR DAYS!']      # None Clearly
        else:
            window_text_list = ['']

        for window_text in window_text_list:
            compare_status, window_hwnd = compare_window_text(window_text, 0.1)
            if compare_status:
                fasten_window(window_hwnd)
                im = imagesearch.ImageSearch()
                self.dm.key_name = payment_type
                self.dm.read_data()
                password = list(self.dm.decryption_data())
                file_name = f'{payment_type}\\1080\\{password[0]}'      # 원래 1080 자리에 resolution이 들어감.
                im.image_search_windows(file_name, False, True)

                if im.get_detection_status():
                    for num in password[1:]:
                        file_name = f'{payment_type}\\1080\\{num}'
                        im.image_search_windows(file_name, True, True)
                    if im.get_detection_status():
                        while True:
                            if not compare_window_text(window_text)[0]:
                                break
                            else:
                                time.sleep(0.3)

    def auto_runner(self):
        for payment_type in self.payment_type_list:
            self.common_logic(payment_type)


class AutomaticCert:
    def __init__(self):
        self.user_name = None
        self.phone_num = None
        self.sleep_time = 50

    def initial_setting(self):
        while True:
            if self.user_name is None:
                empty_data_text = '사용자 이름'
            elif self.phone_num is None:
                empty_data_text = '사용자 휴대폰 번호'
            else:
                break
            print(f'[{empty_data_text}]의 초기 설정이 되어 있지 않습니다')
            print(f'[{empty_data_text}] 입력: ')
            input_resource = input('')

        self.write_password(payment_type, input_resource)


    def update_data(self, user_name: str = None, phone_num: str = None, sleep_time: int = 50):
        self.user_name = user_name
        self.phone_num = phone_num
        self.sleep_time = sleep_time



class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.command = None
        self.command_list = [
            'culture-charge',
            'automatic-payment',
            'kakao'
        ]
        self.init_ui()

    def init_ui(self):
        qle = QLineEdit(self)
        qle.move(60, 100)
        qle.editingFinished.connect(lambda: self.return_signal(qle))

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(qle)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(3)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowTitle('ENM Secretary - Command')
        self.setGeometry(100, 300, 200, 50)
        self.center()
        self.show()

    def return_signal(self, qle):
        self.command = qle.text()
        self.check_command()
        self.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def check_command(self):
        if self.command == 'culture-charge':
            cultureland_charger()


def cultureland_charger():

    return


def compare_window_text(detect_window_text: string, interval: float = 0.3):
    """
    :param detect_window_text:  Enter a title for the window you want to detect.
    :param interval:            Enter the amount of time to wait if window navigation fails.
    :return:                    Returns whether {detect_window_text} is included in the title of the currently active
                                window.
    :rtype:                     bool, int
    """

    foreground_window_text = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    window_hwnd = win32gui.FindWindow(None, foreground_window_text)

    if detect_window_text in foreground_window_text:
        print(f'window_hwnd: {window_hwnd}')
        return True, window_hwnd
    else:
        time.sleep(interval)
        return False, window_hwnd


def fasten_window(window_hwnd: int):
    window_rect = win32gui.GetWindowRect(window_hwnd)
    win32gui.MoveWindow(window_hwnd, 0, 0, window_rect[2] - window_rect[0], window_rect[3] - window_rect[1], True)


def mma_certificator():
    compare_result, window_hwnd = compare_window_text('여러분과 함께 하는 병무청 입니다', 0.1)

    authentication_hard_disk_activated_image_name = 'hard_disk_activated'
    authentication_popup_confirm_image_name = 'popup_confirm'
    name = '김종인'
    rrn = '9802101155710'
    authentication_password = '@dlsvp2tmxm'

    if compare_result:
        fasten_window(window_hwnd)

        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('enter')
        pyautogui.press('tab')

        pyperclip.copy(name)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('tab')

        pyautogui.write(rrn)
        pyautogui.press('tab')

        pyautogui.press('enter')

        im = imagesearch.ImageSearch()
        im.image_search_windows(authentication_hard_disk_activated_image_name, True, True)
        for i in range(3):
            pyautogui.press('tab')
        pyautogui.write(authentication_password)
        pyautogui.press('enter')

        im.image_search_windows(authentication_popup_confirm_image_name, True, True)
        time.sleep(0.3)
        pyautogui.leftClick(im.get_pos_center())

        while True:
            if not compare_window_text('여러분과 함께 하는 병무청 입니다')[0]:
                break
            else:
                time.sleep(0.3)
    return


def phone_certification(sleep_time, user_name, phone_num):
    while True:
        win_name = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if 'PASS' in win_name:
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('enter')
            time.sleep(sleep_time)

            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('enter')
            time.sleep(sleep_time)

            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('enter')
            time.sleep(sleep_time)

            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('space')
            time.sleep(sleep_time)

            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('enter')
            time.sleep(sleep_time)

            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyperclip.copy(user_name)
            time.sleep(sleep_time)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.write(phone_num)
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')

            while '3자' not in win32gui.GetWindowText(win32gui.GetForegroundWindow()):
                continue

            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('tab')
            time.sleep(sleep_time)
            pyautogui.hotkey('enter')
            time.sleep(sleep_time)
            break


def default_gui():
    app = QApplication(sys.argv)
    ex = MyApp()
    app.exec_()
    # sys.exit()


def on_release(key):
    global save_key

    if (save_key == keyboard.Key.cmd and key == keyboard.Key.space) or \
            (save_key == keyboard.Key.space and save_key == keyboard.Key.cmd):
        default_gui()
    else:
        save_key = key

    # print(f'release: {key}')


def main():
    listener = keyboard.Listener(on_release=on_release)
    listener.start()

    monitor_resolution = []

    for monitor in get_monitors():
        if monitor.height not in monitor_resolution:
            monitor_resolution.append(monitor.height)

    ap = AutomaticPayment()
    while True:
        ap.auto_runner()
        mma_certificator()
        # phone_certification()


save_key = ''


if __name__ == '__main__':
    main()
