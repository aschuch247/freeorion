"""
This is a species data provider (with dynamic data).
"""

from ElenAi.Constant.CPlanetType import CPlanetType
from ElenAi.CSpecies import CSpecies


class CSpeciesDataDynamic(object):


    def __init__(self, fo):
        self.__m_fo = fo


    def oGetSpecies(self, sName):
        oFoSpecies = self.__m_fo.getSpecies(sName)

        dictPlanetTypePlanetEnvironment = {
            CPlanetType.swamp:     oFoSpecies.getPlanetEnvironment(self.__m_fo.planetType.swamp),
            CPlanetType.toxic:     oFoSpecies.getPlanetEnvironment(self.__m_fo.planetType.toxic),
            CPlanetType.inferno:   oFoSpecies.getPlanetEnvironment(self.__m_fo.planetType.inferno),
            CPlanetType.radiated:  oFoSpecies.getPlanetEnvironment(self.__m_fo.planetType.radiated),
            CPlanetType.barren:    oFoSpecies.getPlanetEnvironment(self.__m_fo.planetType.barren),
            CPlanetType.tundra:    oFoSpecies.getPlanetEnvironment(self.__m_fo.planetType.tundra),
            CPlanetType.desert:    oFoSpecies.getPlanetEnvironment(self.__m_fo.planetType.desert),
            CPlanetType.terran:    oFoSpecies.getPlanetEnvironment(self.__m_fo.planetType.terran),
            CPlanetType.ocean:     oFoSpecies.getPlanetEnvironment(self.__m_fo.planetType.ocean),
            CPlanetType.asteroids: oFoSpecies.getPlanetEnvironment(self.__m_fo.planetType.asteroids),
            CPlanetType.gasGiant:  oFoSpecies.getPlanetEnvironment(self.__m_fo.planetType.gasGiant)
        }

        return CSpecies(
            oFoSpecies.name,
            dictPlanetTypePlanetEnvironment,
            oFoSpecies.tags,
            oFoSpecies.homeworlds
        )
