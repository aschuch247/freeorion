"""
This class represents a system.
"""


class CSystem(object):
    def __init__(self, fX, fY):
        self.m_fX = fX
        self.m_fY = fY

    def fGetX(self):
        return self.m_fX

    def fGetY(self):
        return self.m_fY
