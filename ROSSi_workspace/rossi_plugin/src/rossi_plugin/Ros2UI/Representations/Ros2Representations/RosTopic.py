from abc import ABC

from .RosQOS import RosQOS


class RosTopic:
    def __init__(self, name: str, msg_type: str, QOS: RosQOS = None):
        self.name = name
        self.msg_type = msg_type
        self.QOS = QOS

    def equals(self, topic: 'RosTopic'):
        # TODO return self.name == topic.name and self.QOS.equals(topic.QOS) and self.msg_type == topic.msg_type
        return self.name == topic.name and self.msg_type == topic.msg_type
        pass


class AbstractRosTopicUser(ABC):
    def __init__(self, topic: RosTopic):
        self.topic = topic


class RosPublisher(AbstractRosTopicUser):
    def __init__(self, topic: str, msg_type: str, QOS: RosQOS = None):
        super(RosPublisher, self).__init__(RosTopic(topic, msg_type, QOS))


class RosSubscriber(AbstractRosTopicUser):
    def __init__(self, topic: str, msg_type: str, QOS: RosQOS = None):
        super(RosSubscriber, self).__init__(RosTopic(topic, msg_type, QOS))
