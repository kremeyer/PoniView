import os

IMAGE_FORMATS = ('.npy', '.tif', '.tiff', '.bmp', '.eps', '.gif', '.jpeg', '.jpg', '.png')
APP_ID = 'PoniView'


def get_data_path():
    return os.path.dirname(__file__)
