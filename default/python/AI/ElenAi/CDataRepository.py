"""
This is a data repository.
"""


class CDataRepository(object):


    def __init__(self, oShipHullData):
        self.__m_oShipHullData = oShipHullData


    def oGetShipHullData(self):
        return self.__m_oShipHullData
