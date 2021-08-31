import importlib
import inspect
import sys
import builtins

from .GraphEntity import GraphFunctionEntity, GraphConstantEntity, GraphClassEntity
from .IPythonSniffer import IPythonSniffer
import types


class BuiltInSniffer(IPythonSniffer):
    def __init__(self):
        super().__init__()

    def getfunctionnames(self):
        return [(name, obj) for name, obj in vars(builtins).items() if isinstance(obj, types.BuiltinFunctionType) and not name.startswith("__")]
    def getEverything(self):
        return dir(builtins)

    def getAtributeInfo(self, function):
        return "", None

    def getModuleInfo(self):
        ret = []
        for s in sys.builtin_module_names:
            classes = []
            functions = []
            constants = []
            module = importlib.import_module(s)
            if("_" not in s): #no semi private objetcs
                for name, obj in vars(module).items():
                    if("__" not in name and "_" not in name): #no (semi) private objects
                        if(isinstance(obj, types.BuiltinFunctionType)):
                            displayname, attributes = self.getAtributeInfo(obj)
                            functions.append(GraphFunctionEntity(obj, name, displayname, attributes))
                        elif(isinstance(obj, int) or isinstance(obj, float) or isinstance(obj, str) or isinstance(obj, complex)): #primitive datentypen
                            constants.append(GraphConstantEntity(obj, name, name))
                        elif(inspect.isclass(obj)):
                            classattributes = inspect.getmembers(obj, lambda a: not (inspect.isroutine(a)))
                            methods = []
                            #print(name + " " + str(type(obj)) + str(obj.__bases__))
                            for thing in inspect.getmembers(obj):
                                if not thing in classattributes:
                                    methods.append(thing)
                            classes.append(GraphClassEntity(obj, name, name, methods, classattributes))
                            #for a in classattributes:
                            #    if not (a[0].startswith('__') and a[0].endswith('__')):
                            #        print("\t\t" + str(a))
                            #print("\tfunctions: ")
                            #for a in functions:
                            #    if not (a[0].startswith('__') and a[0].endswith('__')):
                            #        print("\t\t" + str(a))
                        else: #objects
                            constants.append(GraphConstantEntity(obj, name, name))
                            #print("\t\t" + name + " " + str(type(obj)))
            ret.append((s, functions, classes, constants))
        return ret
