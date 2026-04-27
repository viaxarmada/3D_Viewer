"""
3D Preview Generator Module
============================
Generate interactive 3D previews.

Primary renderer: Google's <model-viewer> web component, embedded via
HTML. Renders GLB/GLTF directly — supports PBR textures, normal maps,
and embedded animations. Non-GLB inputs are converted to GLB on the fly
through trimesh so they share the same render path.

Legacy helpers retained for offline / non-CDN environments:
  - create_pyvista_preview / trimesh_to_pyvista (textured, server-rendered)
  - create_3d_preview / create_wireframe_preview (Plotly, flat-shaded)
"""

import base64

import numpy as np
import plotly.graph_objects as go


# ── Active renderer: Google <model-viewer> ──────────────────────────────────

# HTML template for the model-viewer embed. Uses placeholder tokens
# (rather than Python f-string interpolation) because the JS / CSS
# contains many `{` and `}` characters that would conflict with f-strings.
_MODEL_VIEWER_TEMPLATE = r"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body, html {
      margin: 0;
      padding: 0;
      height: 100%;
      background: __BG__;
      font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    }
    #wrap { position: relative; width: 100%; height: __HEIGHT__px; }
    model-viewer {
      width: 100%;
      height: __HEIGHT__px;
      background-color: __BG__;
      --poster-color: __BG__;
    }
    #status {
      position: absolute; top: 8px; left: 12px;
      background: rgba(255, 255, 255, 0.94);
      padding: 6px 10px;
      border-radius: 4px;
      font-size: 12px;
      color: #555;
      max-width: 85%;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
    }
    #status.error { color: #b00020; background: #fff3f3; }
    #status.hidden { display: none; }
    .hint {
      position: absolute; bottom: 8px; left: 12px;
      font-size: 11px; color: #888; pointer-events: none;
    }
  </style>
</head>
<body>
  <div id="wrap">
    <div id="status">Initializing 3D viewer…</div>
    <model-viewer id="mv"
      alt="3D model preview"
      camera-controls
      touch-action="pan-y"
      __AUTOPLAY__
      __AUTOROTATE__
      shadow-intensity="1"
      exposure="1.0"
      environment-image="neutral">
    </model-viewer>
    <div class="hint">drag to orbit · scroll to zoom · animations autoplay</div>
  </div>
  <script type="module">
    // Fallback chain — first CDN that successfully registers the
    // <model-viewer> custom element wins. Order: jsdelivr (most
    // reliable globally), unpkg, googleapis.
    const CDNS = [
      'https://cdn.jsdelivr.net/npm/@google/model-viewer@3.5.0/dist/model-viewer.min.js',
      'https://unpkg.com/@google/model-viewer@3.5.0/dist/model-viewer.min.js',
      'https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js'
    ];

    const statusEl = document.getElementById('status');
    const mv = document.getElementById('mv');

    function setStatus(msg, isError) {
      statusEl.textContent = msg;
      statusEl.classList.toggle('error', !!isError);
      statusEl.classList.remove('hidden');
    }
    function hideStatus() {
      statusEl.classList.add('hidden');
    }

    async function loadLibrary() {
      let lastErr = null;
      for (const url of CDNS) {
        try {
          setStatus('Loading viewer library…');
          await import(url);
          if (customElements.get('model-viewer')) {
            return url;
          }
          lastErr = new Error('Loaded but custom element not registered');
        } catch (e) {
          lastErr = e;
          // eslint-disable-next-line no-console
          console.warn('[model-viewer] CDN failed:', url, e);
        }
      }
      throw lastErr || new Error('All CDNs failed.');
    }

    function b64ToBlob(b64, mime) {
      // Decode in chunks so very large GLBs don't blow the call stack.
      const CHUNK = 0x8000;
      const bin = atob(b64);
      const len = bin.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i += CHUNK) {
        const end = Math.min(i + CHUNK, len);
        for (let j = i; j < end; j++) bytes[j] = bin.charCodeAt(j);
      }
      return new Blob([bytes], { type: mime });
    }

    // Embedded GLB payload (base64). Inlined here so the iframe is
    // fully self-contained — no second network round-trip.
    const GLB_B64 = "__GLB_B64__";

    (async () => {
      try {
        const cdn = await loadLibrary();
        setStatus('Decoding model…');
        const blob = b64ToBlob(GLB_B64, 'model/gltf-binary');
        const objectUrl = URL.createObjectURL(blob);
        // Switching to a blob URL avoids the 2–4 MB data-URL ceiling
        // some browsers enforce on iframe contexts and is much faster
        // for the renderer to fetch.
        mv.src = objectUrl;
        setStatus('Rendering…');
      } catch (e) {
        setStatus('Could not load 3D viewer: ' + (e && e.message ? e.message : e), true);
      }
    })();

    mv.addEventListener('load', () => hideStatus());
    mv.addEventListener('error', (ev) => {
      const detail = ev && ev.detail;
      const msg =
        (detail && detail.sourceError && detail.sourceError.message) ||
        (detail && detail.type) ||
        'unknown error';
      setStatus('Model failed to render: ' + msg, true);
    });
  </script>
</body>
</html>
"""


def create_model_viewer_html(
    glb_bytes,
    height=550,
    autoplay=True,
    auto_rotate=False,
    background='#0f0f0f',
):
    """
    Build a self-contained HTML document that renders GLB bytes via
    Google's <model-viewer> web component.

    Robustness features:
      - Multi-CDN fallback chain (jsdelivr → unpkg → googleapis).
      - Blob URL src (avoids the data-URL size ceiling and parses faster
        than base64 for the renderer).
      - Status overlay that surfaces library-load and model-load errors
        in the iframe so failures are diagnosable instead of silent.
      - load / error event listeners that hide the overlay on success
        and show the actual model-viewer error message on failure.

    Capabilities:
      - PBR textures (baseColor, metallic-roughness, normal, emissive,
        occlusion).
      - Embedded GLB animations autoplay.
      - Mouse orbit + scroll zoom + pinch on touch.

    Args:
        glb_bytes: bytes of a valid GLB file.
        height: int, viewer height in CSS pixels.
        autoplay: bool, autoplay embedded animations.
        auto_rotate: bool, slowly rotate the camera. Default off — when
            there is an embedded animation, auto-rotate fights with it.
        background: CSS color string for the viewer backdrop.

    Returns:
        str: a self-contained HTML document suitable for
        streamlit.components.v1.html().
    """
    b64 = base64.b64encode(glb_bytes).decode('ascii')
    autoplay_attr = 'autoplay' if autoplay else ''
    auto_rotate_attr = 'auto-rotate auto-rotate-delay="2000"' if auto_rotate else ''

    return (
        _MODEL_VIEWER_TEMPLATE
        .replace('__HEIGHT__', str(int(height)))
        .replace('__BG__', background)
        .replace('__AUTOPLAY__', autoplay_attr)
        .replace('__AUTOROTATE__', auto_rotate_attr)
        # Replace the (huge) base64 payload last so the previous small
        # substitutions are cheap.
        .replace('__GLB_B64__', b64)
    )


def trimesh_to_glb_bytes(mesh):
    """
    Export a trimesh mesh (or scene) to GLB bytes for use with
    <model-viewer>. Embeds textures present on the mesh's visual; cannot
    embed animations (those exist at the scene level and are stripped
    upstream by mesh_loader.dump(concatenate=True)).

    Args:
        mesh: trimesh.Trimesh or trimesh.Scene.

    Returns:
        bytes: a valid GLB binary.
    """
    return mesh.export(file_type='glb')


# ── Legacy helpers (not called from the active preview path) ────────────────


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
