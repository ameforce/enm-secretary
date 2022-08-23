import pyautogui
from libs import imagesearch


def main():
    im = imagesearch.ImageSearch()
    im.image_search_windows('smilepay\\1080\\1', True, False)
    pyautogui.move(im.get_pos_center())
    print(f'Current Mouse Position: {pyautogui.position()}')


if __name__ == '__main__':
    main()