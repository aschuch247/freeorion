"""
This class contains methods to manage the research queue of the empire.
"""


class CResearchQueue(object):


    def __init__(self, fo):
        self.fo = fo


    def vLog(self):
        print '--- research queue ---'

        for oFoResearchQueueElement in self.fo.getEmpire().researchQueue:
            print '\'%s\'' % (oFoResearchQueueElement.tech)
