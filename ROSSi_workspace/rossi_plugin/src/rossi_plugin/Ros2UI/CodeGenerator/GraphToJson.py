import importlib
import json
import pkgutil
import types
from inspect import isclass
from typing import List

from ..UI.BaseGraphEntities.StandartGraphEntity import StandartGraphEntity
from ..UI import Editors as Editors
#from ..utils import import_submodules


def exportJson(file: str, items: List[StandartGraphEntity], basename: str) -> None:
    ret = []
    for item in items:
        ret.append(item.toJson())
    with open(file, "w") as f:
        print(basename, ret)
        json.dump({str(basename): ret}, f, indent=4)


# TODO only works if run here (thats why there is a duplicate in Ros2UI.utils.
def import_submodules(package, recursive=True):
    # based on https://stackoverflow.com/questions/3365740/how-to-import-all-submodules
    """ Import all submodules of a module, recursively, including subpackages
    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
        elif recursive:
            for attribute_name in dir(results[full_name]):
                attribute = getattr(results[full_name], attribute_name)
                if isclass(attribute):
                    globals()[attribute_name] = attribute
    return results


# exports a json file
def importJson(file: str, basename: str) -> List[StandartGraphEntity]:
    ret: List[StandartGraphEntity] = []
    # imports all classes inside Editors module
    import_submodules(Editors.__name__)
    with open(file, "r") as f:
        data2 = json.load(f)
        if data2[basename] is not None:
            for tr in data2[basename]:
                for key in tr.keys():
                    data = tr[key]
                    ret.append(eval(key).fromJson(data))
    return ret


