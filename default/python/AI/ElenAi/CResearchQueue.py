"""
This class contains methods to manage the research queue of the empire.
"""


class CResearchQueue(object):


    def __init__(self, fo):
        self.fo = fo


    def bIsEnqueued(self, sTechnology):
        return self.fo.getEmpire().researchQueue.inQueue(sTechnology)


    def vEnqueue(self, sTechnology):
        print 'Enqueuing technology \'%s\' with result %d.' % (
            sTechnology,
            self.fo.issueEnqueueTechOrder(sTechnology, self.fo.getEmpire().researchQueue.size + 1)
        )


    def vLog(self):
        print '--- research queue ---'

        for oFoResearchQueueElement in self.fo.getEmpire().researchQueue:
            print '\'%s\'' % (oFoResearchQueueElement.tech)
