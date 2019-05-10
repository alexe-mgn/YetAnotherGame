import pygame
from geometry import Vec2d, FRect
from loading import get_path, load_model
from config import *


class FONT:
    default = pygame.font.match_font('times')
    potra = get_path('Res\\potra.ttf')


def fit_text(size, ln):
    return int(min((size[1] * .8, size[0] * .9 * 1.6 / ln)))


def draw_text(font_path, surface, text, rect, color=(255, 255, 255), alignment='center', size=None):
    if size is None:
        size = fit_text(rect.size, len(text))
    else:
        size = int(size)
    font = pygame.font.Font(font_path,
                            size)
    text = font.render(text, 1, color)
    t_rect = text.get_rect()
    t_rect.centery = rect.centery
    if alignment == 'left':
        t_rect.left = rect.left
    elif alignment == 'right':
        t_rect.right = rect.right
    else:
        t_rect.centerx = rect.centerx
    surface.blit(text, t_rect)


class Division:
    _draw_debug = False
    image = None

    def __init__(self, parent=None, main=None):
        self._parent = parent
        self._main = main
        if main is None and parent is not None:
            self._main = parent.main

        if main is not None or parent is not None:
            if parent is not None:
                parent.add(self)
            self._rect = FRect(0, 0, 100, 100)
            self.absolute = False
        else:
            self._rect = FRect(0, 0, 0, 0)
            self.absolute = True
        self._abs_rect = self.global_rect()

        self.in_step = False

        self.elements = []
        self.disabled = []
        self.step_time = 1
        self.event = None
        self.hover = False
        self.press = False
        self.select = False
        self.selected = None
        self.post_init()

    def post_init(self):
        pass

    @property
    def main(self):
        return self._main

    @main.setter
    def main(self, new):
        self._main = new
        for i in self.elements:
            i.main = new
        for i in self.disabled:
            i.main = new

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new):
        if self._parent is not None:
            self._parent.remove(self)
        self._parent = new
        if new is not None:
            self._main = new.main
            new.add(self)

    def global_parent(self):
        if self._parent is not None:
            return self._parent
        else:
            return self

    def global_rect(self):
        if self._parent is not None:
            rect = self._parent.abs_rect
        elif self._main is not None:
            rect = self._main.rect
        else:
            return FRect(self._rect)
        if self.absolute:
            return FRect(*map(sum, zip(rect.topleft, self._rect.topleft)), *self._rect.size)
        else:
            s_rect = self._rect
            s_tl = Vec2d(s_rect.topleft)
            s_sz = Vec2d(s_rect.size)
            return FRect(*(s_tl / 100 * rect.size + rect.topleft), *(s_sz / 100 * rect.size))

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, rect):
        self._rect = FRect(rect)
        if self.in_step:
            self._abs_rect = self.global_rect()

    @property
    def local_rect(self):
        return FRect(0, 0, *self.rect.size)

    @property
    def abs_rect(self):
        return self._abs_rect

    def add(self, element):
        if element not in self.elements:
            self.elements.append(element)

    def remove(self, obj):
        if obj in self.elements:
            obj.deactivate()
            self.elements.remove(obj)

    def enable(self, obj):
        if obj in self.disabled:
            self.disabled.remove(obj)
            self.elements.append(obj)
            obj.activate()

    def disable(self, obj):
        if obj in self.elements:
            obj.deactivate()
            self.elements.remove(obj)
            self.disabled.append(obj)

    def enable_all(self):
        for i in self.disabled:
            self.elements.append(i)
            i.activate()
        self.disabled.clear()

    def activate(self):
        self.post_init()
        if not self.in_step:
            self.start_step(self.step_time)
        for i in self.elements:
            i.activate()

    def deactivate(self):
        self.hover = False
        self.press = False
        self.select = False
        for i in self.elements:
            i.deactivate()

    def checkout(self, obj):
        active = obj in self.elements
        disabled = obj in self.disabled
        if active or disabled:
            for i in self.elements:
                if i is not obj:
                    i.deactivate()
                    self.disabled.append(i)
            if disabled:
                self.disabled.remove(obj)
            self.elements.clear()
            self.elements.append(obj)
            obj.activate()

    def checkout_menu(self, obj):
        active = obj in self.elements
        disabled = obj in self.disabled
        if active or disabled:
            mfd = []
            for i in self.elements:
                if i is not obj and isinstance(i, Menu):
                    i.deactivate()
                    mfd.append(i)
                    self.disabled.append(i)
            for i in mfd:
                self.elements.remove(i)
            if disabled:
                self.disabled.remove(obj)
                self.elements.append(obj)
                obj.activate()

    def collidepoint(self, pos):
        return self._abs_rect.collidepoint(*pos)

    def get_point_hits(self, pos):
        hits = []
        if self.hover:
            for i in self.elements:
                if i.collidepoint(pos):
                    hits.append(i)
        return hits

    def start_step(self, upd_time):
        self.in_step = True
        ms = pygame.mouse.get_pos()
        self.step_time = upd_time
        self._abs_rect = self.global_rect()
        if self.collidepoint(ms):
            self.mouse_on()
        else:
            self.mouse_off()
        for i in self.elements:
            i.start_step(upd_time)

    def update(self):
        for i in self.elements:
            i.update()

    def end_step(self):
        for i in self.elements:
            i.end_step()
        self.in_step = False

    def send_event(self, event):
        self.event = event
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.hover:
                    self.button_down()
                elif self.select and (not self._parent or (self._parent and self._parent.hover)):
                    self.select_off()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.button_up()
                if self.press:
                    self.on_event_hit(event)
        if self.hover:
            self.on_event_hit(event)
        for i in self.elements:
            i.send_event(event)
        self.post_handle(event)

    def post_handle(self, event):
        pass

    def on_event_hit(self, event):
        pass

    def draw(self, surface):
        self.on_draw()
        if self.image is not None:
            self.draw_image(surface)
        for i in self.elements:
            i.draw(surface)
        if self._draw_debug:
            self.draw_debug(surface)

    def draw_image(self, surface):
        r = self.abs_rect.pygame
        surface.blit(pygame.transform.scale(self.image, r.size), r.topleft)

    def draw_debug(self, surface):
        if self.press:
            pygame.draw.rect(surface, (0, 255, 0), self._abs_rect.pygame, 1)
        elif self.hover:
            pygame.draw.rect(surface, (255, 255, 0), self._abs_rect.pygame, 1)
        else:
            pygame.draw.rect(surface, (255, 0, 0), self._abs_rect.pygame, 1)

    def __len__(self):
        return len(self.elements)

    def __iter__(self):
        return iter(self.elements)

    def __getitem__(self, ind):
        return self.elements[ind]

    def __setitem__(self, ind, val):
        self.elements[ind] = val

    def __delitem__(self, ind):
        del self.elements[ind]

    def mouse_on(self):
        if not self.hover:
            self.on_focus()
        self.hover = True

    def mouse_off(self):
        if self.hover:
            self.on_unfocus()
        self.hover = False

    def button_down(self):
        # hovered and pressed
        self.press = True
        self.on_hold()

    def button_up(self):
        # button unhold - any case
        if self.press:
            self.on_unhold()
            if self.hover:
                self.on_click()
                if not self.select:
                    self.select_on()
        self.press = False

    def set_selected(self, obj):
        if self.selected is not None:
            self.selected.select = False
            self.selected.on_unselect()
        self.selected = obj

    def select_on(self):
        if self._parent:
            self._parent.set_selected(self)
        self.select = True
        self.on_select()

    def select_off(self):
        self.select = False
        if self._parent:
            self._parent.set_selected(None)
        self.on_unselect()

    def on_select(self):
        pass

    def on_unselect(self):
        pass

    def on_click(self):
        pass

    def on_hold(self):
        pass

    def on_unhold(self):
        pass

    def on_focus(self):
        pass

    def on_unfocus(self):
        pass

    def on_draw(self):
        pass


class Menu(Division):
    pass


class Element(Division):
    font = FONT.default
    image = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ''
        self.text_size = None
        self.text_color = pygame.Color('white')
        self.text_alignment = 'center'

    def draw(self, surface):
        super().draw(surface)
        self.draw_text(surface)

    def draw_text(self, surface):
        if self.text:
            draw_text(self.font,
                      surface,
                      self.text,
                      self._abs_rect,
                      color=self.text_color,
                      alignment=self.text_alignment,
                      size=self.text_size)


class Disabled(Element):

    def draw(self, surface):
        super().draw(surface)
        b_rect = self._abs_rect
        pygame.draw.line(surface, (255, 0, 0), b_rect.topleft, b_rect.bottomright, 2)
        pygame.draw.line(surface, (255, 0, 0), b_rect.topright, b_rect.bottomleft, 2)


class TextField(Element):
    font = get_path('Res\\potra.ttf')


class Button(Element):
    image = None
    images = (
        None, None, None
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = None
        del self.image

    def draw_image(self, surface):
        b_rect = self._abs_rect
        if self.press:
            n = 1
        elif self.hover:
            n = 2
        else:
            n = 0
        if self.images[n]:
            surface.blit(pygame.transform.scale(self.images[n], b_rect.pygame.size), b_rect.topleft)

    def on_event_hit(self, event):
        if (self.press or self.hover) and event.type in MOUSE_EVENTS:
            event.ignore = True


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


class InputBox(Element):
    image = True
    images = (
        load_model('Res\\UI\\input_normal'),
        load_model('Res\\UI\\input_select')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = None
        del self.image
        self.text = u''
        self.text_color = (255, 255, 255)
        self.select = False
        self.timer = 0
        self.display_carret = False

    def start_step(self, upd_time):
        super().start_step(upd_time)
        if self.select:
            self.timer += upd_time
            if self.timer >= 1000:
                self.display_carret = not self.display_carret
                self.timer = 0

    def draw_image(self, surface):
        b_rect = self._abs_rect
        if self.select:
            n = 1
        else:
            n = 0
        surface.blit(pygame.transform.scale(self.images[n], b_rect.pygame.size), b_rect.topleft)

    def draw_text(self, surface):
        if self.text or self.display_carret:
            draw_text(self.font,
                      surface,
                      self.text + ('|' if self.display_carret else ''),
                      self._abs_rect,
                      color=self.text_color,
                      alignment=self.text_alignment,
                      size=self.text_size)

    def on_click(self):
        self.select = True
        self.display_carret = True
        self.timer = 0

    def on_event_hit(self, event):
        if event in MOUSE_EVENTS:
            event.ignore = True

    def deactivate(self):
        self.select = False
        self.display_carret = False
        self.timer = 0
        super().deactivate()

    def on_select(self):
        self.display_carret = True

    def on_unselect(self):
        self.display_carret = False
        self.timer = 0

    def on_input_completion(self):
        pass

    def send_event(self, event):
        super().send_event(event)
        if self.select and event.type in CONTROL_EVENTS:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if len(self.text) > 0:
                        self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.select_off()
                    self.on_input_completion()
                elif len(self.text) < 50:
                    self.text += event.unicode
            event.ignore = True


class ProgressBar(Element):
    image = load_model('Res\\UI\\progress_overlay')
    progress = load_model('Res\\UI\\progress_fill_blue')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.percentage = 100

    def draw(self, surface):
        super().draw(surface)
        self.image = None
        del self.image
        b_rect = self._abs_rect
        size = b_rect.pygame.size
        scaled = pygame.transform.scale(self.progress, size)
        surface.blit(scaled.subsurface((0, 0, int(size[0] * self.percentage / 100), size[1])), b_rect.topleft)
