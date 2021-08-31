from enum import Enum


class GraphEntity:
    def __init__(self, name, displayName = "", docs=""):
        self.displayName = displayName if displayName != "" else name
        self.docs = docs
        self.name = name

    def getname(self):
        return self.name


class GraphConstantEntity(GraphEntity):
    def __init__(self, value, name, displayName = ""):
        super().__init__(name=name, displayName=displayName, docs="constant")
        self.value = value

#kind:
#POSITIONAL_ONLY
#POSITIONAL_OR_KEYWORD
#VAR_POSITIONAL
#KEYWORD_ONLY
#VAR_KEYWORD
class Parameter():
    def __init__(self, name, kind, default):
        self.name = name
        self.kind = kind
        self.default = default


class GraphFunctionEntity(GraphEntity):
    def __init__(self, function, name, displayName = "",  attributes=[]):
        super().__init__(name=name, displayName=displayName, docs=function.__doc__)
        self.function = function
        self.attributes = attributes


class GraphClassEntity(GraphEntity):
    def __init__(self, _class, name, displayName = "", methods = [], members = []):
        super().__init__(name, displayName, _class.__doc__)
        self._class = _class
        self.methods = methods
        self.members = members


class LibraryModuleEntry:
    def __init__(self, modulename, entries):
        self.modulename = modulename
        self.entries = entries

