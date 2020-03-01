"""
This is an adapter to convert a FreeOrion system representation to an independent representation.
"""

from ElenAi.CSystem import CSystem


class CSystemAdapter(object):


    def __init__(self, oFoSystem):
        self.__m_oFoSystem = oFoSystem


    def oGetSystem(self):
        return CSystem(
            self.__m_oFoSystem.id,
            self.__m_oFoSystem.x,
            self.__m_oFoSystem.y,
            self.__m_oFoSystem.starType
        )
