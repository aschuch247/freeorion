"""
Predict the capabilities of a single ship.
"""

from ElenAi.CShipHull import CShipHull
from ElenAi.CShipPart import CShipPart


class CShipPredictor(object):


    def __init__(self, oShip):
        self.__m_oShip = oShip

        self.__m_oShipHull = CShipHull()
        self.__m_oShipPart = CShipPart()


    def bIsArmed(self):
        for sPart in self.__m_oShip.sGetPartList():
            if (self.__m_oShipPart.fGetDamage(sPart) > 0.0):
                return True

        return False


    def fGetDamage(self):
        fDamage = 0.0

        for sPart in self.__m_oShip.sGetPartList():
            fDamage += self.__m_oShipPart.fGetDamage(sPart)

        return fDamage


    def fGetDetection(self):
        fDetection = 0.0

        # Only the ship part with the highest detection range counts.

        for sPart in self.__m_oShip.sGetPartList():
            fDetection = max(fDetection, self.__m_oShipPart.fGetDetection(sPart))

        # Combine the highest detection range ship part and the ship hull detection range.

        return self.__m_oShipHull.fGetDetection(self.__m_oShip.sGetHull()) + fDetection


    def fGetShield(self):
        fShield = 0.0

        # Only the ship part with the highest shield strength counts.

        for sPart in self.__m_oShip.sGetPartList():
            fShield = max(fShield, self.__m_oShipPart.fGetShield(sPart))

        return fShield


    def fGetMaxStructure(self):
        fMaxStructure = self.__m_oShipHull.fGetStructure(self.__m_oShip.sGetHull())

        for sPart in self.__m_oShip.sGetPartList():
            fMaxStructure += self.__m_oShipPart.fGetStructure(sPart)

        return fMaxStructure


    def fGetSpeed(self):
        return self.__m_oShipHull.fGetSpeed(self.__m_oShip.sGetHull())
