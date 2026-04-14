"""
Scale Handler Module - Enhanced
================================
Handle scaling, unit conversion, and dimensional editing for meshes.
Supports both uniform and non-uniform (distortion) scaling.
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
    Apply uniform scale factor to mesh.
    
    Args:
        mesh: trimesh.Trimesh object
        scale_factor: float or [x, y, z] list
        
    Returns:
        trimesh.Trimesh: The scaled mesh (modified in place)
    """
    mesh.apply_scale(scale_factor)
    return mesh


def apply_non_uniform_scale(mesh, x_scale, y_scale, z_scale):
    """
    Apply non-uniform scaling (distortion) to mesh.
    
    Args:
        mesh: trimesh.Trimesh object
        x_scale: float, scale factor for X axis
        y_scale: float, scale factor for Y axis
        z_scale: float, scale factor for Z axis
        
    Returns:
        trimesh.Trimesh: The scaled mesh (modified in place)
    """
    mesh.apply_scale([x_scale, y_scale, z_scale])
    return mesh


def calculate_scale_from_dimensions(current_dims, target_dims, proportional=True):
    """
    Calculate scale factors needed to achieve target dimensions.
    
    Args:
        current_dims: dict with 'length', 'width', 'height' (current mm)
        target_dims: dict with 'length', 'width', 'height' (target mm)
        proportional: bool, if True use uniform scaling
        
    Returns:
        dict: {'x_scale': float, 'y_scale': float, 'z_scale': float}
    """
    # Calculate individual scale factors
    x_scale = target_dims['length'] / current_dims['length'] if current_dims['length'] > 0 else 1.0
    y_scale = target_dims['width'] / current_dims['width'] if current_dims['width'] > 0 else 1.0
    z_scale = target_dims['height'] / current_dims['height'] if current_dims['height'] > 0 else 1.0
    
    if proportional:
        # Use average scale factor for all dimensions
        avg_scale = (x_scale + y_scale + z_scale) / 3.0
        return {
            'x_scale': avg_scale,
            'y_scale': avg_scale,
            'z_scale': avg_scale
        }
    else:
        # Use individual scale factors (allows distortion)
        return {
            'x_scale': x_scale,
            'y_scale': y_scale,
            'z_scale': z_scale
        }


def apply_dimensional_scale(mesh, current_dims, target_dims, proportional=True):
    """
    Scale mesh to achieve specific target dimensions.
    
    Args:
        mesh: trimesh.Trimesh object
        current_dims: dict with 'length', 'width', 'height'
        target_dims: dict with 'length', 'width', 'height'
        proportional: bool, maintain proportions if True
        
    Returns:
        trimesh.Trimesh: The scaled mesh
        dict: Scale factors applied {'x_scale', 'y_scale', 'z_scale'}
    """
    # Calculate scale factors
    scales = calculate_scale_from_dimensions(current_dims, target_dims, proportional)
    
    # Apply non-uniform scale
    mesh.apply_scale([scales['x_scale'], scales['y_scale'], scales['z_scale']])
    
    return mesh, scales


def calculate_proportional_dimension(changed_dim_value, changed_dim_original, target_dim_original):
    """
    Calculate proportional dimension when one dimension changes.
    
    Args:
        changed_dim_value: New value for the changed dimension
        changed_dim_original: Original value of changed dimension
        target_dim_original: Original value of dimension to calculate
        
    Returns:
        float: Proportionally scaled target dimension
    """
    if changed_dim_original == 0:
        return target_dim_original
    
    scale_factor = changed_dim_value / changed_dim_original
    return target_dim_original * scale_factor


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
