"""
3D Preview Generator Module
============================
Generate interactive 3D previews.

Primary renderer: PyVista (VTK) — supports textured PBR materials from
GLB/GLTF and OBJ+MTL.

Fallback renderer: Plotly Mesh3d — solid color only, used if PyVista
isn't available.
"""

import numpy as np
import plotly.graph_objects as go


def trimesh_to_pyvista(mesh):
    """
    Convert a trimesh.Trimesh into a (pyvista.PolyData, pyvista.Texture | None)
    pair, preserving UV coordinates and the base-color texture image when
    the source mesh carries them.

    Supports:
      - PBR materials (GLB / GLTF): material.baseColorTexture
      - SimpleMaterial (OBJ + MTL): material.image
    """
    import pyvista as pv

    # VTK face format: each face row is [n_vertices, v0, v1, v2, ...].
    # Our meshes are triangle-only (trimesh enforces this).
    n_faces = len(mesh.faces)
    faces_vtk = np.empty((n_faces, 4), dtype=np.int64)
    faces_vtk[:, 0] = 3
    faces_vtk[:, 1:] = mesh.faces

    pv_mesh = pv.PolyData(np.asarray(mesh.vertices, dtype=np.float64), faces_vtk)

    texture = None
    try:
        visual = getattr(mesh, 'visual', None)
        if visual is None:
            return pv_mesh, None

        # UV coordinates — required for any texture mapping.
        uv = getattr(visual, 'uv', None)
        if uv is None:
            return pv_mesh, None
        uv = np.asarray(uv, dtype=np.float64)
        if uv.ndim != 2 or uv.shape[1] != 2 or uv.shape[0] != len(mesh.vertices):
            return pv_mesh, None
        pv_mesh.active_texture_coordinates = uv

        # Texture image — try PBR first, then SimpleMaterial.
        material = getattr(visual, 'material', None)
        if material is None:
            return pv_mesh, None

        img = getattr(material, 'baseColorTexture', None)
        if img is None:
            img = getattr(material, 'image', None)
        if img is None:
            return pv_mesh, None

        # Normalize to RGB numpy array. PIL Image -> array; array passes through.
        if hasattr(img, 'convert'):
            img_array = np.array(img.convert('RGB'))
        else:
            img_array = np.asarray(img)
            if img_array.ndim == 2:
                img_array = np.stack([img_array] * 3, axis=-1)
            elif img_array.shape[-1] == 4:
                img_array = img_array[..., :3]

        texture = pv.Texture(img_array)
    except Exception:
        # Anything fails -> render untextured rather than break the viewer.
        texture = None

    return pv_mesh, texture


def create_pyvista_preview(mesh, window_size=(800, 550)):
    """
    Build a pyvista.Plotter for the given trimesh mesh, applying the
    embedded texture if one is present. Returns the Plotter unshown so the
    caller (e.g. stpyvista) can render it.
    """
    import pyvista as pv

    pv_mesh, texture = trimesh_to_pyvista(mesh)

    plotter = pv.Plotter(window_size=list(window_size), border=False, off_screen=True)
    plotter.background_color = 'white'

    if texture is not None:
        plotter.add_mesh(pv_mesh, texture=texture, smooth_shading=True)
    else:
        plotter.add_mesh(
            pv_mesh,
            color='lightblue',
            smooth_shading=True,
            specular=0.3,
            specular_power=15,
        )

    plotter.add_axes(interactive=False)
    plotter.view_isometric()

    return plotter


def create_3d_preview(mesh, title="3D Model Preview"):
    """
    Create interactive 3D preview of mesh using Plotly.
    
    Args:
        mesh: trimesh.Trimesh object
        title: str, plot title
        
    Returns:
        plotly.graph_objects.Figure
    """
    # Extract vertices and faces
    vertices = mesh.vertices
    faces = mesh.faces
    
    # Create mesh plot
    fig = go.Figure(data=[
        go.Mesh3d(
            # Coordinates
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            
            # Triangles (i, j, k are vertex indices)
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            
            # Styling
            color='lightblue',
            opacity=0.7,
            name='3D Model',
            
            # Shading
            flatshading=True,
            lighting=dict(
                ambient=0.5,
                diffuse=0.8,
                specular=0.2,
                roughness=0.5,
                fresnel=0.2
            ),
            lightposition=dict(
                x=100,
                y=200,
                z=0
            )
        )
    ])
    
    # Update layout
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='X (mm)',
            yaxis_title='Y (mm)',
            zaxis_title='Z (mm)',
            
            # Equal aspect ratio
            aspectmode='data',
            
            # Camera position
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1)
            ),
            
            # Background
            bgcolor='rgba(240, 240, 240, 0.9)'
        ),
        
        # Layout
        height=500,
        margin=dict(l=0, r=0, t=40, b=0),
        
        # Interactions
        hovermode='closest'
    )
    
    return fig


def create_wireframe_preview(mesh, title="Wireframe Preview"):
    """
    Create wireframe preview (edges only).
    
    Args:
        mesh: trimesh.Trimesh object
        title: str, plot title
        
    Returns:
        plotly.graph_objects.Figure
    """
    vertices = mesh.vertices
    edges = mesh.edges_unique
    
    # Create edge traces
    edge_x = []
    edge_y = []
    edge_z = []
    
    for edge in edges:
        v1, v2 = vertices[edge[0]], vertices[edge[1]]
        edge_x.extend([v1[0], v2[0], None])
        edge_y.extend([v1[1], v2[1], None])
        edge_z.extend([v1[2], v2[2], None])
    
    fig = go.Figure(data=[
        go.Scatter3d(
            x=edge_x,
            y=edge_y,
            z=edge_z,
            mode='lines',
            line=dict(color='blue', width=2),
            name='Edges'
        )
    ])
    
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='X (mm)',
            yaxis_title='Y (mm)',
            zaxis_title='Z (mm)',
            aspectmode='data'
        ),
        height=500,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig
