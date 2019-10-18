from Engine.config import MOUSE_EVENTS, CONTROL_EVENTS
from Engine.geometry import Vec2d, FRect
from Engine.loading import get_path

import pygame


class FONT:
    default = pygame.font.match_font('times')
    potra = get_path('Res\\potra.ttf')


def fit_text(size, ln):
    """
    Рассчитать необходимый размер шрифта, чтобы текст влез.
    :param size: (x, y)
    :param ln: int - длина строки
    :return:
    """
    return int(min((size[1] * .8, size[0] * .9 * 1.6 / ln)))


def draw_text(font_path, surface, text, rect, color=(255, 255, 255), alignment='center', size=None):
    """
    Отрисовка текста на surface
    :param font_path:
    :param surface:
    :param text:
    :param rect: Прямоугольник с текстом относительно surface
    :param color: (r, g, b)
    :param alignment: 'left' | 'center' | 'right' - Выравнивание по заданному прямоугольнику
    :param size: int - размер шрифта
    :return:
    """
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
    """
    Базовый элемент интерфейса. Обычно используются только его дочерние классы.
    Правила:
    1 - Каждый элемент может иметь несколько дочерних.
    2 - Дочерние элементы могут быть включёнными или выключенными.
    3 - Для каждого элемента может существовать 1 "выбранный" self.selected)
    4 - Элемент может иметь или не иметь родительский класс и Main.
    5 - Позиция и размеры элемента определяются прямоугольником (self.rect)
    6 - self.absolute_position определяет являются ли значения прямоугольника
        False - процентами от размера родительского элемента.
        True - сдвигом от topleft родителя и размером в пикселях.
    """
    _draw_debug = False
    image = None

    def __init__(self, parent=None, main=None):
        """
        :param parent: родительский элемент class Division
        :param main: Main приложения (default=None (<=> parent.main))
        """
        self._parent = parent
        self._main = main
        if main is None and parent is not None:
            self._main = parent.main

        if main is not None or parent is not None:
            if parent is not None:
                parent.add_child(self)
            self._rect = FRect(0, 0, 100, 100)
            self.absolute_position = False
        else:
            self._rect = FRect(0, 0, 0, 0)
            self.absolute_position = True
        self._abs_rect = self.calculate_global_rect()

        self.in_step = False

        self._elements = []
        self._disabled = []
        self.step_time = 1
        self.event = None
        self.hover = False
        self.press = False
        self.select = False
        self.selected = None
        self.post_init()

    def post_init(self):
        """
        Переопределяемый.
        Вызывается сразу после инициализации или активации (activate)
        """
        pass

    def get_main(self):
        """
        :return: class Main
        """
        return self._main

    def set_main(self, new):
        """
        Переопределяет Main для себя и всех дочерних элементов.
        :param new: class Main
        """
        if new is not self._main:
            self._main = new
            for i in self._elements:
                i.main = new
            for i in self._disabled:
                i.main = new

    main = property(get_main, set_main)

    def get_parent(self):
        """
        Родительский элемент.
        :return: class Division
        """
        return self._parent

    def set_parent(self, new):
        """
        Изменяет родительский элемент
        :param new: class Division
        """
        if new is not self._parent:
            if self._parent is not None:
                self._parent.remove_child(self)
            self._parent = new
            if new is not None:
                if self._main != new.main:
                    self._main = new.main
                new.add_child(self)

    parent = property(get_parent, set_parent)

    # def global_parent(self):
    #     if self._parent is not None:
    #         return self._parent
    #     else:
    #         return self

    def calculate_global_rect(self):
        """
        Абсолютная позиция (прямоугольник) относительно области отрисовки.
        Рекомендуется вызывать только в Division.start_step, используйте get_global_rect
        :return: Rect()
        """
        if self._parent is not None:
            rect = self._parent.global_rect
        elif self._main is not None:
            rect = self._main.get_visible_rect()
        else:
            return FRect(self._rect)
        if self.absolute_position:
            return FRect(*map(sum, zip(rect.topleft, self._rect.topleft)), *self._rect.size)
        else:
            s_rect = self._rect
            s_tl = Vec2d(s_rect.topleft)
            s_sz = Vec2d(s_rect.size)
            return FRect(*(s_tl / 100 * rect.size + rect.topleft), *(s_sz / 100 * rect.size))

    def get_rect(self):
        """
        Прямоугольник расположения элемента.
        :return: Rect()
        """
        return self._rect

    def set_rect(self, rect):
        """
        Изменить прямоугольник расположения.
        :param rect: Rect()
        """
        self._rect = FRect(rect)
        if self.in_step:
            self._abs_rect = self.calculate_global_rect()

    rect = property(get_rect, set_rect)

    # @property
    # def local_rect(self):
    #     return FRect(0, 0, *self.rect.size)

    def get_global_rect(self):
        """
        Абсолютная позиция (прямоугольник) относительно области отрисовки.
        :return: Rect()
        """
        return self._abs_rect

    global_rect = property(get_global_rect)

    def add_child(self, element):
        if element not in self._elements:
            self._elements.append(element)

    def remove_child(self, obj):
        if obj in self._elements:
            obj.deactivate()
            self._elements.remove(obj)

    def enable_child(self, obj):
        if obj in self._disabled:
            self._disabled.remove(obj)
            self._elements.append(obj)
            obj.activate()

    def disable_child(self, obj):
        if obj in self._elements:
            obj.deactivate()
            self._elements.remove(obj)
            self._disabled.append(obj)

    def enable_all_children(self):
        """
        Включить все дочерние элементы
        """
        for i in self._disabled:
            self._elements.append(i)
            i.activate()
        self._disabled.clear()

    def activate(self):
        """
        "Активировать" элемент. По-сути функция не для конечного программиста, он использует post_init.
        Распространяет активацию на дочерние элементы,
        просто даёт элементу понять что его только что начали использовать.
        """
        self.post_init()
        if not self.in_step:
            self.start_step(self.step_time)
        for i in self._elements:
            i.activate()

    def deactivate(self):
        """
        "Деактивировать" элемент. По-сути функция не для конечного программиста.
        Распространяет деактивацию на дочерние элементы,
        просто даёт элементу понять что его только что перестали использовать.
        :return:
        """
        self.hover = False
        self.press = False
        self.select = False
        for i in self._elements:
            i.deactivate()

    def checkout(self, obj):
        """
        Переключает на отображение конкретного дочерного элемента, все остальные отключаются.
        :param obj: class Division
        """
        active = obj in self._elements
        disabled = obj in self._disabled
        if active or disabled:
            for i in self._elements:
                if i is not obj:
                    i.deactivate()
                    self._disabled.append(i)
            if disabled:
                self._disabled.remove(obj)
            self._elements.clear()
            self._elements.append(obj)
            obj.activate()

    def checkout_menu(self, obj):
        """
        Переключает на отображение конкретного дочерного меню, все остальные отключаются.
        :param obj: class Division
        """
        active = obj in self._elements
        disabled = obj in self._disabled
        if active or disabled:
            mfd = []
            for i in self._elements:
                if i is not obj and isinstance(i, Menu):
                    i.deactivate()
                    mfd.append(i)
                    self._disabled.append(i)
            for i in mfd:
                self._elements.remove(i)
            if disabled:
                self._disabled.remove(obj)
                self._elements.append(obj)
                obj.activate()

    def collidepoint(self, pos):
        """
        Проверяет, находится ли точка внутри собственного глобального прямоугольника.
        :param pos: (x, y)
        :return: bool
        """
        return self._abs_rect.collidepoint(*pos)

    def get_point_hits(self, pos):
        """
        Получить список дочерних элементов (включённых), к которым принадлежит точка.
        :param pos:
        :return: [class Division,...]
        """
        hits = []
        # if self.collidepoint(pos):
        for i in self._elements:
            if i.collidepoint(pos):
                hits.append(i)
        return hits

    def start_step(self, upd_time):
        """
        Подготовка к итерации приложения.
        """
        self.in_step = True
        ms = pygame.mouse.get_pos()
        self.step_time = upd_time
        self._abs_rect = self.calculate_global_rect()
        if self.collidepoint(ms):
            self._mouse_hovers()
        else:
            self._mouse_not_hovers()
        for i in self._elements:
            i.start_step(upd_time)

    def update(self):
        """
        Итерация приложения.
        """
        for i in self._elements:
            i.update()

    def end_step(self):
        """
        Завершение итерации приложения.
        """
        for i in self._elements:
            i.end_step()
        self.in_step = False

    def send_event(self, event):
        """
        Получение события и отправка дочерним элементам.
        """
        self.event = event
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.hover:
                    self.button_down()
                elif self.select and (not self._parent or self._parent.hover):
                    self.select_off()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.button_up()
                if self.press:
                    self.on_event_hit(event)
        if self.hover:
            self.on_event_hit(event)
        for i in self._elements:
            i.send_event(event)
        self.post_handle(event)

    def post_handle(self, event):
        """
        Переопределяемый.
        Постобработка события.
        """
        pass

    def on_event_hit(self, event):
        """
        Переопределяемый.
        Вызывается, если событие обращено к этому элементу.
        """

    def draw(self, surface):
        self.on_draw()
        image = self.get_state_image()
        if image is not None:
            self.draw_image(surface, image)
        for i in self._elements:
            i.draw(surface)
        if self._draw_debug:
            self.draw_debug(surface)

    def get_state_image(self):
        return self.image

    def draw_image(self, surface, image):
        r = self.global_rect.pygame
        surface.blit(pygame.transform.scale(image, r.size), r.topleft)

    def draw_debug(self, surface):
        if self.press:
            pygame.draw.rect(surface, (0, 255, 0), self._abs_rect.pygame, 1)
        elif self.hover:
            pygame.draw.rect(surface, (255, 255, 0), self._abs_rect.pygame, 1)
        else:
            pygame.draw.rect(surface, (255, 0, 0), self._abs_rect.pygame, 1)

    def __len__(self):
        return len(self._elements)

    def __iter__(self):
        return iter(self._elements)

    def __getitem__(self, ind):
        return self._elements[ind]

    def __setitem__(self, ind, val):
        self._elements[ind] = val

    def __delitem__(self, ind):
        del self._elements[ind]

    def _mouse_hovers(self):
        if not self.hover:
            self.on_focus()
        self.hover = True

    def _mouse_not_hovers(self):
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
        """
        У каждого элемента может быть один дочерний, который является selected.
        :param obj: class Division
        """
        if obj is not self.selected:
            if self.selected is not None:
                self.selected.select = False
                self.selected.on_unselect()
            self.selected = obj
            obj.select = True
            obj.on_select()

    def unset_selected(self, obj):
        if obj is self.selected:
            self.selected = None
        obj.select = False
        obj.on_unselect()

    def select_on(self):
        self.select = True
        if self._parent:
            self._parent.set_selected(self)
        else:
            self.on_select()

    def select_off(self):
        self.select = False
        if self._parent:
            self._parent.unset_selected(self)
        else:
            self.on_unselect()

    def on_select(self):
        """
        Переопределяемый.
        По клику на элемент он становится selected (self.select = True)
        """
        pass

    def on_unselect(self):
        """
        Переопределяемый.
        При повторном клике на элемент он становится not selected (self.select = False)
        """
        pass

    def on_click(self):
        """
        Переопределяемый.
        Наведя на элемент, мышь зажали, а потом отпустили, когда она была наведена на этот же элемент.
        """
        pass

    def on_hold(self):
        """
        Переопределяемый.
        Мышь зажали, когда она была наведена на элемент.
        """
        pass

    def on_unhold(self):
        """
        Переопределяемый.
        Мышь отпустили и при этом до этого зажали кнопку наведя на этот же элемент.
        """
        pass

    def on_focus(self):
        """
        Переопределяемый.
        Элемент получил фокус (Первая итерация, когда мышь наведена)
        """
        pass

    def on_unfocus(self):
        """
        Переопределяемый.
        Элемент потерял фокус (Во время фокуса мышь убрали с элемента)
        """
        pass

    def on_draw(self):
        """
        Переопределяемый.
        Вызывается при каждой отрисовке.
        """
        pass


class Menu(Division):
    pass


class Element(Division):
    """
    Элемент, который может содержать текст.
    """
    font = FONT.default

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
    """
    Перечёркнутый элемент.
    Для использование проведите двойное наследование от этого класса и другого.
    """

    def draw(self, surface):
        super().draw(surface)
        b_rect = self._abs_rect
        pygame.draw.line(surface, (255, 0, 0), b_rect.topleft, b_rect.bottomright, 2)
        pygame.draw.line(surface, (255, 0, 0), b_rect.topright, b_rect.bottomleft, 2)


class Button(Element):
    """
    Кнопка.
    Может хранить 3 изображения в self.images для каждого из своих состояний.
    (ничего, зажата, мышь наведена)
    """
    images = (
        None, None, None
    )

    def get_state_image(self):
        return self.images[1 if self.press else (2 if self.hover else 0)]

    def on_event_hit(self, event):
        """
        Переопределён.
        устанавливает аттрибут event.ignore=True, чтобы другие пкнопки не забрали его себе.
        """
        if (self.press or self.hover) and event.type in MOUSE_EVENTS:
            event.ignore = True


class InputBox(Element):
    """
    Поле ввода текста.
    В self.images - 2 изображения для нормального и выделенного состояния.
    """
    images = (
        None,
        None
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = u''
        self.max_text_length = 50
        self.text_color = (255, 255, 255)
        self.select = False
        self.timer = 0
        self.display_caret = False

    def start_step(self, upd_time):
        super().start_step(upd_time)
        if self.select:
            self.timer += upd_time
            if self.timer >= 1000:
                self.display_caret = not self.display_caret
                self.timer = 0

    def get_state_image(self):
        return self.images[int(self.select)]

    def draw_text(self, surface):
        if self.text or self.display_caret:
            draw_text(self.font,
                      surface,
                      self.text + ('|' if self.display_caret else ''),
                      self._abs_rect,
                      color=self.text_color,
                      alignment=self.text_alignment,
                      size=self.text_size)

    def on_click(self):
        self.select = True
        self.display_caret = True
        self.timer = 0

    def on_event_hit(self, event):
        if event in MOUSE_EVENTS:
            event.ignore = True

    def deactivate(self):
        self.select = False
        self.display_caret = False
        self.timer = 0
        super().deactivate()

    def on_select(self):
        self.display_caret = True

    def on_unselect(self):
        self.display_caret = False
        self.timer = 0

    def on_input_completion(self):
        """
        Переопределяемый. Вызывается при завершения ввода.
        """
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
                elif len(self.text) < self.max_text_length:
                    self.text += event.unicode
            event.ignore = True


class ProgressBar(Element):
    """
    "Полоса прогрузки" как это иногда называют.
    image, progress хранят изображения фона и заполнителя.
    """
    image = None
    progress = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = None
        del self.image
        self.percentage = 100

    def draw(self, surface):
        super().draw(surface)
        if self.progress is not None:
            b_rect = self._abs_rect
            size = b_rect.pygame.size
            scaled = pygame.transform.scale(self.progress, size)
            surface.blit(scaled.subsurface((0, 0, int(size[0] * self.percentage / 100), size[1])), b_rect.topleft)
