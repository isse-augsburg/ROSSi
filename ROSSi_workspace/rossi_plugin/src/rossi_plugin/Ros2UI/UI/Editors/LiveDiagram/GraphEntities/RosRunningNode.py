from typing import List

from .....Representations.Ros2Representations.RosTopic import RosPublisher, RosSubscriber


# Represents a running node in the current ROS 2 Environment
# Used in UI/Editors/LiveDiagram
class RosRunningNode:
    publishers: List[RosPublisher]
    subscribers: List[RosSubscriber]

    def __init__(self, name: str, publisher: List[RosPublisher], subscriber: List[RosSubscriber], namespace: str = ""):
        self.name = name
        self.namespace = namespace
        self.publishers = publisher
        self.subscribers = subscriber

    def getMatchingTopics(self, other: 'RosRunningNode'):
        pubs = []
        subs = []

        for pub in other.publishers:
            for pub2 in self.publishers:
                if pub.topic.equals(pub2.topic):
                    pubs.append(pub.topic)

        for sub in other.subscribers:
            for sub2 in self.subscribers:
                if sub.topic.equals(sub2.topic):
                    subs.append(sub.topic)

        return pubs, subs

    # returns true if names and namespaces are equal
    def equals(self, node: 'RosRunningNode') -> bool:
        return self.name == node.name and self.namespace == node.namespace

