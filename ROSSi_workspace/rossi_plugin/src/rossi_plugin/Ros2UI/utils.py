import importlib
import pkgutil
from inspect import isclass


def dynamic_import(name):
    name = name.replace(" ", "")
    name = name.replace("/", ".")
    components = name.split('.')
    #print(components)
    mod = __import__(components[0])
    #print(mod)
    for comp in components[1:]:
        try:
            #print("trying to get attr", mod, comp)
            mod = getattr(mod, comp)
        except AttributeError as e:
            print(e)
    return mod


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



def dynamic_import_ros2_msg(name):
    name = name.replace(" ", "")
    name = name.replace("/", ".")
    components = name.split('.')
    mod = __import__(components[0]+"." + components[1])
    for comp in components[1:]:
        try:
            #print("trying to get attr", mod, comp)
            mod = getattr(mod, comp)
        except AttributeError as e:
            print(e)
    return mod
from geometry_msgs.msg import PointStamped


def fullname(object) -> str:
    module = object.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return object.__class__.__name__
    else:
        return module + "." + object.__class__.__name__