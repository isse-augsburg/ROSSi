from ros2pkg.api import get_package_names
from ros2launch.api import get_share_file_path_from_package
from ros2pkg.api import get_executable_paths
from ros2node.api import get_publisher_info
from ros2node.api import get_subscriber_info
import os
# . /opt/ros/dashing/setup.bash
# pycharm-community . (in project folder)

class ROS2Sniffer:
    def __init__(self):
        pass

    def getStuff(self):
        ret = {}
        for pkg_name in get_package_names():
            pkg = {}
            paths = get_executable_paths(package_name=pkg_name)
            #print(pkg_name)
            for path in sorted(paths):
                pkg[os.path.basename(path)] = {}
                #print("\t" + os.path.basename(path))
            ret[pkg_name] = pkg
        #print(ret)
        return ret

if __name__ == '__main__':
    ROS2Sniffer()
