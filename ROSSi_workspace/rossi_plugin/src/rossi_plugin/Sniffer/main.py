import os

from Sniffer.PkgutilSniffer import *
from Sniffer.BuiltInSniffer import *
from Sniffer.OperatorSniffer import *


class Example:
    bool143 = True
    bool2 = True
    blah = False
    foo = True
    foobar2000 = False

def getattributes(module):
    return [attr for attr in dir(module) if not callable(getattr(module, attr)) and not attr.startswith("__")]



for m in sys.modules: #all imported modules since start of python
    print(m)
print("----------------")
#print(sys.modules[__name__])
#print("1")

#for current_module in sys.modules:
#    for key in dir(current_module):
#        print(key)
#        if isinstance( getattr(current_module, key), type):
#            pass#print(key)
print()
print(os.getcwd())
for p in pkgutil.iter_modules([os.path.dirname(__file__)]): #for all submodules on path, or, if path is None, all top-level modules on sys.path.
    print(str([(name, obj) for name, obj in inspect.getmembers(p) if "__" not in name and not name.startswith("_")]))
    if p.ispkg:
        module = importlib.import_module(p.name)
        print(p.name)
        # print(importlib.util.find_spec(p.name))
        for pp in dir(module):
            #print("\t" + pp)
            if isinstance(print, types.FunctionType):
                for ppp in inspect.getfullargspec(pp):
                    pass
                    #print("\t\t" + ppp)

            # elif isinstance(print, types.BuiltinFunctionType):
            #    print("\t\t c function")
        for attribute in getattributes(module):
            pass
            #print("attr: " + str(module) + " " +  attribute)



for s in getattributes(Example):
    pass
    #print(s)


print()
sniffer = OperatorSniffer()

for module in sniffer.getModuleInfo():
    name, functions, classes, constants = module
    #print(name + ":")
    for graphFunctionEntity in functions:
        #print("\t" + graphFunctionEntity.name + " (" + graphFunctionEntity.displayName + ") " + " has following attributes:")
        if graphFunctionEntity.attributes is not None:
            pass
            #print("\t\t" + str([s for s in graphFunctionEntity.attributes]))
        else:
            pass
            #print("\t\tunknown")
        #print(t + " " + str(a) + "\n")
sniffer = PkgutilSniffer()
for module in sniffer.getModuleInfo():
    pass
