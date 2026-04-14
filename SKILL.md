# 3D Model Import Specialist - Skill Guide

## Purpose
This skill provides proven code templates, error solutions, and best practices for implementing 3D model file import with volume calculation using the trimesh library.

## Supported Formats
- **STL** (Binary & ASCII) - Universal 3D printing standard
- **3MF** (ZIP-based) - Modern format with units metadata
- **OBJ** (Wavefront) - Common interchange format
- **GLB** (Binary glTF) - Modern web 3D standard
- **GLTF** (JSON glTF) - "JPEG of 3D", web-friendly

## Core Library: trimesh

### Installation
```bash
pip install trimesh networkx
```

### Basic Usage Pattern
```python
import trimesh
import tempfile
import os

# 1. Save uploaded file to temp location
with tempfile.NamedTemporaryFile(delete=False, suffix='.stl') as tmp:
    tmp.write(uploaded_file.getvalue())
    tmp.flush()
    tmp_path = tmp.name

try:
    # 2. Load mesh
    mesh = trimesh.load(tmp_path)
    
    # 3. Calculate volume
    volume_mm3 = abs(mesh.volume)
    
    # 4. Get dimensions
    bounds = mesh.bounds
    length = bounds[1][0] - bounds[0][0]
    
finally:
    # 5. Cleanup
    os.unlink(tmp_path)
```

## Quick Reference

### Volume Calculation
```python
volume = mesh.volume              # Raw volume
volume_mm3 = abs(mesh.volume)    # Absolute (handle inverted normals)
```

### Dimensions
```python
bounds = mesh.bounds
# Returns: [[xmin, ymin, zmin], [xmax, ymax, zmax]]

length = bounds[1][0] - bounds[0][0]
width = bounds[1][1] - bounds[0][1]
height = bounds[1][2] - bounds[0][2]
```

### Quality Checks
```python
is_watertight = mesh.is_watertight    # True if closed, no holes
triangle_count = len(mesh.faces)
vertex_count = len(mesh.vertices)
```

### Scaling
```python
mesh.apply_scale(2.0)           # Uniform scale 2x
mesh.apply_scale([2, 1, 1])     # Scale X by 2, Y and Z unchanged
mesh.apply_scale(25.4)          # Convert inches to mm
```

## Format-Specific Handling

### STL (Binary & ASCII)
```python
# Automatic detection
mesh = trimesh.load('file.stl')

# No units metadata - assume mm
# No color/material info
```

### 3MF (ZIP-based with units)
```python
mesh = trimesh.load('file.3mf')

# Check units metadata
units = mesh.metadata.get('units', 'millimeter')

# Convert to mm if needed
if units == 'inch':
    mesh.apply_scale(25.4)
elif units == 'centimeter':
    mesh.apply_scale(10.0)
elif units == 'meter':
    mesh.apply_scale(1000.0)
```

### OBJ (Wavefront)
```python
mesh = trimesh.load('file.obj')

# May reference .mtl file for materials (auto-loaded if present)
# Usually in arbitrary units
```

### GLB/GLTF (Scene handling)
```python
mesh = trimesh.load('file.glb')  # or .gltf

# GLB/GLTF may contain scenes with multiple objects
if isinstance(mesh, trimesh.Scene):
    # Combine all meshes into one
    mesh = mesh.dump(concatenate=True)

# Extract materials (optional)
if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'material'):
    color = mesh.visual.material.baseColorFactor  # RGBA
```

## Common Errors & Solutions

### Error: "Mesh is empty"
**Cause:** File has no geometry
**Solution:**
```python
if len(mesh.vertices) == 0:
    raise ValueError("File contains no geometry")
```

### Error: Negative volume
**Cause:** Inconsistent face normals
**Solution:**
```python
volume = abs(mesh.volume)  # Always use absolute value
```

### Error: File not found (race condition)
**Cause:** Temp file cleanup before load
**Solution:**
```python
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
    tmp.write(uploaded_file.getvalue())
    tmp.flush()  # Force write to disk
    tmp_path = tmp.name
```

### Error: Large file timeout
**Cause:** File too large
**Solution:**
```python
MAX_SIZE = 50 * 1024 * 1024  # 50 MB
if len(uploaded_file.getvalue()) > MAX_SIZE:
    raise ValueError("File too large. Max 50 MB.")
```

### Error: Invalid format
**Cause:** Corrupted or unsupported file
**Solution:**
```python
try:
    mesh = trimesh.load(tmp_path)
except Exception as e:
    raise ValueError(f"Cannot read file: {str(e)}")
```

## Complete Working Template

```python
def process_3d_model(uploaded_file):
    """
    Process uploaded 3D model and extract volume/dimensions.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        dict: {
            'volume_mm3': float,
            'length_mm': float,
            'width_mm': float,
            'height_mm': float,
            'is_watertight': bool,
            'triangles': int,
            'vertices': int,
            'filename': str,
            'format': str,
            'mesh': trimesh object (for preview)
        }
    """
    import trimesh
    import tempfile
    import os
    
    # Validate file size
    MAX_SIZE = 50 * 1024 * 1024  # 50 MB
    file_size = len(uploaded_file.getvalue())
    if file_size > MAX_SIZE:
        raise ValueError(f"File too large: {file_size/(1024*1024):.1f} MB. Max 50 MB.")
    
    # Get file extension
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp.flush()
        tmp_path = tmp.name
    
    try:
        # Load mesh
        mesh = trimesh.load(tmp_path)
        
        # Handle GLB/GLTF scenes
        if file_ext in ['.glb', '.gltf'] and isinstance(mesh, trimesh.Scene):
            mesh = mesh.dump(concatenate=True)
        
        # Validate geometry
        if len(mesh.vertices) == 0:
            raise ValueError("File contains no geometry")
        
        # Handle 3MF units
        if file_ext == '.3mf':
            units = mesh.metadata.get('units', 'millimeter')
            if units == 'inch':
                mesh.apply_scale(25.4)
            elif units == 'centimeter':
                mesh.apply_scale(10.0)
            elif units == 'meter':
                mesh.apply_scale(1000.0)
        
        # Calculate volume (absolute value for inverted normals)
        volume_mm3 = abs(mesh.volume)
        
        # Get dimensions
        bounds = mesh.bounds
        dims = bounds[1] - bounds[0]
        
        # Return results
        return {
            'volume_mm3': volume_mm3,
            'length_mm': dims[0],
            'width_mm': dims[1],
            'height_mm': dims[2],
            'is_watertight': mesh.is_watertight,
            'triangles': len(mesh.faces),
            'vertices': len(mesh.vertices),
            'filename': uploaded_file.name,
            'format': file_ext.upper().replace('.', ''),
            'mesh': mesh
        }
        
    except Exception as e:
        raise ValueError(f"Error processing 3D model: {str(e)}")
        
    finally:
        # Cleanup temp file
        try:
            os.unlink(tmp_path)
        except:
            pass
```

## 3D Preview Template (Plotly)

```python
def create_3d_preview(mesh):
    """Create interactive 3D preview with Plotly"""
    import plotly.graph_objects as go
    
    vertices = mesh.vertices
    faces = mesh.faces
    
    fig = go.Figure(data=[
        go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            color='lightblue',
            opacity=0.7,
            name='3D Model',
            flatshading=True,
            lighting=dict(
                ambient=0.5,
                diffuse=0.8,
                specular=0.2,
                roughness=0.5
            )
        )
    ])
    
    fig.update_layout(
        scene=dict(
            xaxis_title='X (mm)',
            yaxis_title='Y (mm)',
            zaxis_title='Z (mm)',
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        title="3D Model Preview",
        height=500,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig
```

## Scale/Resize Template

```python
def apply_scale(mesh, scale_factor):
    """
    Apply scale to mesh.
    
    Args:
        mesh: trimesh object
        scale_factor: float or [x, y, z] list
        
    Returns:
        trimesh: scaled mesh (original is modified in place)
    """
    mesh.apply_scale(scale_factor)
    return mesh

# Unit conversions
UNIT_SCALES = {
    'millimeters': 1.0,
    'centimeters': 10.0,
    'inches': 25.4,
    'meters': 1000.0
}

def convert_units(mesh, from_unit, to_unit='millimeters'):
    """Convert mesh from one unit to another"""
    scale = UNIT_SCALES[from_unit] / UNIT_SCALES[to_unit]
    mesh.apply_scale(scale)
    return mesh
```

## Validation Checklist

Before deploying, verify:

- [ ] File upload accepts all 5 formats
- [ ] Volume calculation works for simple cube (10mm = 1000mm³)
- [ ] Dimensions extracted correctly
- [ ] Watertight check works
- [ ] GLB/GLTF scene handling works
- [ ] 3MF unit conversion works
- [ ] Scale controls work
- [ ] Preview displays correctly
- [ ] Error messages are helpful
- [ ] Temp files cleaned up

## Best Practices

1. **Always use absolute value** for volume (handles inverted normals)
2. **Always cleanup temp files** (use try/finally)
3. **Validate file size** before processing (prevent timeout)
4. **Check for empty geometry** after loading
5. **Handle scenes** for GLB/GLTF (multiple objects)
6. **Convert units** for 3MF (has metadata)
7. **Use flush()** when writing temp files (prevent race conditions)
8. **Provide helpful errors** (don't just say "failed")

## Performance Tips

- Files >10MB may take 5-10 seconds to load
- Complex meshes (>100k triangles) may slow preview
- Use `mesh.simplify_quadric_decimation()` for large meshes
- Consider showing progress spinner for large files

## See Also

- `library_reference.md` - Complete trimesh API
- `error_patterns.md` - Full error catalog
- `code_templates.md` - More templates
- `examples/` - Working code examples
