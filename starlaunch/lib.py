import json
import platform
import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List


class NoBaseDir(Exception):
    pass


class NoName(Exception):
    pass


class NoInstancesDir(Exception):
    pass


class ApplicationSettings:
    def __init__(self, file: Path):
        self.file = file
        with file.open('r') as f:
            self.data = json.load(f)

    @property
    def starbound_dir(self) -> Path:
        if 'starbound_dir' not in self.data:
            self.data['starbound_dir'] = str(Path.home() / 'games/starbound/starbound')
        directory = Path(self.data['starbound_dir'])
        if directory.is_dir():
            return directory

    @property
    def instances_dir(self) -> Path:
        if 'instances_dir' not in self.data:
            self.data['instances_dir'] = str(Path.home() / 'games/starbound/instances')
        directory = Path(self.data['instances_dir'])
        if directory.is_dir():
            return directory

    def write(self):
        with self.file.open('w') as f:
            json.dump(self.data, f, indent=2)


class Instance:
    def __init__(self, file: Path, settings: ApplicationSettings):
        self.file = file.absolute()
        self.applicationSettings = settings
        with file.open('r') as f:
            self.data = json.load(f)
        self.location = file.parent

    @property
    def storage(self) -> Path:
        if 'storage' in self.data:
            return make_path(self.data['storage'], self.applicationSettings.starbound_dir,
                             self.location)
        return self.location / 'storage'

    @storage.setter
    def storage(self, value: Path):
        self.data['storage'] = str(value)

    @property
    def mods(self) -> Path:
        if 'mods' in self.data:
            return make_path(self.data['mods'], self.applicationSettings.starbound_dir,
                             self.location)
        return self.location / 'mods'

    @mods.setter
    def mods(self, value: Path):
        self.data['mods'] = str(value)

    @property
    def name(self) -> str:
        if 'name' in self.data:
            return self.data['name']
        return 'Starbound'

    @name.setter
    def name(self, value: str):
        self.data['name'] = value

    def write(self):
        with self.file.open('w') as f:
            json.dump(self.data, f, indent=2)

    def config_file_contents(self) -> dict:
        return {
            "assetDirectories": [
                str(self.applicationSettings.starbound_dir / '../assets'),
                str(self.mods)
            ],
            "storageDirectory": str(self.storage)
        }

    def launch(self):
        starbound = self.applicationSettings.starbound_dir / 'starbound'
        # TODO: .autopatch file to change window name
        # { "op": "replace", "path": "/windowTitle", "value": self.name }
        with NamedTemporaryFile(mode='w+', encoding='utf8') as config:
            json.dump(self.config_file_contents(), config)
            subprocess.run([starbound, '-bootconfig', config.name])


def make_path(path: str, sourcedir: Path, instancedir: Path) -> Path:
    if re.match(r'^/|[A-Za-z]:', path):
        # absolute on either linux or windows
        return Path(path)
    if path.startswith('sb:'):
        # starbound dir, strip off the sb beforehand
        return sourcedir / path[3:]
    if path.startswith('inst:'):
        return instancedir / path[5:]
    raise ValueError('Invalid path given, must be absolute or relative to starbound (sb:) or '
                     'instance (inst:) directory')


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

    def write(self):
        self.settings.write()
        for inst in self.instances:
            inst.write()


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
