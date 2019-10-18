if __name__ == '__main__':
    import pyximport

    pyximport.install(pyimport=True, build_dir='c_run_temp')
    from Engine.main import Main

    main = Main()
    main.start()
