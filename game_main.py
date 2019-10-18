import Engine.main


class Main(Engine.main.Main):

    def home(self):
        """
        Выйти в главное меню. Ну или как захотите.
        """
        self.set_level(None)
        from Game.GUI import MainMenu
        self.set_gui(MainMenu(main=self))

    def load_survival(self):
        """
        ABOUT TO BE DELETED
        Загрузка тестового уровня.
        """
        from Game.Levels.Survival import Survival
        self.set_level(Survival(self))
        self.set_gui(None)


if __name__ == '__main__':
    main = Main()
    main.start()
