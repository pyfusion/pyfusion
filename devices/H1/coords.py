"""
"""
from pyfusion.data.base import BaseCoordTransform

class MirnovKhMagneticCoordTransform(BaseCoordTransform):
    input_coords = 'cylindrical'
    output_coords = 'magnetic'

    def transform(self, coords):
        pass
