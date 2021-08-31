from typing import List, Tuple


class CodeHolder:
    def __init__(self):
        pass

    # return constructor code, own code, imports
    def getCode(self, intendLevel=0) -> Tuple[List[str], List[str], List[str]]:
        raise NotImplementedError