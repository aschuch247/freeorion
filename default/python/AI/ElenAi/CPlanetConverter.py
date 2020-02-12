"""
This is a factory to convert a FreeOrion planet representation to an abstract representation.
"""

from freeOrionAIInterface import meterType

from ElenAi.CPlanet import CPlanet


class CPlanetConverter(object):


    def __init__(self, oFoUniverse, oFoPlanet):
        self.__m_oFoUniverse = oFoUniverse
        self.__m_oFoPlanet = oFoPlanet


    def __tsGetBuilding(self):
        for ixBuilding in self.__m_oFoPlanet.buildingIDs:
            yield self.__m_oFoUniverse.getBuilding(ixBuilding).buildingTypeName


    def oGetPlanet(self):
        return CPlanet(
            self.__m_oFoPlanet.id,
            self.__m_oFoPlanet.owner,
            self.__m_oFoPlanet.type,
            self.__m_oFoPlanet.habitableSize,
            self.__m_oFoPlanet.speciesName,
            self.__m_oFoPlanet.currentMeterValue(meterType.population),
            self.__m_oFoPlanet.specials,
            frozenset(self.__tsGetBuilding())
        )
