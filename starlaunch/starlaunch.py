import sys

from starlaunch import gui, lib


def main():
    if len(sys.argv) > 1:
        cli_run()
    else:
        gui_run()


def gui_run():
    model = lib.Application()
    app = gui.Application(model)
    app.run()


def cli_run():
    model = lib.Application()
    name = sys.argv[1]
    for inst in model.instances:
        if inst.name == name:
            inst.launch()
            break
    else:
        sys.exit('Invalid instance named!')


if __name__ == '__main__':
    main()
