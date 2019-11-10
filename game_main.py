try:
    import Engine.main
except ImportError as error:
    import traceback

    traceback.print_exc()
    print("Error occurred when trying to import Engine.")
    print("Likely submodule was not initialized")
    print("Run update_engine.bat")
    input("Press enter to continue")
else:

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
