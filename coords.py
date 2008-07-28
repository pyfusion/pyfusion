from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import synonym

import pyfusion


class Coordinates(pyfusion.Base):
    __tablename__ = "coords"
    id = Column('id', Integer, primary_key=True)
    coord_system = Column('coord_system', String(50))
    __mapper_args__ = {'polymorphic_on':coord_system}
    A = Column('A', Float)
    B = Column('B', Float)
    C = Column('C', Float)
    def transform(self,func):
        """
        transform coordinate systems.
        should this just return values? or a new Coordinates object with different coord_system?
        """
        raise NotImplementedError
    

class ToroidalCoordinates(Coordinates):
    __tablename__ = 'coords_toroidal'
    __mapper_args__ = {'polymorphic_identity':'toroidal'}
    id = Column('id', Integer, ForeignKey('coords.id'), primary_key=True)
    def _get_attr_A(self):
        return self.A
    def _set_attr_A(self, attr):
        self.A = attr
    def _get_attr_B(self):
        return self.B
    def _set_attr_B(self, attr):
        self.B = attr
    def _get_attr_C(self):
        return self.C
    def _set_attr_C(self, attr):
        self.C = attr
    r = synonym('A', descriptor=property(_get_attr_A, _set_attr_A))
    phi = synonym('B', descriptor=property(_get_attr_B, _set_attr_B))
    theta = synonym('C', descriptor=property(_get_attr_C, _set_attr_C))

class CylindricalCoordinates(Coordinates):
    __tablename__ = 'coords_cylindrical'
    __mapper_args__ = {'polymorphic_identity':'cylindrical'}
    id = Column('id', Integer, ForeignKey('coords.id'), primary_key=True)
    def _get_attr_A(self):
        return self.A
    def _set_attr_A(self, attr):
        self.A = attr
    def _get_attr_B(self):
        return self.B
    def _set_attr_B(self, attr):
        self.B = attr
    def _get_attr_C(self):
        return self.C
    def _set_attr_C(self, attr):
        self.C = attr
    r = synonym('A', descriptor=property(_get_attr_A, _set_attr_A))
    phi = synonym('B', descriptor=property(_get_attr_B, _set_attr_B))
    z = synonym('C', descriptor=property(_get_attr_C, _set_attr_C))

