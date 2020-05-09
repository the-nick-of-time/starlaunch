import platform
from pathlib import Path
from typing import List

import gui
from lib import ApplicationSettings, Instance


class Application:
    def __init__(self):
        self.configfile = config_file()
        if not self.configfile.exists():
            create_file(self.configfile)
        self.settings = ApplicationSettings(self.configfile)
        self.instances = read_instances(self.settings.instances_dir, self.settings)

    @staticmethod
    def launch(instance: Instance):
        instance.launch()


def read_instances(instanceroot: Path, settings: ApplicationSettings) -> List[Instance]:
    instances = []
    for instance in instanceroot.iterdir():
        if not instance.is_dir():
            continue
        instance_file = instance / 'instance.json'
        if not instance_file.exists():
            continue
        instances.append(Instance(instance_file, settings))
    return instances


def config_file() -> Path:
    if platform.system() == 'Windows':
        return Path.home() / 'AppData/Roaming/starlaunch/settings.json'
    return Path.home() / '.config/starlaunch/settings.json'


def create_file(file: Path):
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text('{}')


def main():
    app = gui.Application()
    app.run()


if __name__ == '__main__':
    main()
