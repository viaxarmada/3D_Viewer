"""
Volume Calculator Module
========================
Calculate volume and dimensions from trimesh objects.
"""


def calculate_volume_and_dimensions(mesh):
    """
    Calculate volume and dimensions from a trimesh mesh.
    
    Args:
        mesh: trimesh.Trimesh object
        
    Returns:
        dict: {
            'volume_mm3': float (cubic millimeters),
            'length_mm': float,
            'width_mm': float,
            'height_mm': float,
            'is_watertight': bool,
            'triangles': int,
            'vertices': int
        }
    """
    # Calculate volume (use absolute value to handle inverted normals)
    volume_mm3 = abs(mesh.volume)
    
    # Get bounding box
    bounds = mesh.bounds
    # bounds format: [[xmin, ymin, zmin], [xmax, ymax, zmax]]
    
    # Calculate dimensions
    dimensions = bounds[1] - bounds[0]  # [length, width, height]
    
    length_mm = float(dimensions[0])
    width_mm = float(dimensions[1])
    height_mm = float(dimensions[2])
    
    # Check if mesh is watertight (closed, no holes)
    is_watertight = mesh.is_watertight
    
    # Get mesh statistics
    triangle_count = len(mesh.faces)
    vertex_count = len(mesh.vertices)
    
    return {
        'volume_mm3': volume_mm3,
        'length_mm': length_mm,
        'width_mm': width_mm,
        'height_mm': height_mm,
        'is_watertight': is_watertight,
        'triangles': triangle_count,
        'vertices': vertex_count
    }


def convert_volume(volume_mm3, to_unit='cubic_cm'):
    """
    Convert volume from mm³ to other units.
    
    Args:
        volume_mm3: Volume in cubic millimeters
        to_unit: Target unit ('cubic_cm', 'cubic_inches', 'cubic_meters', 'liters')
        
    Returns:
        float: Converted volume
    """
    conversions = {
        'cubic_mm': 1.0,
        'cubic_cm': 0.001,
        'cubic_inches': 0.0000610237,
        'cubic_meters': 1e-9,
        'liters': 0.000001,
        'milliliters': 0.001
    }
    
    if to_unit not in conversions:
        raise ValueError(f"Unknown unit: {to_unit}")
    
    return volume_mm3 * conversions[to_unit]
