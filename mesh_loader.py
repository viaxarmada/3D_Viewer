"""
Mesh Loader Module
==================
Load 3D model files in various formats using trimesh.
"""

import trimesh
import tempfile
import os


def load_3d_model(uploaded_file):
    """
    Load 3D model from uploaded file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        dict: {
            'success': bool,
            'mesh': trimesh object (if success),
            'format': str (file format),
            'file_size': int (bytes),
            'error': str (if not success)
        }
    """
    try:
        # Validate file size
        MAX_SIZE = 50 * 1024 * 1024  # 50 MB
        file_bytes = uploaded_file.getvalue()
        file_size = len(file_bytes)
        
        if file_size > MAX_SIZE:
            return {
                'success': False,
                'error': f"File too large: {file_size/(1024*1024):.1f} MB. Maximum is 50 MB."
            }
        
        # Get file extension
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        format_name = file_ext.replace('.', '').upper()
        
        # Validate format
        valid_formats = ['.stl', '.3mf', '.obj', '.glb', '.gltf']
        if file_ext not in valid_formats:
            return {
                'success': False,
                'error': f"Unsupported format: {format_name}. Use STL, 3MF, OBJ, GLB, or GLTF."
            }
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(file_bytes)
            tmp.flush()  # Ensure write is complete
            tmp_path = tmp.name
        
        try:
            # Load mesh using trimesh
            mesh = trimesh.load(tmp_path)
            
            # Handle GLB/GLTF scenes (may contain multiple objects)
            if file_ext in ['.glb', '.gltf'] and isinstance(mesh, trimesh.Scene):
                # Combine all meshes in the scene
                mesh = mesh.dump(concatenate=True)
            
            # Validate that mesh has geometry
            if not hasattr(mesh, 'vertices') or len(mesh.vertices) == 0:
                return {
                    'success': False,
                    'error': "File contains no geometry. Please check the 3D model."
                }
            
            # Handle 3MF unit conversion
            if file_ext == '.3mf' and hasattr(mesh, 'metadata'):
                units = mesh.metadata.get('units', 'millimeter')
                
                # Convert to millimeters if needed
                if units == 'inch':
                    mesh.apply_scale(25.4)
                elif units == 'centimeter':
                    mesh.apply_scale(10.0)
                elif units == 'meter':
                    mesh.apply_scale(1000.0)
            
            return {
                'success': True,
                'mesh': mesh,
                'format': format_name,
                'file_size': file_size
            }
            
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
                
    except Exception as e:
        return {
            'success': False,
            'error': f"Error loading file: {str(e)}"
        }
