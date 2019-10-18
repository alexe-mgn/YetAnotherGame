from Game.GUI_Elements import *

from Engine.geometry import FRect
from Engine.config import *

import pygame

import json
import os

ABS_RECORDS_FILE = get_write_path(RECORDS_FILE)


def preload_records():
    directory = os.path.dirname(ABS_RECORDS_FILE)
    if not os.path.isdir(directory):
        os.mkdir(directory)
    if not os.path.isfile(ABS_RECORDS_FILE):
        with open(ABS_RECORDS_FILE, mode='w') as out:
            out.write(json.dumps({}))


class Title(TextField):
    font = FONT.potra

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rect.size = (90, 20)
        self.rect.center = (50, 12.5)
        self.text = APP_NAME


class InvSlot(Button):
    image = True
    images = (
        load_model('Res\\UI\\inv_slot'),
        load_model('Res\\UI\\inv_slot_selected'),
        load_model('Res\\UI\\inv_slot_hover')
    )
    content = None

    def get_state_image(self):
        return self.images[1 if self.select or self.press and self.hover else (2 if self.hover else 0)]

    def draw(self, surface):
        super().draw(surface)
        b_rect = self._abs_rect
        if self.content:
            ir = FRect(0, 0, b_rect.w * .8, b_rect.h * .8)
            ir.center = b_rect.center
            r = FRect(self.content.get_rect())
            r.fit_ip(ir)
            surface.blit(pygame.transform.scale(self.content, r.pygame.size), r.topleft)


class TutorialMenu(Menu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tutorial = Element(self)
        self.tutorial.image = load_model('Res\\Tutorial')
        self.tutorial.rect = (10, 10, 80, 80)

        self.back = BtnSmall(self)
        self.back.rect.size = (15, 8)
        self.back.rect.topleft = (5, 5)
        self.back.text = 'Back'
        self.back.on_click = lambda: self.parent.checkout_menu(self.parent.home)


class CreditsMenu(Menu):

    def __init__(self, parent):
        sx, sy = 40, 25

        class CText(TextField):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.rect.size = (sx, sy)
                self.text_alignment = 'left'

            def update(self):
                self.text_size = self.global_rect.size[0] / 15

        super().__init__(parent)
        self.title = Title(self)
        st_y = 20
        dy = 5
        c = CText(self)
        c.rect.topleft = (50 - sx, st_y)
        c.text = 'Author:'
        c = CText(self)
        c.rect.topleft = (50, st_y)
        c.text = 'github.com/alexe-mgn'

        c = CText(self)
        c.rect.topleft = (50 - sx, st_y + dy)
        c.text = 'Sprites, Models:'
        c = CText(self)
        c.rect.topleft = (50, st_y + dy)
        c.text = 'opengameart.org/users/skorpio'

        c = CText(self)
        c.rect.topleft = (50 - sx, st_y + dy * 2)
        c.text = 'UI:'
        c = CText(self)
        c.rect.topleft = (50, st_y + dy * 2)
        c.text = 'opengameart.org/users/kindland'

        c = CText(self)
        c.rect.topleft = (50 - sx, st_y + dy * 3)
        c.text = 'Sound:'

        c = CText(self)
        c.rect.topleft = (50, st_y + dy * 3)
        c.text = 'Michel Baradari'
        c = CText(self)
        c.rect.topleft = (50, st_y + dy * 4)
        c.text = 'Iwan Gabovitch'

        c = CText(self)
        c.rect.topleft = (50, st_y + dy * 5)
        c.text = 'Michael Kurinnoy'

        c = CText(self)
        c.rect.topleft = (50 - sx, st_y + dy * 6)
        c.text = '      (Published by)'
        c = CText(self)
        c.rect.topleft = (50, st_y + dy * 6)
        c.text = 'opengameart.org/users/qubodup'

        b = BtnLarge(self)
        b.rect.size = (35, 10)
        b.rect.center = (50, 90)
        b.text = 'Back'
        b.on_click = lambda: self.parent.checkout_menu(self.parent.home)


class LeadersMenu(Menu):
    class Placement(Element):

        def __init__(self, *args, n='..', **kwargs):
            super().__init__(*args, **kwargs)
            self.rect.size = (5, 6)
            self.rect.left = 25
            self.text_alignment = 'left'
            self.text = str(n).ljust(2, ' ')
            # self._draw_debug = True

    class Name(Element):

        def __init__(self, *args, name='........', **kwargs):
            super().__init__(*args, **kwargs)
            self.rect.size = (40, 6)
            self.rect.left = 30
            self.text_alignment = 'left'
            self.text = str(name)
            # self._draw_debug = True

    class Score(Element):

        def __init__(self, *args, score='........', **kwargs):
            super().__init__(*args, **kwargs)
            self.rect.size = (20, 6)
            self.rect.left = 70
            self.text_alignment = 'left'
            self.text = str(score)
            # self._draw_debug = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = TextField(self)
        self.title.rect.size = (90, 10)
        self.title.rect.center = (50, 10)
        self.title.text = 'Leaders'

        self.back = BtnSmall(self)
        self.back.rect.size = (15, 8)
        self.back.rect.topleft = (5, 5)
        self.back.text = 'Back'
        self.back.on_click = lambda: self.parent.checkout_menu(self.parent.home)

    def post_init(self):
        dy = 8
        preload_records()
        with open(ABS_RECORDS_FILE, mode='r') as data_file:
            data = sorted(json.loads(data_file.read()).items(), key=lambda e: e[1], reverse=True)
        ln = len(data)
        for n in range(10):
            pl = self.Placement(self, n=str(n + 1))
            if -1 < n < ln:
                name = self.Name(self, name=data[n][0])
                sc = self.Score(self, score=data[n][1])
            else:
                name = self.Name(self)
                sc = self.Score(self)
            for i in [pl, name, sc]:
                i.rect.centery = 20 + dy * n


class MainMenu(Menu):
    class HomeMenu(Menu):

        def __init__(self, parent):
            class CBtn(BtnSmall):

                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.rect.size = (29, 9)

                def update(self):
                    self.text_size = self.global_rect.size[0] / 8

            class DisCBtn(Disabled, CBtn):
                pass

            super().__init__(parent)
            self.title = Title(self)
            dy = 10
            st_y = 35

            b_tutorial = CBtn(self)
            self.b_tutorial = b_tutorial
            b_tutorial.rect.center = (50, st_y)
            b_tutorial.text = 'Tutorial'
            b_tutorial.on_click = lambda: self.parent.checkout_menu(self.parent.tutorial)

            b_survival = CBtn(self)
            self.b_survival = b_survival
            b_survival.rect.center = (50, st_y + dy)
            b_survival.text = 'Survival Mode'
            b_survival.on_click = self.main.load_survival

            b_options = DisCBtn(self)
            self.b_options = b_options
            b_options.rect.center = (50, st_y + dy * 2)
            b_options.text = 'Options'

            b_leaders = CBtn(self)
            self.b_leaders = b_leaders
            b_leaders.rect.center = (50, st_y + dy * 3)
            b_leaders.text = 'Leaderboards'
            b_leaders.on_click = lambda: self.parent.checkout_menu(self.parent.leaderboards)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.home = self.HomeMenu(self)
        self.tutorial = TutorialMenu(self)
        self.credits = CreditsMenu(self)
        self.leaderboards = LeadersMenu(self)
        self.checkout(self.home)


class LevelGUI(Menu):
    class HomeMenu(Menu):

        def __init__(self, parent):
            class CBtn(BtnSmall):

                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.rect.size = (29, 9)

                def update(self):
                    self.text_size = self.global_rect.size[0] / 8

            class DisCBtn(Disabled, CBtn):
                pass

            super().__init__(parent)
            self.title = Title(self)
            dy = 10
            st_y = 35

            b_cont = CBtn(self)
            self.b_continue = b_cont
            b_cont.rect.center = (50, st_y)
            b_cont.text = 'Continue'
            b_cont.on_click = lambda: self.parent.unpause()

            b_tutorial = CBtn(self)
            self.b_tutorial = b_tutorial
            b_tutorial.rect.center = (50, st_y + dy)
            b_tutorial.text = 'Tutorial'
            b_tutorial.on_click = lambda: self.parent.checkout_menu(self.parent.tutorial)

            b_options = DisCBtn(self)
            self.b_options = b_options
            b_options.rect.center = (50, st_y + dy * 2)
            b_options.text = 'Options'

            b_leaders = CBtn(self)
            self.b_leaders = b_leaders
            b_leaders.rect.center = (50, st_y + dy * 3)
            b_leaders.text = 'Leaderboards'
            b_leaders.on_click = lambda: self.parent.checkout_menu(self.parent.leaderboards)

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

        class InventoryUI(Menu):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._inventory = []
                self.slots = []
                # mr = self.main.rect.size
                # self.rect.size = (8 * 0, 8 * mr[0] / mr[1])

            @property
            def inventory(self):
                return self._inventory

            @inventory.setter
            def inventory(self, inv):
                self._inventory = inv
                self.slots.clear()
                ln = len(inv)
                s_ind = inv.index
                for n, i in enumerate(inv):
                    s = InvSlot(self)
                    s.rect.size = (100 / ln, 100)
                    s.rect.left = (100 / ln * n)
                    s.rect.top = 0
                    ws = inv[n]
                    if ws:
                        s.content = ws[0].preview(s.calculate_global_rect().size)
                    s.on_select = lambda w_inv=inv, ind=n: w_inv.checkout(ind)
                    s.select_off = lambda: None
                    self.slots.append(s)
                self[s_ind].select_on()
                # mr = self.main.rect.size
                # self.rect.size = (8 * len(inv), 8 * mr[0] / mr[1])

            def recalculate_icons(self):
                for w, s in zip(self.inventory, self.slots):
                    if w:
                        s.content = w[0].preview(s.calculate_global_rect().size)
                    else:
                        s.content = None

        class PlayerHPBar(StyledProgressBar):
            progress = load_model('Res\\UI\\progress_fill_red')

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.player = None

            def on_draw(self):
                self.percentage = self.player.health / self.player.max_health * 100 if self.player else 0

            @property
            def player(self):
                return self._player

            @player.setter
            def player(self, player):
                self._player = player

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            sl = TextField(self)
            self.score_label = sl
            sl.rect.size = (20, 8)
            sl.rect.topright = (98, 2)
            sl.text_alignment = 'right'

            inv = self.InventoryUI(self)
            self.inventory = inv
            mr = self.main.get_visible_rect().size
            inv.rect.size = (40, 8 * mr[0] / mr[1])
            inv.rect.centerx = 50
            inv.rect.bottom = 100

            hp = self.PlayerHPBar(self)
            self.hp = hp
            hp.rect.size = (35, 4)
            hp.rect.topleft = (2, 2)

        def on_draw(self):
            self.score_label.text = str(self.main.level.score)

        def post_handle(self, event):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.parent.pause()
                    event.ignore = True
                elif 49 <= event.key <= 53:
                    kc = event.key - 49
                    self.inventory[kc].select_on()

        @property
        def player(self):
            return self._player

        @player.setter
        def player(self, player):
            self._player = player
            self.inventory.inventory = player.w_inv
            self.hp.player = player

    class RecordMenu(Menu):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title = TextField(self)
            self.title.rect.size = (90, 20)
            self.title.rect.center = (50, 12.5)
            self.title.text = 'Game Over'
            self.title.font = BtnSmall.font

            h = Element(self)
            self.hint = h
            h.rect.size = (40, 10)
            h.rect.center = (50, 51)
            h.text = 'Enter your name'

            inp = StyledInputBox(self)
            self.input = inp
            inp.rect.size = (50, 10)
            inp.rect.center = (50, 60)

            ac = BtnSmall(self)
            self.accept = ac
            ac.rect.size = (20, 8)
            ac.rect.center = (50, 75)
            ac.text = 'Accept'
            ac.on_click = self.write_record

        def post_handle(self, event):
            event.ignore = True

        def write_record(self):
            preload_records()
            with open(ABS_RECORDS_FILE, mode='r') as data_file:
                d = data_file.read()
                data = json.loads(d)
            name = self.input.text
            score = self.main.level.score
            if name in data.keys():
                if score > data[name]:
                    data[name] = score
            else:
                data[name] = score
            with open(ABS_RECORDS_FILE, mode='w') as data_file:
                data_file.write(json.dumps(data))
            self.main.home()

    def pause(self):
        self.main.level.pause()
        self.checkout_menu(self.home)

    def unpause(self):
        self.main.level.unpause()
        self.checkout_menu(self.ingame)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.home = self.HomeMenu(self)
        self.tutorial = TutorialMenu(self)
        self.ingame = self.IngameMenu(self)
        self.record = self.RecordMenu(self)
        self.leaderboards = LeadersMenu(self)
        self.checkout_menu(self.ingame)
