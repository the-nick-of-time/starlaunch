import json
import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile


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
        if 'starbound_dir' in self.data:
            directory = Path(self.data['starbound_dir'])
            if directory.is_dir():
                return directory
        raise NoBaseDir('No or invalid base directory set')

    @property
    def instances_dir(self) -> Path:
        if 'instances_dir' in self.data:
            directory = Path(self.data['instances_dir'])
            if directory.is_dir():
                return directory
        raise NoInstancesDir('No or invalid instances directory set')

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

    @property
    def mods(self) -> Path:
        if 'mods' in self.data:
            return make_path(self.data['mods'], self.applicationSettings.starbound_dir,
                             self.location)
        return self.location / 'mods'

    @property
    def name(self) -> str:
        if 'name' in self.data:
            return self.data['name']
        raise NoName('Instance must have a name')

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
