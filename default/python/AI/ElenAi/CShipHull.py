"""
This is a representation of a ship hull.
"""


class CShipHull(object):


    def __init__(self, sName, fFuel, fSpeed, fStealth, fStructure):
        self.__m_sName = sName
        self.__m_fFuel = fFuel
        self.__m_fSpeed = fSpeed
        self.__m_fStealth = fStealth
        self.__m_fStructure = fStructure


    def sGetName(self):
        return self.__m_sName


    def fGetDetection(self):

        # @todo This is not implemented right now!

        return -1.0


    def fGetSpeed(self):
        return self.__m_fSpeed


    def fGetStealth(self):
        """
        Get the stealth strength of the ship hull.
        """

        return self.__m_fStealth


    def fGetStructure(self):
        return self.__m_fStructure
