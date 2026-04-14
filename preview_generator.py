"""
3D Preview Generator Module
============================
Generate interactive 3D previews using Plotly.
"""

import plotly.graph_objects as go


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
