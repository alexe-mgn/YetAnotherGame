if __name__ == '__main__':
    from main_loop import Main
    from level import Level

    main = Main()
from config import APP_NAME
from interface import *
from Game.Levels.Survival import Survival
from Game.Levels.Test import TestLevel


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

            def load_survival():
                self.main.load_gui(None)
                self.main.load_level(TestLevel())

            b_survival.on_click = load_survival

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


if __name__ == '__main__':
    level = Level(screen=main.rect, zoom_offset=main.zoom_offset)
    menu = MainMenu(main=main)
    level.gui = menu
    main.load_level(level)
    main.start()
