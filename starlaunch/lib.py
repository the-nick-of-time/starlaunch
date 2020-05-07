import json
import re
from pathlib import Path


class NoBaseDir(Exception):
    pass


class NoName(Exception):
    pass


class ApplicationSettings:
    def __init__(self, file: Path):
        self.file = file
        with file.open('r') as f:
            self.data = json.load(f)

    @property
    def starbound_dir(self) -> Path:
        if 'starbound_dir' in self.data:
            return Path(self.data['starbound_dir'])
        raise NoBaseDir('No base directory set')

    def write(self):
        with self.file.open('w') as f:
            json.dump(self.data, f, indent=2)


class Instance:
    def __init__(self, file: Path, settings: ApplicationSettings):
        self.file = file
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


def make_path(path: str, sourcedir: Path, instancedir: Path) -> Path:
    if re.match(r'/|[A-Za-z]:', path):
        # absolute on either linux or windows
        return Path(path)
    if path.startswith('sb:'):
        # starbound dir, strip off the sb beforehand
        return sourcedir / path[3:]
    if path.startswith('inst:'):
        return instancedir / path[5:]
