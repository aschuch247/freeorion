"""
This is an adapter to convert a FreeOrion fleet representation to an independent representation.
"""

from ElenAi.CFleet import CFleet


class CFleetAdapter(object):


    def __init__(self, oFoFleet):
        self.__m_oFoFleet = oFoFleet


    def oGetFleet(self):
        return CFleet(
            self.__m_oFoFleet.id,
            self.__m_oFoFleet.owner
        )
