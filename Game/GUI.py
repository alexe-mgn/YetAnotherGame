import pygame
from config import APP_NAME
from interface import *


class MainMenu(Menu):
    class HomeMenu(Menu):

        def __init__(self, parent):
            class CBtn(BtnSmall):

                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.rect.size = (29, 9)

                def update(self):
                    self.text_size = self.abs_rect.size[0] / 8

            super().__init__(parent)
            dy = 10
            st_y = 35

            b_start = CBtn(self)
            self.b_start = b_start
            b_start.rect.center = (50, st_y)
            b_start.text = ''

            b_survival = CBtn(self)
            self.b_survival = b_survival
            b_survival.rect.center = (50, st_y + dy)
            b_survival.text = 'Survival Mode'

            b_survival.on_click = self.main.load_survival

            b_options = CBtn(self)
            self.b_options = b_options
            b_options.rect.center = (50, st_y + dy * 2)
            b_options.text = 'Options'

            b_leaders = CBtn(self)
            self.b_leaders = b_leaders
            b_leaders.rect.center = (50, st_y + dy * 3)
            b_leaders.text = 'Leaderboards'

            b_creds = CBtn(self)
            self.b_credits = b_creds
            b_creds.rect.center = (50, st_y + dy * 4)
            b_creds.text = 'Credits'
            b_creds.on_click = lambda: self.parent.checkout_menu(self.parent.credits)

            b_exit = CBtn(self)
            self.b_exit = b_exit
            b_exit.rect.center = (50, st_y + dy * 5)
            b_exit.text = 'Quit'
            b_exit.on_click = self.main.quit

    class CreditsMenu(Menu):

        def __init__(self, parent):
            sx, sy = 40, 25

            class CText(TextField):

                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.rect.size = (sx, sy)
                    self.text_alignment = 'left'

                def update(self):
                    self.text_size = self.abs_rect.size[0] / 15

            super().__init__(parent)
            st_y = 20
            dy = 2
            c = CText(self)
            c.rect.topleft = (50 - sx, st_y)
            c.text = 'Author:'
            c = CText(self)
            c.rect.topleft = (50, st_y)
            c.text = 'github.com/alexe-mgn'

            c = CText(self)
            c.rect.topleft = (50 - sx, st_y + sy + dy)
            c.text = 'Sprites, Models:'
            c = CText(self)
            c.rect.topleft = (50, st_y + sy + dy)
            c.text = 'opengameart.org/users/skorpio'

            b = BtnLarge(self)
            b.rect.size = (35, 10)
            b.rect.center = (50, 90)
            b.text = 'Back'
            b.on_click = lambda: self.parent.checkout_menu(self.parent.home)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = Element(self)
        self.title.rect.size = (90, 20)
        self.title.rect.center = (50, 12.5)
        self.title.text = APP_NAME
        self.title.font = BtnSmall.font
        self.home = self.HomeMenu(self)
        self.credits = self.CreditsMenu(self)
        self.checkout_menu(self.home)


class LevelGUI(Menu):
    class HomeMenu(Menu):

        def __init__(self, parent):
            class CBtn(BtnSmall):

                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.rect.size = (29, 9)

                def update(self):
                    self.text_size = self.abs_rect.size[0] / 8

            super().__init__(parent)
            self.title = Element(self)
            self.title.rect.size = (90, 20)
            self.title.rect.center = (50, 12.5)
            self.title.text = APP_NAME
            self.title.font = BtnSmall.font
            dy = 10
            st_y = 35

            b_start = CBtn(self)
            self.b_start = b_start
            b_start.rect.center = (50, st_y)
            b_start.text = ''

            b_options = CBtn(self)
            self.b_options = b_options
            b_options.rect.center = (50, st_y + dy * 2)
            b_options.text = 'Options'

            b_leaders = CBtn(self)
            self.b_leaders = b_leaders
            b_leaders.rect.center = (50, st_y + dy * 3)
            b_leaders.text = 'Leaderboards'

            b_home = CBtn(self)
            self.b_home = b_home
            b_home.rect.center = (50, st_y + dy * 4)
            b_home.text = 'Main Menu'
            b_home.on_click = self.main.home

            b_exit = CBtn(self)
            self.b_exit = b_exit
            b_exit.rect.center = (50, st_y + dy * 5)
            b_exit.text = 'Quit'
            b_exit.on_click = self.main.quit

        def post_handle(self, event):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.parent.unpause()
                event.ignore = True

    class IngameMenu(Menu):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def post_handle(self, event):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.parent.pause()
                event.ignore = True

    def pause(self):
        self.main.level.pause()
        self.checkout_menu(self.home)

    def unpause(self):
        self.main.level.unpause()
        self.checkout_menu(self.ingame)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.home = self.HomeMenu(self)
        self.ingame = self.IngameMenu(self)
        self.checkout_menu(self.ingame)
