from typing import List

from ....Representations.Python3Representations import ClassRep, ConstantRep, FunctionRep


class ModuleRep:
    name: str
    functions: List[FunctionRep]
    classes: List[ClassRep]
    constants: List[ConstantRep]

    def __init__(self, name, classes=None, functions=None, constants=None):
        self.classes = classes
        self.functions = functions
        self.constants = constants
        self.name = name


