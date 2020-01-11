"""
This is a manager base class.
"""


class CManager(object):


    def __init__(self, fo):
        self.fo = fo


    def _bIsOwn(self, oUniverseObject):
        return oUniverseObject.ownedBy(self.fo.empireID())
