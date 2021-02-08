"""
This is a representation of a ship part.
"""


class CShipPart(object):


    def __init__(self, sName, fDamage, fDetection, fShield, fSpeed, fStealth, fStructure):
        self.__m_sName = sName
        self.__m_fDamage = fDamage
        self.__m_fDetection = fDetection
        self.__m_fShield = fShield
        self.__m_fSpeed = fSpeed
        self.__m_fStealth = fStealth
        self.__m_fStructure = fStructure


    def sGetName(self):
        return self.__m_sName


    def fGetDamage(self):
        return self.__m_fDamage


    def fGetDetection(self):
        return self.__m_fDetection


    def fGetShield(self):
        return self.__m_fShield


    def fGetSpeed(self):
        return self.__m_fSpeed


    def fGetStealth(self):
        """
        Get the stealth strength of the ship part.
        """

        return self.__m_fStealth


    def fGetStructure(self):
        return self.__m_fStructure
