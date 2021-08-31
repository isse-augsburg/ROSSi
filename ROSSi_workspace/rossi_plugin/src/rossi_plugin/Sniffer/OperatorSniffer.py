import operator
from .IPythonSniffer import IPythonSniffer
import types
from .GraphEntity import GraphFunctionEntity


class OperatorSniffer(IPythonSniffer):
    def __init__(self):
        super().__init__()

    def getAtributeInfo(self, function):
        # eq(a, b) -- Same as a==b.
        string = function.__doc__
        if "--" in string:
            l = str.split(string, "(")
            l = str.split(l[1], ")")
            # a,b
            attr = str.split(l[0], ",")
            attributes = []
            displayname = ""
            if(" Same as " in string):
                displayname = str.split(string, " Same as ")[1]
                displayname = displayname.replace(".", "")
            return displayname, attr
        else:
            return "", None

    def getfunctionnames(self):
        return [(name, obj) for name, obj in vars(operator).items() if
                isinstance(obj, types.BuiltinFunctionType) and not name.startswith("__")]

    def getEverything(self):
        return dir(operator)

    def getModuleInfo(self):
        list = []
        for name, obj in vars(operator).items():
            if isinstance(obj, types.BuiltinFunctionType) and not name.startswith("__"):
                displayname, attributes = self.getAtributeInfo(obj)
                list.append(GraphFunctionEntity(obj, name, displayname, attributes))
            elif not name.startswith("__"):
                print(str(obj), str(type(obj))) #TODO there are three classes in here
        return [("operators", list, [], [])]
