import pygame
from geometry import Vec2d, FRect
from loading import get_path, load_model


def draw_text(font_path, surface, text, rect, color=(255, 255, 255), alignment='center', size=None):
    if size is None:
        size = int(min((rect.height * .9, rect.width * .9 * 1.6 / len(text))))
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

        self.image = None
        self.elements = []
        self.disabled = []
        self.step_time = 1
        self.hover = False
        self.press = False

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

    def disable(self, obj):
        if obj in self.elements:
            obj.deactivate()
            self.elements.remove(obj)
            self.disabled.append(obj)

    def enable_all(self):
        for i in self.disabled:
            self.elements.append(i)
        self.disabled.clear()

    def deactivate(self):
        self.hover = False
        self.press = False
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

    def send_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover:
                self.button_down()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.button_up()
        for i in self.elements:
            i.send_event(event)

    def draw(self, surface):
        if self.image is not None:
            self.draw_image(surface)
        for i in self.elements:
            i.draw(surface)
        if self._draw_debug:
            self.draw_debug(surface)

    def draw_image(self, surface):
        surface.blit(pygame.transform.scale(self.image, self.abs_rect.size), self.abs_rect)

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
        return self.elements

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
        self.press = True

    def button_up(self):
        if self.hover and self.press:
            self.on_click()
        self.press = False

    def on_click(self):
        pass

    def on_focus(self):
        pass

    def on_unfocus(self):
        pass


class Menu(Division):
    pass


"""
class Table(Division):
    
    def __init__(self, cols=0, rows=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.t_size = (cols, rows)
        self.table = [[None] * cols for _ in range(rows)]
    
    @property
    def cols(self):
        return self.t_size[0]
    
    @property
    def rows(self):
        return self.t_size[1]
    
    def add(self, element, col=None, row=None):
        super().add(element)
    
    def __iter__(self):
        return self.table

    def __getitem__(self, ind):
        return self.table[ind]

    def __setitem__(self, ind, val):
        pass
"""


class Element(Division):
    font = pygame.font.match_font('times')
    image = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ''
        self.text_size = None
        self.text_color = pygame.Color('white')
        self.text_alignment = 'center'

    def draw(self, surface):
        super().draw(surface)
        if self.text:
            draw_text(self.font,
                      surface,
                      self.text,
                      self._abs_rect,
                      color=self.text_color,
                      alignment=self.text_alignment,
                      size=self.text_size)


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
        surface.blit(pygame.transform.scale(self.images[n], b_rect.pygame.size), b_rect.topleft)


class BtnLarge(Button):
    font = get_path('Res\\potra.ttf')
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
    font = get_path('Res\\potra.ttf')
    image = True
    images = (
        load_model('Res\\UI\\btn_small'),
        load_model('Res\\UI\\btn_small_click'),
        load_model('Res\\UI\\btn_small_hover')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_color = (255, 255, 255)

    def draw(self, surface):
        super().draw(surface)
