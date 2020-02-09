"""
This is a representation of a system.
"""


class CSystem(object):


    def __init__(self, fX, fY):
        self.__m_fX = fX
        self.__m_fY = fY

    def fGetX(self):
        return self.__m_fX

    def fGetY(self):
        return self.__m_fY
