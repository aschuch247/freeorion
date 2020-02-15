"""
This is the global empire manager.
"""


class CEmpireManager(object):


    def __init__(self, oUniverse, oEmpireRelation, sTechnologyFrozenset):
        self.__m_oUniverse = oUniverse
        self.__m_oEmpireRelation = oEmpireRelation
        self.__m_sTechnologyFrozenset = sTechnologyFrozenset

        self.__m_sSpeciesFrozenset = frozenset(self.__tsGetSpecies())


    def sGetSpeciesFrozenset(self):
        return self.__m_sSpeciesFrozenset


    def __tsGetSpecies(self):
        """
        Return each species the empire has access to.
        """

        for oSystem in self.__m_oUniverse.toGetSystem():
            for oPlanet in oSystem.toGetPlanet():
                if (self.__m_oEmpireRelation.bIsOwnPlanet(oPlanet)):
                    if (oPlanet.bIsColony()):
                        yield oPlanet.sGetSpecies()

        SpeciesDict = {
            'SP_EXOBOT': 'PRO_EXOBOTS',
            'SP_BANFORO': 'TECH_COL_BANFORO',
            'SP_KILANDOW': 'TECH_COL_KILANDOW',
            'SP_MISIORLA': 'TECH_COL_MISIORLA'
        }

        # @todo Is it enough to own the technology or is also a corresponding 'BLD_XENORESURRECTION_LAB' required?

        for sSpecies, sTechnology in SpeciesDict.items():
            if (sTechnology in self.__m_sTechnologyFrozenset):
                yield sSpecies
