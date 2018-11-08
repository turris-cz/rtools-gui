
def main(argv):
    from .application import Application
    from .guard import Guard

    with Guard():
        app = Application(argv)

        # this import need to be used after the app is created
        from rtools_gui.mainwindow import MainWindow
        mainwindow = MainWindow()
        mainwindow.show()
        retval = app.exec_()

    exit(retval)
