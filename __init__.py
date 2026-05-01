"""
Core modules for 3D Volume Calculator
"""

from .mesh_loader import load_3d_model
from .volume_calculator import calculate_volume_and_dimensions
from .preview_generator import (
    create_model_viewer_html,
    trimesh_to_glb_bytes,
)
from .scale_handler_enhanced import (
    apply_scale_factor,
    apply_non_uniform_scale,
    apply_dimensional_scale,
    calculate_proportional_dimension,
    convert_mesh_units,
    UNIT_CONVERSION_FACTORS,
)

__all__ = [
    'load_3d_model',
    'calculate_volume_and_dimensions',
    'create_model_viewer_html',
    'trimesh_to_glb_bytes',
    'apply_scale_factor',
    'apply_non_uniform_scale',
    'apply_dimensional_scale',
    'calculate_proportional_dimension',
    'convert_mesh_units',
    'UNIT_CONVERSION_FACTORS',
]
