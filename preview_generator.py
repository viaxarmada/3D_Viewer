"""
3D Preview Generator Module
============================
Generate interactive 3D previews via Google's <model-viewer> web component,
embedded in a self-contained HTML document. Renders GLB/GLTF directly —
supports PBR textures, normal maps, and embedded animations. Non-GLB inputs
are converted to GLB on the fly through trimesh so they share the same
render path.

The model-viewer library is bundled locally (vendor/) and inlined into the
iframe HTML, so the preview works in environments where CDNs are blocked
(corporate firewalls, sandboxed deploys, restrictive CSPs, offline use).
"""

import base64
import os


_VENDOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vendor')
_MODEL_VIEWER_LIB_PATH = os.path.join(_VENDOR_DIR, 'model-viewer-3.5.0.umd.min.js')


def _load_model_viewer_lib():
    with open(_MODEL_VIEWER_LIB_PATH, 'r', encoding='utf-8') as f:
        return f.read()


# Read once at import time. ~910 KB — fine to keep in memory; reading on
# every preview render would be wasteful since this never changes.
_MODEL_VIEWER_LIB = _load_model_viewer_lib()


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

  <!-- Bundled @google/model-viewer 3.5.0 UMD build, BSD-3-Clause licensed.
       Inlined here so the preview works without CDN access. -->
  <script>__MV_LIB__</script>

  <script>
    (function () {
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

      // Embedded GLB payload (base64).
      const GLB_B64 = "__GLB_B64__";

      try {
        if (!customElements.get('model-viewer')) {
          throw new Error('model-viewer custom element not registered');
        }
        setStatus('Decoding model…');
        const blob = b64ToBlob(GLB_B64, 'model/gltf-binary');
        const objectUrl = URL.createObjectURL(blob);
        // Blob URL avoids the data-URL size ceiling some browsers enforce
        // on iframe contexts and is much faster for the renderer to fetch.
        mv.src = objectUrl;
        setStatus('Rendering…');
      } catch (e) {
        setStatus('Could not initialize 3D viewer: ' + (e && e.message ? e.message : e), true);
      }

      mv.addEventListener('load', () => hideStatus());
      mv.addEventListener('error', (ev) => {
        const detail = ev && ev.detail;
        const msg =
          (detail && detail.sourceError && detail.sourceError.message) ||
          (detail && detail.type) ||
          'unknown error';
        setStatus('Model failed to render: ' + msg, true);
      });
    })();
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
    Google's <model-viewer> web component, with the library inlined so
    no CDN access is required.

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
        # Replace the large payloads last so earlier small substitutions
        # don't have to scan past them.
        .replace('__MV_LIB__', _MODEL_VIEWER_LIB)
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
