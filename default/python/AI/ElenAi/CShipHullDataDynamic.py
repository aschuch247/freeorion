"""
This is a ship hull data provider (with dynamic data).
"""

from ElenAi.CShipHull import CShipHull


class CShipHullDataDynamic(object):


    def __init__(self, fo):
        self.__m_fo = fo


    def oGetShipHull(self, sName):
        oFoShipHull = self.__m_fo.getShipHull(sName)

        return CShipHull(
            oFoShipHull.name,
            oFoShipHull.fuel,
            oFoShipHull.speed,
            oFoShipHull.stealth,
            oFoShipHull.structure
        )
