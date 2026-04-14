"""
Scale Handler Module
====================
Handle scaling and unit conversion for meshes.
"""

# Unit conversion factors (to millimeters)
UNIT_CONVERSION_FACTORS = {
    'millimeters': 1.0,
    'centimeters': 10.0,
    'inches': 25.4,
    'meters': 1000.0,
    'feet': 304.8
}


def apply_scale_factor(mesh, scale_factor):
    """
    Apply scale factor to mesh.
    
    Args:
        mesh: trimesh.Trimesh object
        scale_factor: float or [x, y, z] list
        
    Returns:
        trimesh.Trimesh: The scaled mesh (modified in place)
    """
    mesh.apply_scale(scale_factor)
    return mesh


def convert_mesh_units(mesh, from_unit, to_unit='millimeters'):
    """
    Convert mesh from one unit system to another.
    
    Args:
        mesh: trimesh.Trimesh object
        from_unit: str, source unit system
        to_unit: str, target unit system (default: millimeters)
        
    Returns:
        trimesh.Trimesh: The converted mesh (modified in place)
    """
    if from_unit not in UNIT_CONVERSION_FACTORS:
        raise ValueError(f"Unknown source unit: {from_unit}")
    
    if to_unit not in UNIT_CONVERSION_FACTORS:
        raise ValueError(f"Unknown target unit: {to_unit}")
    
    # Calculate scale factor
    scale_factor = UNIT_CONVERSION_FACTORS[from_unit] / UNIT_CONVERSION_FACTORS[to_unit]
    
    # Apply scale
    mesh.apply_scale(scale_factor)
    
    return mesh


def scale_to_percentage(mesh, percentage):
    """
    Scale mesh to percentage of original size.
    
    Args:
        mesh: trimesh.Trimesh object
        percentage: float (100 = no change, 200 = double, 50 = half)
        
    Returns:
        trimesh.Trimesh: The scaled mesh
    """
    scale_factor = percentage / 100.0
    return apply_scale_factor(mesh, scale_factor)


def get_scale_factor(from_unit, to_unit='millimeters'):
    """
    Get scale factor for unit conversion.
    
    Args:
        from_unit: str, source unit
        to_unit: str, target unit (default: millimeters)
        
    Returns:
        float: Scale factor to multiply by
    """
    return UNIT_CONVERSION_FACTORS[from_unit] / UNIT_CONVERSION_FACTORS[to_unit]
