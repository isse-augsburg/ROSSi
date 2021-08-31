from typing import List

from .RosTopic import RosPublisher, RosSubscriber


class RosExecutable:
    def __init__(self, executableName: str = None, displayName: str = None, package: 'RosPackage' = None, pubs: List[RosPublisher] = None, subs: List[RosSubscriber] = None):
        self.pubs = pubs
        self.subs = subs
        self.package = package
        self.executableName = executableName
        self.displayName = displayName


class RosPackage:
    def __init__(self, name: str, executables: List[RosExecutable] = None, launchFiles: List[str] = None):
        self.executables = executables
        self.name = name
        self.launchFiles = launchFiles



