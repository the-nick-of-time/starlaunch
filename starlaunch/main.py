import sys

from starlaunch import gui, lib


def main():
    if len(sys.argv) > 1:
        cli_run()
    else:
        gui_run()


def gui_run():
    try:
        model = lib.Application()
    except lib.NeedsFirstTimeSetup:
        gui.first_time_setup()
        model = lib.Application()
    app = gui.Application(model)
    app.run()


def cli_run():
    try:
        model = lib.Application()
    except lib.NeedsFirstTimeSetup:
        instances = input("Instances directory: ")
        starbound = input("Directory containing starbound executable: ")
        lib.first_time_setup(instances, starbound)
        model = lib.Application()
    name = sys.argv[-1]
    server = False
    if '--server' in sys.argv:
        server = True
    for inst in model.instances:
        if inst.name == name:
            if server:
                inst.launch_server()
            else:
                inst.launch()
            break
    else:
        sys.exit('Invalid instance named!')


if __name__ == '__main__':
    main()
