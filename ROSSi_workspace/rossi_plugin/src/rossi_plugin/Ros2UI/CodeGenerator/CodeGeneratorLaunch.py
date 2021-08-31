from typing import List, Tuple

from PyQt5.QtWidgets import QGraphicsItem

from ..UI.BaseGraphEntities import StandartGraphEntity
from ..UI.Editors.LaunchFileEditor.GraphEntities.RosArgumentGraphEntity import RosArgumentGraphEntity
from ..UI.Editors.LaunchFileEditor.GraphEntities.RosNamespaceGraphEntity import RosNamespaceGraphEntity


# a class that makes a Launch File from a bunch of StandartGraphEntities
class CodeGeneratorLaunch:
    tabsize: int = 4
    imports: List[str]
    function: List[str]
    code: List[str]
    endfunction: List[str]

    def __init__(self, inputs: List[StandartGraphEntity.StandartGraphEntity], base: QGraphicsItem):
        # set up the basic skeleton of a ROS 2 launch file
        self.inputs = inputs
        self.base = base
        self.imports = [
            "from launch import LaunchDescription",
        ]
        self.function = [
            "\ndef generate_launch_description():",
            "\treturn LaunchDescription(["
        ]
        self.code = []
        self.endfunction = [
            "\t])"
        ]

        # collect all Nodes that lie in no Namespace, get their code and needed imports
        args = []
        for item in self._getOuterNodes():
            if type(item) is RosArgumentGraphEntity:
                args.append(item)
            else:
                code, imports = item.toCode(2)
                self._addImports(imports)
                self.code.extend(code)

        # arguments have to be treated separately, because their order matters
        arg_code, imports = self._getArgumentCode(args, 2)
        self._addImports(imports)
        if arg_code is not None:
            arg_code.extend(self.code)
            self.code = arg_code

        # next, collect all outer namespaces. Means all namespaces without a parent namespace
        # then iterate recursively through their child namespaces and other items inside
        # add imports and code of those items
        for namespace in self._getOuterNamespaces():
            if namespace.childItems() is not None and namespace.childItems is not []:
                code, imports = namespace.toCode(2, self._recNamespace(namespace, 2))
                self._addImports(imports)
                self.code.extend(code)

    # returns ordered code for all args given
    def _getArgumentCode(self, args: List[RosArgumentGraphEntity], intend: int) -> Tuple[List[str], List[str]]:
        code: List[str] = []
        imports: List[str] = []
        sort_of_sorted: List[List[RosArgumentGraphEntity]] = []
        platt: List[RosArgumentGraphEntity] = []

        for item in args:
            # gather all subtrees of items not yet visited
            if not any(item in x for x in sort_of_sorted):
                arr = self._recArg(item, [])
                arr.reverse()  # so 'roots' will be at index 0
                sort_of_sorted.append(arr)

        for arr in sort_of_sorted:
            for item in arr:
                if item not in platt:
                    platt.append(item)

        for item in platt:
            c, i = item.toCode(intend)
            code.extend(c)
            imports.extend(i)

        return code, imports

    # should return all arguemnts with higher level than arg's level
    def _recArg(self, arg: RosArgumentGraphEntity, so_far: List[RosArgumentGraphEntity]) -> List[RosArgumentGraphEntity]:
        parents = arg.getParentArgumentGraphEntities()

        # TODO check for circles

        so_far.append(arg)
        # print("added", arg.name, [item.name for item in so_far])
        if len(parents) > 0:
            for par in parents:
                #print("found parents", [item.name for item in parents])
                so_far.extend(self._recArg(par, []))

        return so_far

    def _recNamespace(self, namespace: RosNamespaceGraphEntity, intend: int = 0):
        code: List[str] = []
        for item in namespace.childItems():
            if item is not namespace.port:
                if isinstance(item, RosNamespaceGraphEntity) and item.parentItem() is namespace:
                    c, imports = item.toCode(intend + 1, self._recNamespace(item, intend + 1))
                    self._addImports(imports)
                    code.extend(c)
                else:
                    if item.parentItem() is namespace:
                        c, imports = item.toCode(intend + 1)
                        self._addImports(imports)
                        code.extend(c)
        return code

    def _addImports(self, imp):
        for strr in imp:
            if strr not in self.imports:
                self.imports.append(strr)

    def _getOuterNodes(self):
        ret: List[StandartGraphEntity] = []
        for item in self.inputs:
            print(type(item), "please not namespace", not type(item) is RosNamespaceGraphEntity, type(item) is not RosNamespaceGraphEntity)
            if item.parentItem() is self.base and not type(item) is RosNamespaceGraphEntity:
                print("added item")
                ret.append(item)
        return ret

    def _getOuterNamespaces(self):
        ret: List[RosNamespaceGraphEntity] = []
        for item in self.inputs:
            if item.parentItem() is self.base and type(item) is RosNamespaceGraphEntity:
                ret.append(item)
        return ret

    def make_launch_file(self, path: str):
        end = ".launch.py"
        if end not in path:
            path += end
        with open(path, "w+") as out:
            text = []
            text.extend(self.imports)
            text.extend(self.function)
            text.extend(self.code)
            text.extend(self.endfunction)
            for s in text:
                out.write(s + "\n")
