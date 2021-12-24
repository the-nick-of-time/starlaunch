import json
import os
import platform
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List


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
        if not directory.exists():
            directory.mkdir(parents=True)
        if directory.is_dir():
            return directory
        else:
            raise FileExistsError(f"{directory} exists but is not a directory")

    def set_starbound_dir(self, value):
        self.data['starbound_dir'] = value

    @property
    def instances_dir(self) -> Path:
        if 'instances_dir' not in self.data:
            self.data['instances_dir'] = str(Path.home() / 'games/starbound/instances')
        directory = Path(self.data['instances_dir'])
        if not directory.exists():
            directory.mkdir(parents=True)
        if directory.is_dir():
            return directory
        else:
            raise FileExistsError(f"{directory} exists but is not a directory")

    def set_instances_dir(self, value):
        self.data['instances_dir'] = value

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

    def set_storage(self, value: Path):
        self.data['storage'] = self.make_path_relative(value)

    @property
    def mods(self) -> Path:
        if 'mods' in self.data:
            return make_path(self.data['mods'], self.applicationSettings.starbound_dir,
                             self.location)
        return self.location / 'mods'

    def set_mods(self, value: Path):
        self.data['mods'] = self.make_path_relative(value)

    @property
    def name(self) -> str:
        if 'name' in self.data:
            return self.data['name']
        return 'Starbound'

    def set_name(self, value: str):
        self.data['name'] = value

    def make_path_relative(self, path: Path) -> str:
        try:
            # instance-relative?
            return 'inst:' + str(path.relative_to(self.location))
        except ValueError:
            pass
        try:
            # root installation-relative?
            return 'sb:' + str(path.relative_to(self.applicationSettings.starbound_dir))
        except ValueError:
            # fall back on absolute
            return str(path)

    def write(self):
        with self.file.open('w') as f:
            json.dump(self.data, f, indent=2)

    def config_file_contents(self, tempdir: str) -> dict:
        return {
            "assetDirectories": [
                str(self.applicationSettings.starbound_dir / '../assets'),
                str(self.mods),
            ],
            "storageDirectory": str(self.storage)
        }

    def patch_file_contents(self):
        return [{
            "op": "replace",
            "path": "/windowTitle",
            "value": self.name
        }]

    def launch(self):
        starbound = exe(self.applicationSettings.starbound_dir / 'starbound')
        libs = (f"{os.environ.get('LD_LIBRARY_PATH', '')}:"
                f"{self.applicationSettings.starbound_dir}")
        env = {**os.environ, 'LD_LIBRARY_PATH': libs}
        with TemporaryDirectory() as dirname:
            configname = f"{dirname}/sbinit.config"
            with open(configname, 'w') as config:
                json.dump(self.config_file_contents(dirname), config, indent=2)
            (Path(dirname) / 'assets').mkdir()
            with (Path(dirname) / 'assets/client.config.patch').open('w') as patch:
                json.dump(self.patch_file_contents(), patch)
            subprocess.run([starbound, '-bootconfig', configname], env=env,
                           cwd=str(self.applicationSettings.starbound_dir))

    def launch_server(self):
        starbound = exe(self.applicationSettings.starbound_dir / 'starbound_server')
        libs = (f"{os.environ.get('LD_LIBRARY_PATH', '')}:"
                f"{self.applicationSettings.starbound_dir}")
        env = {**os.environ, 'LD_LIBRARY_PATH': libs}
        with TemporaryDirectory() as dirname:
            configname = f"{dirname}/sbinit.config"
            with open(configname, 'w') as config:
                json.dump(self.config_file_contents(dirname), config, indent=2)
            try:
                subprocess.run([starbound, '-bootconfig', configname], env=env,
                               cwd=str(self.applicationSettings.starbound_dir))
            except KeyboardInterrupt:
                # SIGINT gets passed to the process, stops it, and that's fine
                pass


def exe(file: Path) -> Path:
    if platform.system() == 'Windows':
        return file.with_suffix('.exe')
    return file


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


class NeedsFirstTimeSetup(Exception):
    pass


class Application:
    def __init__(self):
        self.configfile = config_file()
        if not self.configfile.exists():
            raise NeedsFirstTimeSetup()
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


def first_time_setup(instances: str, starbound: str):
    file = config_file()
    configuration = json.dumps({
        "instances_dir": instances,
        "starbound_dir": starbound,
    })
    file.parent.mkdir(parents=True)
    file.write_text(configuration)
