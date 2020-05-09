import gui
import lib


def main():
    model = lib.Application()
    app = gui.Application(model)
    app.run()


if __name__ == '__main__':
    main()
