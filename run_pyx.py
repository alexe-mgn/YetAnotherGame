if __name__ == '__main__':
    import pyximport

    pyximport.install(pyimport=True, build_dir='c_run_temp')
    from game_main import Main

    main = Main()
    main.start()
