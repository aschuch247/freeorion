"""
This is a ship part data provider (with dynamic data).
"""

from ElenAi.CShipPart import CShipPart


class CShipPartDataDynamic(object):


    def __init__(self, fo):
        self.__m_fo = fo


    def oGetShipPart(self, sName):
        oFoShipPart = self.__m_fo.getShipPart(sName)

        return CShipPart(
            oFoShipPart.name,
            self.__fGetDamage(oFoShipPart),
            self.__fGetDetection(oFoShipPart),
            self.__fGetShield(oFoShipPart),
            self.__fGetSpeed(oFoShipPart),
            self.__fGetStealth(oFoShipPart),
            self.__fGetStructure(oFoShipPart)
        )


    def __fGetDamage(self, oFoShipPart):
        if (oFoShipPart.partClass != self.__m_fo.shipPartClass.shortRange):
            return 0.0

        # This is the product of number of shots times damage per shot.

        return oFoShipPart.secondaryStat * oFoShipPart.capacity


    def __fGetDetection(self, oFoShipPart):
        if (oFoShipPart.partClass != self.__m_fo.shipPartClass.detection):
            return 0.0

        return oFoShipPart.capacity


    def __fGetShield(self, oFoShipPart):
        if (oFoShipPart.partClass != self.__m_fo.shipPartClass.shields):
            return 0.0

        return oFoShipPart.capacity


    def __fGetSpeed(self, oFoShipPart):
        if (oFoShipPart.partClass != self.__m_fo.shipPartClass.speed):
            return 0.0

        return oFoShipPart.capacity


    def __fGetStealth(self, oFoShipPart):
        """
        Get the stealth strength of the ship part.
        """

        if (oFoShipPart.partClass != self.__m_fo.shipPartClass.stealth):
            return 0.0

        return oFoShipPart.capacity


    def __fGetStructure(self, oFoShipPart):
        if (oFoShipPart.partClass != self.__m_fo.shipPartClass.armour):
            return 0.0

        return oFoShipPart.capacity
