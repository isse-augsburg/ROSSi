import hashlib
import threading
from datetime import datetime
from subprocess import PIPE, run, Popen
from time import sleep

import psutil
import typing


# TODO remove at the end
class Processrunner(threading.Thread):
    process = None
    name: str
    namespace: str
    package_name: str
    executable_name: str
    command: str
    callback: typing.Callable[[bytes], typing.Any]

    def __init__(self, package_name: str, executable_name: str):
        super(Processrunner, self).__init__()
        self.package_name = package_name
        self.executable_name = executable_name
        tmp = str(int(datetime.now().timestamp() * 1000))
        self.name = "blackboxnode_"+tmp
        self.namespace = "/blackboxnamespace_"+tmp
        self.fullname = self.namespace + "/" + self.name
        print(package_name, executable_name)

    def execute_command(self, command: str, callback: typing.Callable[[bytes], typing.Any]) -> None:
        self.command = command
        self.callback = callback
        self._start_node()
        self.start()

    def _start_node(self):
        command = "exec ros2 run {0} {1} --ros-args -r __ns:={2} -r __node:={3}".format(
            self.package_name, self.executable_name, self.namespace, self.name)
        self.process = Popen(command, shell=True, stdout=PIPE)

    def run(self):
        while True:
            result = run(["ros2 node list"], shell=True, stdout=PIPE)
            #print(self.fullname, str(result.stdout), self.fullname in str(result.stdout))
            #our node is here now
            if self.fullname in str(result.stdout):
                #print(result.stdout.decode("utf-8"))
                break
        result = run([self.command + self.fullname], shell=True, stdout=PIPE)
        self.callback(result.stdout)
        print(result.stdout.decode("utf-8"))
        self._killit(self.process.pid)

    def _killit(self, proc_pid):
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            print(proc.pid)
            proc.kill()
        process.kill()


class NodeInfo:
    package_name: str
    executable_name: str
    callback: typing.Callable[[str], typing.Any]

    def __init__(self, package_name: str, executable_name: str):
        self.package_name = package_name
        self.executable_name = executable_name

    def get_topics(self, callback: typing.Callable[[str], typing.Any]):
        runner = Processrunner(self.package_name, self.executable_name)
        self.callback = callback
        runner.execute_command("ros2 node info ", self._callback)

    def _callback(self, infos: bytes):
        string = infos.decode("utf-8")
        #print(string)
        self.callback(string)


class Ros2SystemInfo:
    callback: typing.Callable[[typing.List["AbstractGraphEntity"]], typing.Any]

    def get_infos(self, callback: typing.Callable[[typing.List["AbstractGraphEntity"]], typing.Any]):
        self.callback = callback
        runner = Processrunner

    def _callback(self, infos: bytes):
        string = infos.decode("utf-8")
        self.callback(string)
