"""
This is a representation of a ship design.
"""

from ElenAi.CShipPart import CShipPart


class CShipDesign(object):


    def __init__(self, oDataRepository, sHull, sPartList):
        self.__m_sPartList = sPartList

        self.__m_oShipHullData = oDataRepository.oGetShipHullData().oGetShipHull(sHull)
        self.__m_oShipPart = CShipPart()


    def bIsArmed(self):
        for sPart in self.__m_sPartList:
            if (self.__m_oShipPart.fGetDamage(sPart) > 0.0):
                return True

        return False


    def fGetDamage(self):
        fDamage = 0.0

        for sPart in self.__m_sPartList:
            fDamage += self.__m_oShipPart.fGetDamage(sPart)

        return fDamage


    def fGetDetection(self):
        fDetection = 0.0

        # Only the ship part with the highest detection range counts.

        for sPart in self.__m_sPartList:
            fDetection = max(fDetection, self.__m_oShipPart.fGetDetection(sPart))

        # Combine the highest detection range ship part and the ship hull detection range.

        return self.__m_oShipHullData.fGetDetection() + fDetection


    def fGetShield(self):
        fShield = 0.0

        # Only the ship part with the highest shield strength counts.

        for sPart in self.__m_sPartList:
            fShield = max(fShield, self.__m_oShipPart.fGetShield(sPart))

        return fShield


    def fGetStealth(self):
        """
        Get the stealth strength of the ship.
        """

        fStealth = 0.0

        # Only the ship part with the highest stealth strength counts.

        for sPart in self.__m_sPartList:
            fStealth = max(fStealth, self.__m_oShipPart.fGetStealth(sPart))

        # Combine the highest stealth strength ship part and the ship hull stealth strength.

        return self.__m_oShipHullData.fGetStealth() + fStealth


    def fGetMaxStructure(self):
        fMaxStructure = self.__m_oShipHullData.fGetStructure()

        for sPart in self.__m_sPartList:
            fMaxStructure += self.__m_oShipPart.fGetStructure(sPart)

        return fMaxStructure


    def fGetSpeed(self):
        fSpeed = 0.0

        # Only the ship part with the highest speed counts.

        for sPart in self.__m_sPartList:
            fSpeed = max(fSpeed, self.__m_oShipPart.fGetSpeed(sPart))

        # Combine the highest speed ship part and the ship hull speed.

        return self.__m_oShipHullData.fGetSpeed() + fSpeed
