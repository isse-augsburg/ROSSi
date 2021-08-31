from typing import List

import typing
from rosidl_runtime_py import get_message_interfaces

from ....utils import dynamic_import

# {} empty msg exists
# all std field types in ros2 msgs we can directly set in Python3
# sequence<type> = []
std_types = [
    "boolean",  # bool
    "octet",  # byte
    "uint8",  # char, int
    "float",  # color, float32
    "double",  # float64
    "sequence<double>",
    "string",
    "int8",
    "int16",
    "int32",
    "int64",
    "uint64",
    "uint32",
    "uint16",
    "uint8",

]

def getAllTopics() -> List[str]:
    ret = []
    message_interfaces = get_message_interfaces()
    for package_name in sorted(message_interfaces):
        for message_name in sorted(message_interfaces[package_name]):
            ret.append(f'{package_name}/{message_name}')

    return ret


# returns dict with all basic fields and the basic fields of sub message types recursively
# sequences are represented by arrays
def getAllFieldsOfTopic(topic: str) -> typing.Dict:
    ret = {}
    klass = dynamic_import(topic)
    o = klass()
    if hasattr(o, 'get_fields_and_field_types'):
        dic: typing.Dict = o.get_fields_and_field_types()
        for key in dic.keys():
            #print("\t", key, ":", dic[key], type(dic[key]), "sequence<" in dic[key])
            tmp_val = dic[key]
            seq = False
            if "sequence<" in tmp_val:
                tmp = dic[key].split("sequence<")[1]
                tmp = tmp[0:-1]
                tmp_val = tmp
                seq = True
            if tmp_val not in std_types:
                # not a std type
                # type is in this form package_name/class_name
                # python module is package_name.msg.class_name though
                s = tmp_val.split("/")[1:]
                string = ""
                for tmp in s:
                    string += tmp+"."
                string = string[:-1]
                # put everything together
                inner_topic = tmp_val.split("/")[0] + ".msg." + string
                if seq:
                    dic[key] = [getAllFieldsOfTopic(inner_topic)]
                else:
                    dic[key] = getAllFieldsOfTopic(inner_topic)
            if seq:
                dic[key] = [tmp_val]
        ret[topic] = dic
    else:
        ret[topic] = "unknown"
    return ret


def getAllFieldOfTopicOLD(topic: str) -> typing.List:
    klass = dynamic_import(topic)
    o = klass()
    fields = []
    print(dir(o), hasattr(o, 'get_fields_and_field_types'))
    if hasattr(o, 'get_fields_and_field_types'):
        print(o.get_fields_and_field_types())
    for f in dir(o):
        if not callable(getattr(o, f)) and not f.startswith("__") and not f.startswith("_"):
            print(f, type(f))
            fields.append(f)
    return fields