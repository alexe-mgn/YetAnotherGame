from Engine.interface import *
from Engine.loading import load_model
from Engine.config import *


class TextField(Element):
    """
    Element с другим шрифтом
    """
    font = get_path('Res\\potra.ttf')


class BtnLarge(Button):
    font = FONT.potra
    image = True
    images = (
        load_model('Res\\UI\\btn_large'),
        load_model('Res\\UI\\btn_large_click'),
        load_model('Res\\UI\\btn_large_hover')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_color = (255, 255, 255)


class BtnSmall(Button):
    font = FONT.potra
    image = True
    images = (
        load_model('Res\\UI\\btn_small'),
        load_model('Res\\UI\\btn_small_click'),
        load_model('Res\\UI\\btn_small_hover')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_color = (255, 255, 255)


class StyledInputBox(InputBox):
    """
    Текстовое поле ввода.
    В self.images - 2 изображения для нормального и выделенного состояния.
    """
    images = (
        load_model('Res\\UI\\input_normal'),
        load_model('Res\\UI\\input_select')
    )


class StyledProgressBar(ProgressBar):
    """
    "Полоса прогрузки" как это иногда называют.
    image, progress хранят изображения фона и заполнителя.
    """
    image = load_model('Res\\UI\\progress_overlay')
    progress = load_model('Res\\UI\\progress_fill_blue')
