"""
3D Volume Calculator - Standalone Application
==============================================

Calculate volume and dimensions from 3D model files.
Supports: STL, 3MF, OBJ, GLB, GLTF

Export results to DVA (Design Volume Analyzer) or use standalone.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import sys
import os
import copy

# Add current directory to Python path (fix for Streamlit Cloud)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try importing from `core` package first (when checked out as a submodule
# inside DVA), fall back to flat directory layout (Streamlit Cloud).
try:
    from core.mesh_loader import load_3d_model
    from core.volume_calculator import calculate_volume_and_dimensions
    from core.preview_generator import (
        create_model_viewer_html,
        trimesh_to_glb_bytes,
    )
    from core.scale_handler_enhanced import (
        apply_scale_factor,
        apply_non_uniform_scale,
        apply_dimensional_scale,
        calculate_proportional_dimension,
        UNIT_CONVERSION_FACTORS,
    )
except ImportError:
    from mesh_loader import load_3d_model
    from volume_calculator import calculate_volume_and_dimensions
    from preview_generator import (
        create_model_viewer_html,
        trimesh_to_glb_bytes,
    )
    from scale_handler_enhanced import (
        apply_scale_factor,
        apply_non_uniform_scale,
        apply_dimensional_scale,
        calculate_proportional_dimension,
        UNIT_CONVERSION_FACTORS,
    )

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="3D Volume Calculator",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state ───────────────────────────────────────────────────────────
if 'model_data' not in st.session_state:
    st.session_state.model_data = None
if 'scaled_mesh' not in st.session_state:
    st.session_state.scaled_mesh = None
if 'original_mesh' not in st.session_state:
    st.session_state.original_mesh = None
if 'original_dimensions' not in st.session_state:
    st.session_state.original_dimensions = None
if 'temp_length' not in st.session_state:
    st.session_state.temp_length = None
if 'temp_width' not in st.session_state:
    st.session_state.temp_width = None
if 'temp_height' not in st.session_state:
    st.session_state.temp_height = None
if 'original_file_bytes' not in st.session_state:
    st.session_state.original_file_bytes = None
if 'original_file_ext' not in st.session_state:
    st.session_state.original_file_ext = None
if 'was_scaled' not in st.session_state:
    st.session_state.was_scaled = False

# ── Theme / typography injection ────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"], .stApp,
    .stMarkdown, .stText, .stCaption, button, input, textarea, select {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    [data-testid="stToolbar"] { display: none; }

    /* Container */
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1180px;
    }

    /* Custom header */
    .app-header {
        padding-bottom: 1.25rem;
        border-bottom: 1px solid #1f1f1f;
        margin-bottom: 2rem;
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .app-title {
        font-size: 22px;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #fafafa;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .app-mark {
        display: inline-block;
        width: 10px; height: 10px;
        background: #6366f1;
        border-radius: 2px;
        transform: rotate(45deg);
    }
    .app-subtitle {
        font-size: 13px;
        color: #737373;
        margin: 0;
    }

    /* Section labels */
    .section-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #737373;
        margin: 2.25rem 0 0.875rem 0;
    }
    .section-label:first-of-type { margin-top: 0; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #111111;
        border: 1px solid #1f1f1f;
        border-radius: 10px;
        padding: 14px 18px;
        transition: border-color 0.15s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: #2a2a2a;
    }
    [data-testid="stMetricLabel"] {
        color: #737373 !important;
    }
    [data-testid="stMetricLabel"] p {
        font-size: 11px !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #737373 !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', ui-monospace, monospace !important;
        font-size: 26px !important;
        font-weight: 600 !important;
        color: #fafafa !important;
        margin-top: 2px;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', ui-monospace, monospace !important;
        font-size: 12px !important;
    }

    /* Buttons */
    .stButton > button, .stDownloadButton > button {
        border-radius: 7px;
        border: 1px solid #262626;
        background-color: #111111;
        color: #fafafa;
        font-weight: 500;
        font-size: 13px;
        padding: 0.5rem 1rem;
        transition: all 0.15s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: #404040;
        background-color: #1a1a1a;
        color: #fafafa;
    }
    .stButton > button[kind="primary"] {
        background-color: #6366f1;
        border-color: #6366f1;
        color: #ffffff;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #818cf8;
        border-color: #818cf8;
    }

    /* File uploader */
    [data-testid="stFileUploader"] section {
        background-color: #0c0c0c;
        border: 1px dashed #2a2a2a;
        border-radius: 10px;
        padding: 1.25rem;
        transition: all 0.15s ease;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #6366f1;
        background-color: #0f0f0f;
    }
    [data-testid="stFileUploaderDropzone"] {
        background-color: transparent;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        border: 1px solid #1f1f1f;
        border-radius: 10px;
        background-color: #0c0c0c;
        margin-bottom: 0.75rem;
    }
    [data-testid="stExpander"] details summary {
        padding: 0.875rem 1rem;
        font-weight: 500;
        font-size: 14px;
    }
    [data-testid="stExpander"] details summary:hover {
        background-color: #111111;
    }
    [data-testid="stExpander"] details > div {
        padding: 0 1rem 1rem 1rem;
        border-top: 1px solid #1a1a1a;
    }

    /* Inputs */
    .stNumberInput input, .stTextInput input, .stSelectbox > div > div {
        background-color: #111111 !important;
        border: 1px solid #262626 !important;
        color: #fafafa !important;
        border-radius: 6px !important;
    }
    .stNumberInput input:focus, .stTextInput input:focus {
        border-color: #6366f1 !important;
    }

    /* Captions */
    [data-testid="stCaptionContainer"], .stCaption {
        color: #737373 !important;
        font-size: 12px !important;
    }

    /* Dividers */
    hr {
        border: none !important;
        border-top: 1px solid #1f1f1f !important;
        margin: 1.25rem 0 !important;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        border-radius: 8px;
        border: 1px solid;
        font-size: 13px;
    }

    /* Code block */
    .stCodeBlock, [data-testid="stCodeBlock"] {
        background-color: #0c0c0c !important;
        border: 1px solid #1f1f1f !important;
        border-radius: 8px !important;
    }

    /* Metadata strip */
    .meta-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem 1rem;
        font-size: 12px;
        color: #737373;
        margin: 0.25rem 0 0 0;
        font-family: 'JetBrains Mono', ui-monospace, monospace;
    }
    .meta-strip .sep { color: #404040; }
    .meta-strip .ok { color: #10b981; }
    .meta-strip .warn { color: #f59e0b; }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #737373;
        font-size: 14px;
        border: 1px dashed #1f1f1f;
        border-radius: 12px;
        background-color: #0c0c0c;
    }

    /* Footer */
    .app-footer {
        margin-top: 4rem;
        padding-top: 1rem;
        border-top: 1px solid #1f1f1f;
        text-align: center;
        color: #525252;
        font-size: 11px;
        letter-spacing: 0.04em;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #0a0a0a; }
    ::-webkit-scrollbar-thumb { background: #1f1f1f; border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: #2a2a2a; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #080808;
        border-right: 1px solid #1f1f1f;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="app-header">
        <div>
            <div class="app-title"><span class="app-mark"></span>3D Volume Calculator</div>
            <div class="app-subtitle">Volume and dimensions from STL, GLB, GLTF, OBJ, and 3MF</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar (slim) ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">Reference</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style='font-size:13px; color:#a3a3a3; line-height:1.65;'>
        <strong style='color:#fafafa;'>Supported formats</strong><br>
        STL · 3MF · OBJ · GLB · GLTF<br><br>
        <strong style='color:#fafafa;'>Texture & animation</strong><br>
        GLB embeds them. STL/3MF/OBJ render as flat geometry.<br><br>
        <strong style='color:#fafafa;'>Limits</strong><br>
        50 MB max upload<br>
        All units in millimeters
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Upload row ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Model</div>', unsafe_allow_html=True)

col_upload, col_filemeta = st.columns([2, 3])
with col_upload:
    uploaded_file = st.file_uploader(
        "Upload model",
        type=['stl', '3mf', 'obj', 'glb', 'gltf'],
        help="STL · 3MF · OBJ · GLB · GLTF — up to 50 MB",
        label_visibility="collapsed",
    )

# ── Process upload ──────────────────────────────────────────────────────────
if uploaded_file is not None:
    try:
        with st.spinner("Loading model…"):
            mesh_result = load_3d_model(uploaded_file)

            if mesh_result['success']:
                mesh = mesh_result['mesh']
                calc_result = calculate_volume_and_dimensions(mesh)

                st.session_state.model_data = {
                    **calc_result,
                    'filename': uploaded_file.name,
                    'format': mesh_result['format'],
                    'file_size': mesh_result['file_size'],
                    'timestamp': datetime.now().isoformat(),
                }
                st.session_state.scaled_mesh = copy.deepcopy(mesh)
                st.session_state.original_mesh = copy.deepcopy(mesh)
                st.session_state.original_file_bytes = mesh_result.get('file_bytes')
                st.session_state.original_file_ext = (mesh_result.get('file_ext') or '').lower()
                st.session_state.was_scaled = False

                st.session_state.original_dimensions = {
                    'length': calc_result['length_mm'],
                    'width': calc_result['width_mm'],
                    'height': calc_result['height_mm'],
                }
                st.session_state.temp_length = calc_result['length_mm']
                st.session_state.temp_width = calc_result['width_mm']
                st.session_state.temp_height = calc_result['height_mm']
            else:
                st.error(mesh_result['error'])

    except Exception as e:
        st.error(f"Could not load model: {e}")

# ── Filemeta strip alongside upload ─────────────────────────────────────────
with col_filemeta:
    if st.session_state.model_data:
        d = st.session_state.model_data
        size_mb = d['file_size'] / (1024 * 1024)
        watertight_html = (
            '<span class="ok">● Watertight</span>'
            if d['is_watertight']
            else '<span class="warn">● Non-watertight</span>'
        )
        st.markdown(
            f"""
            <div style='padding-top:0.5rem;'>
              <div style='font-size:14px; color:#fafafa; font-weight:500;'>{d['filename']}</div>
              <div class='meta-strip'>
                <span>{d['format']}</span><span class='sep'>·</span>
                <span>{size_mb:.2f} MB</span><span class='sep'>·</span>
                <span>{d['triangles']:,} triangles</span><span class='sep'>·</span>
                <span>{d['vertices']:,} vertices</span><span class='sep'>·</span>
                {watertight_html}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='padding-top:0.6rem; font-size:13px; color:#525252;'>No model loaded</div>",
            unsafe_allow_html=True,
        )

# ── Main content (only when a model is loaded) ──────────────────────────────
if st.session_state.model_data is None:
    st.markdown(
        """
        <div class='empty-state' style='margin-top:1.5rem;'>
            Drop a 3D model above to calculate volume, view dimensions,
            and preview with embedded textures and animations.
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    data = st.session_state.model_data

    # ── Preview (hero) ──────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Preview</div>', unsafe_allow_html=True)

    mesh_to_preview = st.session_state.scaled_mesh
    file_bytes = st.session_state.get('original_file_bytes')
    file_ext = st.session_state.get('original_file_ext') or ''
    was_scaled = st.session_state.get('was_scaled', False)

    use_original_glb = (
        file_ext == '.glb'
        and not was_scaled
        and file_bytes is not None
    )

    glb_bytes = None
    note = None
    try:
        with st.spinner("Preparing 3D preview…"):
            if use_original_glb:
                glb_bytes = file_bytes
                note = "Original GLB · embedded textures and animations preserved"
            else:
                glb_bytes = trimesh_to_glb_bytes(mesh_to_preview)
                if file_ext in ('.glb', '.gltf') and was_scaled:
                    note = (
                        "Scaled geometry · embedded animations stripped on re-export"
                    )
                elif file_ext in ('.stl', '.3mf', '.obj'):
                    note = (
                        f"{file_ext.lstrip('.').upper()} files do not carry textures "
                        "or animations · rendering geometry only"
                    )
    except Exception as e:
        st.error(f"Could not prepare GLB: {e}")

    if glb_bytes is not None:
        try:
            html = create_model_viewer_html(
                glb_bytes,
                height=680,
                autoplay=True,
                auto_rotate=not use_original_glb,
                background='#0f0f0f',
            )
            components.html(html, height=720, scrolling=False)
            if note:
                st.caption(note)
        except Exception as e:
            st.error(f"Error rendering 3D preview: {e}")

    # ── Measurements ────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Measurements</div>', unsafe_allow_html=True)

    volume_cm3 = data['volume_mm3'] / 1000
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Volume", f"{volume_cm3:,.2f}", "cm³")
    with m2:
        st.metric("Length", f"{data['length_mm']:.2f}", "mm · X")
    with m3:
        st.metric("Width", f"{data['width_mm']:.2f}", "mm · Y")
    with m4:
        st.metric("Height", f"{data['height_mm']:.2f}", "mm · Z")

    if not data['is_watertight']:
        st.caption(
            "Mesh is not watertight — volume is approximate. "
            "Repair the mesh in CAD to get an exact value."
        )

    # ── Tools ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Tools</div>', unsafe_allow_html=True)

    # ── Tool: Scale & resize ────────────────────────────────────────────────
    with st.expander("Scale & resize", expanded=False):
        scale_method = st.radio(
            "Method",
            ["Edit dimensions", "Scale factor", "Unit conversion"],
            horizontal=True,
            key="scale_method_radio",
        )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # ── Method 1: Edit dimensions ──
        if scale_method == "Edit dimensions":
            proportional = st.checkbox(
                "Proportional scaling",
                value=True,
                help="Maintain shape proportions",
                key="proportional_check",
            )

            current_length = data['length_mm']
            current_width = data['width_mm']
            current_height = data['height_mm']

            col_dim1, col_dim2, col_dim3 = st.columns(3)
            with col_dim1:
                st.markdown(
                    "<div style='font-size:11px;color:#737373;text-transform:uppercase;"
                    "letter-spacing:0.06em;margin-bottom:4px;'>Length · X</div>",
                    unsafe_allow_html=True,
                )
                new_length = st.number_input(
                    "Length (mm)",
                    min_value=0.01, max_value=10000.0,
                    value=float(current_length), step=0.1, format="%.2f",
                    key="dim_length", label_visibility="collapsed",
                )

            if proportional and new_length != current_length:
                scale_ratio = new_length / current_length
                calculated_width = current_width * scale_ratio
                calculated_height = current_height * scale_ratio
            else:
                calculated_width = current_width
                calculated_height = current_height

            with col_dim2:
                st.markdown(
                    "<div style='font-size:11px;color:#737373;text-transform:uppercase;"
                    "letter-spacing:0.06em;margin-bottom:4px;'>Width · Y</div>",
                    unsafe_allow_html=True,
                )
                if proportional and new_length != current_length:
                    new_width = st.number_input(
                        "Width (mm)",
                        min_value=0.01, max_value=10000.0,
                        value=float(calculated_width), step=0.1, format="%.2f",
                        key="dim_width", label_visibility="collapsed", disabled=True,
                    )
                else:
                    new_width = st.number_input(
                        "Width (mm)",
                        min_value=0.01, max_value=10000.0,
                        value=float(current_width), step=0.1, format="%.2f",
                        key="dim_width", label_visibility="collapsed",
                    )

            with col_dim3:
                st.markdown(
                    "<div style='font-size:11px;color:#737373;text-transform:uppercase;"
                    "letter-spacing:0.06em;margin-bottom:4px;'>Height · Z</div>",
                    unsafe_allow_html=True,
                )
                if proportional and new_length != current_length:
                    new_height = st.number_input(
                        "Height (mm)",
                        min_value=0.01, max_value=10000.0,
                        value=float(calculated_height), step=0.1, format="%.2f",
                        key="dim_height", label_visibility="collapsed", disabled=True,
                    )
                else:
                    new_height = st.number_input(
                        "Height (mm)",
                        min_value=0.01, max_value=10000.0,
                        value=float(current_height), step=0.1, format="%.2f",
                        key="dim_height", label_visibility="collapsed",
                    )

            x_scale = new_length / current_length
            y_scale = new_width / current_width
            z_scale = new_height / current_height
            volume_scale = x_scale * y_scale * z_scale
            new_volume = data['volume_mm3'] * volume_scale
            new_volume_cm3 = new_volume / 1000

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.markdown(
                "<div style='font-size:11px;color:#737373;text-transform:uppercase;"
                "letter-spacing:0.06em;'>Preview after apply</div>",
                unsafe_allow_html=True,
            )
            p1, p2, p3, p4 = st.columns(4)
            with p1:
                st.metric("Length", f"{new_length:.2f}", f"{(x_scale-1)*100:+.1f}%")
            with p2:
                st.metric("Width", f"{new_width:.2f}", f"{(y_scale-1)*100:+.1f}%")
            with p3:
                st.metric("Height", f"{new_height:.2f}", f"{(z_scale-1)*100:+.1f}%")
            with p4:
                st.metric("Volume", f"{new_volume_cm3:.2f}", f"{(volume_scale-1)*100:+.1f}%")

            if not proportional and (
                abs(x_scale - y_scale) > 0.001 or abs(y_scale - z_scale) > 0.001
            ):
                st.caption("⚠ Non-proportional scaling — model will be distorted.")

            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
            if st.button(
                "Apply dimensions",
                use_container_width=True, type="primary", key="apply_dims",
            ):
                try:
                    scaled_mesh = copy.deepcopy(st.session_state.original_mesh)
                    scaled_mesh = apply_non_uniform_scale(
                        scaled_mesh, x_scale, y_scale, z_scale
                    )
                    calc_result = calculate_volume_and_dimensions(scaled_mesh)
                    st.session_state.model_data.update(calc_result)
                    st.session_state.scaled_mesh = scaled_mesh
                    st.session_state.was_scaled = True
                    st.success("Dimensions applied")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        # ── Method 2: Scale factor ──
        elif scale_method == "Scale factor":
            scale_factor = st.number_input(
                "Scale factor (1.0 = no change)",
                min_value=0.01, max_value=100.0,
                value=1.0, step=0.1, format="%.2f",
                key="scale_factor_input",
            )
            st.caption(f"= {scale_factor*100:.0f}% of current size")

            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            if st.button(
                "Apply scale factor",
                use_container_width=True, type="primary", key="apply_scale",
            ):
                try:
                    scaled_mesh = copy.deepcopy(st.session_state.original_mesh)
                    current_length = data['length_mm']
                    original_length = st.session_state.original_dimensions['length']
                    current_scale = current_length / original_length
                    total_scale = current_scale * scale_factor
                    scaled_mesh = apply_scale_factor(scaled_mesh, total_scale)
                    calc_result = calculate_volume_and_dimensions(scaled_mesh)
                    st.session_state.model_data.update(calc_result)
                    st.session_state.scaled_mesh = scaled_mesh
                    st.session_state.was_scaled = True
                    st.success(f"Scaled {scale_factor:.2f}×")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        # ── Method 3: Unit conversion ──
        elif scale_method == "Unit conversion":
            from_unit = st.selectbox(
                "File units",
                ["millimeters", "centimeters", "inches", "meters"],
                index=0, key="unit_select",
            )
            conversion_factor = UNIT_CONVERSION_FACTORS[from_unit]
            st.caption(f"Multiplies geometry by {conversion_factor} to convert to mm")

            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            if st.button(
                "Apply conversion",
                use_container_width=True, type="primary", key="apply_unit",
            ):
                try:
                    scaled_mesh = copy.deepcopy(st.session_state.original_mesh)
                    scaled_mesh = apply_scale_factor(scaled_mesh, conversion_factor)
                    calc_result = calculate_volume_and_dimensions(scaled_mesh)
                    st.session_state.model_data.update(calc_result)
                    st.session_state.scaled_mesh = scaled_mesh
                    st.session_state.was_scaled = True
                    st.success(f"Converted from {from_unit} to mm")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # ── Tool: Export ────────────────────────────────────────────────────────
    with st.expander("Export results", expanded=False):
        export_data = {
            'volume_mm3': data['volume_mm3'],
            'volume_cm3': volume_cm3,
            'dimensions_mm': {
                'length': data['length_mm'],
                'width': data['width_mm'],
                'height': data['height_mm'],
            },
            'source': '3D_MODEL',
            'filename': data['filename'],
            'format': data['format'],
            'is_watertight': data['is_watertight'],
            'mesh_info': {
                'triangles': data['triangles'],
                'vertices': data['vertices'],
            },
            'timestamp': data['timestamp'],
        }
        json_str = json.dumps(export_data, indent=2)

        st.download_button(
            label="Download JSON for DVA",
            data=json_str,
            file_name=f"volume_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:11px;color:#737373;text-transform:uppercase;"
            "letter-spacing:0.06em;margin-bottom:0.4rem;'>Raw payload</div>",
            unsafe_allow_html=True,
        )
        st.code(json_str, language='json')

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class='app-footer'>
        3D VOLUME CALCULATOR · BUILT WITH STREAMLIT, TRIMESH, &lt;MODEL-VIEWER&gt;
    </div>
    """,
    unsafe_allow_html=True,
)
