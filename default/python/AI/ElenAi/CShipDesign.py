"""
This is a representation of a ship design.
"""


class CShipDesign(object):


    def __init__(self, oDataRepository, sHull, sPartList):
        self.__m_sPartList = sPartList

        self.__m_oShipHull = oDataRepository.oGetShipHullData().oGetShipHull(sHull)
        self.__m_oShipPartData = oDataRepository.oGetShipPartData()


    def bIsArmed(self):
        for sPart in self.__m_sPartList:
            if (self.__m_oShipPartData.oGetShipPart(sPart).fGetDamage() > 0.0):
                return True

        return False


    def fGetDamage(self):
        fDamage = 0.0

        for sPart in self.__m_sPartList:
            fDamage += self.__m_oShipPartData.oGetShipPart(sPart).fGetDamage()

        return fDamage


    def fGetDetection(self):
        fDetection = 0.0

        # Only the ship part with the highest detection range counts.

        for sPart in self.__m_sPartList:
            fDetection = max(fDetection, self.__m_oShipPartData.oGetShipPart(sPart).fGetDetection())

        # Combine the highest detection range ship part and the ship hull detection range.

        return self.__m_oShipHull.fGetDetection() + fDetection


    def fGetShield(self):
        fShield = 0.0

        # Only the ship part with the highest shield strength counts.

        for sPart in self.__m_sPartList:
            fShield = max(fShield, self.__m_oShipPartData.oGetShipPart(sPart).fGetShield())

        return fShield


    def fGetStealth(self):
        """
        Get the stealth strength of the ship.
        """

        fStealth = 0.0

        # Only the ship part with the highest stealth strength counts.

        for sPart in self.__m_sPartList:
            fStealth = max(fStealth, self.__m_oShipPartData.oGetShipPart(sPart).fGetStealth())

        # Combine the highest stealth strength ship part and the ship hull stealth strength.

        return self.__m_oShipHull.fGetStealth() + fStealth


    def fGetMaxStructure(self):
        fMaxStructure = self.__m_oShipHull.fGetStructure()

        for sPart in self.__m_sPartList:
            fMaxStructure += self.__m_oShipPartData.oGetShipPart(sPart).fGetStructure()

        return fMaxStructure


    def fGetSpeed(self):
        fSpeed = 0.0

        # Only the ship part with the highest speed counts.

        for sPart in self.__m_sPartList:
            fSpeed = max(fSpeed, self.__m_oShipPartData.oGetShipPart(sPart).fGetSpeed())

        # Combine the highest speed ship part and the ship hull speed.

        return self.__m_oShipHull.fGetSpeed() + fSpeed