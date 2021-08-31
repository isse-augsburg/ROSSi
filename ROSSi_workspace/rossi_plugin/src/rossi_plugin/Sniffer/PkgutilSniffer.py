import importlib
import inspect
import pkgutil
import types

from .GraphEntity import GraphConstantEntity, GraphFunctionEntity, GraphClassEntity, Parameter
from .IPythonSniffer import IPythonSniffer


class PkgutilSniffer(IPythonSniffer):
    def __init__(self):
        super().__init__()

    def getModuleInfo(self):
        ret = []
        for p in pkgutil.iter_modules():
            if p.ispkg:
                classes = []
                functions = []
                constants = []
                #print(str(p.ispkg) + ": -----------")
                try:
                    module = importlib.import_module(p.name)
                    for name, obj in vars(module).items():
                        if isinstance(obj, types.BuiltinFunctionType) and not name.startswith("__"):
                            functions.append(GraphFunctionEntity(obj, name, "", None))
                        elif (isinstance(obj, int) or isinstance(obj, float) or isinstance(obj, str) or isinstance(obj, complex)):  # primitive datentypen
                            if not name.startswith("__"):
                                constants.append(GraphConstantEntity(obj, name, name))
                        elif (inspect.isclass(obj)):
                            classattributes = inspect.getmembers(obj, lambda a: not (inspect.isroutine(a)))
                            methods = []
                            # print(name + " " + str(type(obj)) + str(obj.__bases__))
                            for thing in inspect.getmembers(obj):
                                if not thing in classattributes:
                                    methods.append(thing)
                            classes.append(GraphClassEntity(obj, name, name, methods, classattributes))
                        elif isinstance(obj, types.ModuleType):
                            pass
                        elif isinstance(obj, types.FunctionType):
                            try:
                                #print("\t" + name + " " + str(inspect.signature(obj)))
                                attributes = []
                                for namep, param in inspect.signature(obj).parameters.items():
                                    attributes.append(Parameter(namep, param.kind, param.default if param.default is not inspect.Parameter.empty else None))
                                functions.append(GraphFunctionEntity(obj, name, "", attributes))
                            except:
                                pass
                                #print("\t" + name + " " + str((inspect.getfullargspec(obj))))
                        else:
                            pass#print("\t" + name + " " + str(type(obj)))
                    ret.append((p.name, functions, classes, constants))
                except:
                    print(p.name + " is no module")
        return ret