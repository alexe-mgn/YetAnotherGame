class NameSpace:
    """
    Simple namespace with pretty creation procedure.
    Usage:
    class namespace(NameSpace):
        var1 = 1
        var2 = 2
        var3 = 3

    namespace.var1
    namespace.as_dict()
    namespace.keys()
    namespace.values()
    namespace.items()
    namespace.as_dict()['var1']
    namespace.values()
    """
    builtins = []

    @classmethod
    def __getitem__(cls, key):
        return getattr(cls, key)

    @classmethod
    def __setitem__(cls, key, value):
        setattr(cls, key, value)

    @classmethod
    def as_dict(cls):
        return {k: v for k, v in cls.__dict__.items() if k not in cls.builtins}

    @classmethod
    def keys(cls):
        return [k for k in cls.__dict__.keys() if k not in cls.builtins]

    @classmethod
    def values(cls):
        return [v for k, v in cls.__dict__.items() if k not in cls.builtins]

    @classmethod
    def items(cls):
        return [e for e in cls.__dict__.items() if e[0] not in cls.builtins]

    @classmethod
    def init_class(cls):
        cls.builtins = dir(cls)
        cls.builtins.append('builtins')


NameSpace.init_class()


def transform_name(string):
    return ''.join([' ' if e.isspace() else e for e in string])


class EmptyGameObject:
    """
    Объект, который можно использовать при отсутствии GUI или уровня.
    """
    _draw_debug = False

    def start_step(self, upd_time):
        pass

    def update(self):
        pass

    def end_step(self):
        pass

    def send_event(self, event):
        pass

    def handle_keys(self):
        pass

    def draw(self, surface):
        pass

    def pregenerate(self):
        pass

    def set_screen(self, *args):
        pass

    @property
    def main(self):
        return

    @main.setter
    def main(self, o):
        pass

    def __bool__(self):
        return False
