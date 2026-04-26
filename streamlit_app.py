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

# Try importing from core package, fall back to direct imports
try:
    from core.mesh_loader import load_3d_model
    from core.volume_calculator import calculate_volume_and_dimensions
    from core.preview_generator import (
        create_3d_preview,
        create_model_viewer_html,
        trimesh_to_glb_bytes,
    )
    from core.scale_handler_enhanced import (
        apply_scale_factor,
        apply_non_uniform_scale,
        apply_dimensional_scale,
        calculate_proportional_dimension,
        UNIT_CONVERSION_FACTORS
    )
except ImportError:
    try:
        from mesh_loader import load_3d_model
        from volume_calculator import calculate_volume_and_dimensions
        from preview_generator import (
            create_3d_preview,
            create_model_viewer_html,
            trimesh_to_glb_bytes,
        )
        from scale_handler_enhanced import (
            apply_scale_factor,
            apply_non_uniform_scale,
            apply_dimensional_scale,
            calculate_proportional_dimension,
            UNIT_CONVERSION_FACTORS
        )
    except ImportError:
        try:
            from core.scale_handler import apply_scale_factor, UNIT_CONVERSION_FACTORS
            def apply_non_uniform_scale(mesh, x, y, z):
                mesh.apply_scale([x, y, z])
                return mesh
            def apply_dimensional_scale(mesh, curr, targ, prop):
                scales = {'x_scale': targ['length']/curr['length'], 
                         'y_scale': targ['width']/curr['width'],
                         'z_scale': targ['height']/curr['height']}
                mesh.apply_scale([scales['x_scale'], scales['y_scale'], scales['z_scale']])
                return mesh, scales
            def calculate_proportional_dimension(new, old_changed, old_target):
                return (new / old_changed) * old_target if old_changed > 0 else old_target
        except ImportError as e:
            st.error(f"""
            ❌ **Import Error**
            
            Cannot find required modules. Error: {str(e)}
            """)
            st.stop()

# Page config
st.set_page_config(
    page_title="3D Volume Calculator",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'model_data' not in st.session_state:
    st.session_state.model_data = None
if 'scaled_mesh' not in st.session_state:
    st.session_state.scaled_mesh = None
if 'original_mesh' not in st.session_state:
    st.session_state.original_mesh = None
if 'original_dimensions' not in st.session_state:
    st.session_state.original_dimensions = None
if 'show_scale_controls' not in st.session_state:
    st.session_state.show_scale_controls = False
if 'temp_length' not in st.session_state:
    st.session_state.temp_length = None
if 'temp_width' not in st.session_state:
    st.session_state.temp_width = None
if 'temp_height' not in st.session_state:
    st.session_state.temp_height = None
# Raw bytes + ext of the uploaded file. Used by the <model-viewer> preview
# so unmodified GLB uploads keep their embedded animations.
if 'original_file_bytes' not in st.session_state:
    st.session_state.original_file_bytes = None
if 'original_file_ext' not in st.session_state:
    st.session_state.original_file_ext = None
# Set True once the user applies any scale/resize. Drives whether the
# preview uses the raw original bytes (animations) vs. a re-exported GLB
# of the scaled mesh (no animations).
if 'was_scaled' not in st.session_state:
    st.session_state.was_scaled = False

# Header
st.title("📐 3D Volume Calculator")
st.markdown("**Calculate accurate volumes from 3D model files** • Export to DVA or use standalone")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    Upload your 3D model to:
    - Calculate exact volume
    - View dimensions
    - Preview 3D model
    - Scale/resize
    - Export to DVA
    
    **Supported Formats:**
    - STL (3D printing)
    - 3MF (modern 3D printing)
    - OBJ (universal interchange)
    - GLB (web 3D binary)
    - GLTF (web 3D JSON)
    """)
    
    st.markdown("---")
    st.markdown("**Max file size:** 50 MB")
    st.markdown("**All units:** Millimeters (mm)")

# Main content - Single tab now
tab1, tab2 = st.tabs(["📁 Upload & Calculate", "📤 Export Results"])

# ═══════════════════════════════════════════════════════════════════
# TAB 1: UPLOAD & CALCULATE (with integrated scaling)
# ═══════════════════════════════════════════════════════════════════

with tab1:
    st.header("Upload 3D Model")
    
    uploaded_file = st.file_uploader(
        "Choose a 3D model file",
        type=['stl', '3mf', 'obj', 'glb', 'gltf'],
        help="Upload your product's 3D model file"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("Loading 3D model..."):
                # Load mesh
                mesh_result = load_3d_model(uploaded_file)
                
                if mesh_result['success']:
                    mesh = mesh_result['mesh']
                    
                    # Calculate volume and dimensions
                    calc_result = calculate_volume_and_dimensions(mesh)
                    
                    # Store in session state
                    st.session_state.model_data = {
                        **calc_result,
                        'filename': uploaded_file.name,
                        'format': mesh_result['format'],
                        'file_size': mesh_result['file_size'],
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state.scaled_mesh = copy.deepcopy(mesh)
                    st.session_state.original_mesh = copy.deepcopy(mesh)
                    st.session_state.original_file_bytes = mesh_result.get('file_bytes')
                    st.session_state.original_file_ext = (mesh_result.get('file_ext') or '').lower()
                    st.session_state.was_scaled = False
                    
                    # Store original dimensions
                    st.session_state.original_dimensions = {
                        'length': calc_result['length_mm'],
                        'width': calc_result['width_mm'],
                        'height': calc_result['height_mm']
                    }
                    
                    # Initialize temp dimensions
                    st.session_state.temp_length = calc_result['length_mm']
                    st.session_state.temp_width = calc_result['width_mm']
                    st.session_state.temp_height = calc_result['height_mm']
                    
                    st.success(f"✅ Model loaded: {uploaded_file.name}")
                else:
                    st.error(f"❌ Error: {mesh_result['error']}")
                    
        except Exception as e:
            st.error(f"❌ Error loading model: {str(e)}")
    
    # Display results if model loaded
    if st.session_state.model_data:
        st.markdown("---")
        data = st.session_state.model_data

        with st.expander("📊 Calculated Results", expanded=True):
            # Metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                volume_cm3 = data['volume_mm3'] / 1000
                st.metric("Volume", f"{volume_cm3:,.2f} cm³")

            with col2:
                st.metric("Length", f"{data['length_mm']:.2f} mm")

            with col3:
                st.metric("Width", f"{data['width_mm']:.2f} mm")

            with col4:
                st.metric("Height", f"{data['height_mm']:.2f} mm")

            # Detailed info
            st.markdown("---")
            col_info1, col_info2 = st.columns(2)

            with col_info1:
                st.markdown("**📁 File Information**")
                st.write(f"**Filename:** {data['filename']}")
                st.write(f"**Format:** {data['format']}")
                st.write(f"**File size:** {data['file_size']/(1024*1024):.2f} MB")

            with col_info2:
                st.markdown("**🔍 Mesh Quality**")
                watertight_icon = "✓" if data['is_watertight'] else "✗"
                watertight_text = "Yes (exact volume)" if data['is_watertight'] else "No (approximate)"
                st.write(f"**Watertight:** {watertight_icon} {watertight_text}")
                st.write(f"**Triangles:** {data['triangles']:,}")
                st.write(f"**Vertices:** {data['vertices']:,}")
        
        # ═══════════════════════════════════════════════════════════════
        # SCALE & RESIZE SECTION (Integrated)
        # ═══════════════════════════════════════════════════════════════
        
        st.markdown("---")
        
        # Button to show/hide scale controls
        if st.button("🔧 Scale & Resize Model" if not st.session_state.show_scale_controls else "✕ Close Scale Controls", 
                     use_container_width=True):
            st.session_state.show_scale_controls = not st.session_state.show_scale_controls
            st.rerun()
        
        # Show scale controls if enabled
        if st.session_state.show_scale_controls:
            st.markdown("### 🔧 Scale & Resize Model")
            
            # Method selection
            scale_method = st.radio(
                "Scaling Method:",
                ["Edit Dimensions", "Scale Factor", "Unit Conversion"],
                horizontal=True,
                key="scale_method_radio"
            )
            
            st.markdown("---")
            
            # ═══════════════════════════════════════════════════════
            # METHOD 1: EDIT DIMENSIONS (Default, Most Powerful)
            # ═══════════════════════════════════════════════════════
            
            if scale_method == "Edit Dimensions":
                st.markdown("**Edit Dimensions Directly**")
                
                # Proportional checkbox
                proportional = st.checkbox(
                    "🔗 Proportional Scaling",
                    value=True,
                    help="Maintain shape proportions",
                    key="proportional_check"
                )
                
                # Get current dimensions
                current_length = data['length_mm']
                current_width = data['width_mm']
                current_height = data['height_mm']
                
                # Dimension inputs
                col_dim1, col_dim2, col_dim3 = st.columns(3)
                
                with col_dim1:
                    st.markdown("**📏 Length (X)**")
                    new_length = st.number_input(
                        "Length (mm)",
                        min_value=0.01,
                        max_value=10000.0,
                        value=float(current_length),
                        step=0.1,
                        format="%.2f",
                        key="dim_length",
                        label_visibility="collapsed"
                    )
                
                # Calculate proportional dimensions if length changed
                if proportional and new_length != current_length:
                    scale_ratio = new_length / current_length
                    calculated_width = current_width * scale_ratio
                    calculated_height = current_height * scale_ratio
                else:
                    calculated_width = current_width
                    calculated_height = current_height
                
                with col_dim2:
                    st.markdown("**📏 Width (Y)**")
                    if proportional and new_length != current_length:
                        # Show calculated value, make it editable but update it
                        new_width = st.number_input(
                            "Width (mm)",
                            min_value=0.01,
                            max_value=10000.0,
                            value=float(calculated_width),
                            step=0.1,
                            format="%.2f",
                            key="dim_width",
                            label_visibility="collapsed",
                            disabled=True
                        )
                    else:
                        new_width = st.number_input(
                            "Width (mm)",
                            min_value=0.01,
                            max_value=10000.0,
                            value=float(current_width),
                            step=0.1,
                            format="%.2f",
                            key="dim_width",
                            label_visibility="collapsed"
                        )
                
                with col_dim3:
                    st.markdown("**📏 Height (Z)**")
                    if proportional and new_length != current_length:
                        # Show calculated value
                        new_height = st.number_input(
                            "Height (mm)",
                            min_value=0.01,
                            max_value=10000.0,
                            value=float(calculated_height),
                            step=0.1,
                            format="%.2f",
                            key="dim_height",
                            label_visibility="collapsed",
                            disabled=True
                        )
                    else:
                        new_height = st.number_input(
                            "Height (mm)",
                            min_value=0.01,
                            max_value=10000.0,
                            value=float(current_height),
                            step=0.1,
                            format="%.2f",
                            key="dim_height",
                            label_visibility="collapsed"
                        )
                
                # Show changes preview
                st.markdown("---")
                st.markdown("**Preview Changes:**")
                
                x_scale = new_length / current_length
                y_scale = new_width / current_width
                z_scale = new_height / current_height
                volume_scale = x_scale * y_scale * z_scale
                new_volume = data['volume_mm3'] * volume_scale
                new_volume_cm3 = new_volume / 1000
                
                col_p1, col_p2, col_p3 = st.columns(3)
                
                with col_p1:
                    st.metric("New Length", f"{new_length:.2f} mm", f"{(x_scale-1)*100:+.1f}%")
                with col_p2:
                    st.metric("New Width", f"{new_width:.2f} mm", f"{(y_scale-1)*100:+.1f}%")
                with col_p3:
                    st.metric("New Height", f"{new_height:.2f} mm", f"{(z_scale-1)*100:+.1f}%")
                
                st.metric("New Volume", f"{new_volume_cm3:.2f} cm³", f"{(volume_scale-1)*100:+.1f}%")
                
                # Warning for non-proportional
                if not proportional and (abs(x_scale - y_scale) > 0.001 or abs(y_scale - z_scale) > 0.001):
                    st.warning("⚠️ **Non-proportional scaling** - Model will be distorted!")
                
                # Apply button
                if st.button("✓ Apply New Dimensions", use_container_width=True, type="primary", key="apply_dims"):
                    try:
                        # Create fresh copy from original
                        scaled_mesh = copy.deepcopy(st.session_state.original_mesh)
                        
                        # Apply scaling
                        scaled_mesh = apply_non_uniform_scale(scaled_mesh, x_scale, y_scale, z_scale)
                        
                        # Recalculate
                        calc_result = calculate_volume_and_dimensions(scaled_mesh)
                        
                        # Update session state
                        st.session_state.model_data.update(calc_result)
                        st.session_state.scaled_mesh = scaled_mesh
                        st.session_state.was_scaled = True
                        
                        st.success("✅ Dimensions applied!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            # ═══════════════════════════════════════════════════════
            # METHOD 2: SCALE FACTOR
            # ═══════════════════════════════════════════════════════
            
            elif scale_method == "Scale Factor":
                st.markdown("**Uniform Scale Factor**")
                
                scale_factor = st.number_input(
                    "Scale factor (1.0 = no change)",
                    min_value=0.01,
                    max_value=100.0,
                    value=1.0,
                    step=0.1,
                    format="%.2f",
                    key="scale_factor_input"
                )
                
                st.caption(f"= {scale_factor*100:.0f}% of current size")
                
                if st.button("✓ Apply Scale Factor", use_container_width=True, type="primary", key="apply_scale"):
                    try:
                        scaled_mesh = copy.deepcopy(st.session_state.original_mesh)
                        
                        # Calculate total scale from original
                        current_length = data['length_mm']
                        original_length = st.session_state.original_dimensions['length']
                        current_scale = current_length / original_length
                        total_scale = current_scale * scale_factor
                        
                        scaled_mesh = apply_scale_factor(scaled_mesh, total_scale)
                        calc_result = calculate_volume_and_dimensions(scaled_mesh)
                        
                        st.session_state.model_data.update(calc_result)
                        st.session_state.scaled_mesh = scaled_mesh
                        st.session_state.was_scaled = True
                        
                        st.success(f"✅ Scaled {scale_factor:.2f}x")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            # ═══════════════════════════════════════════════════════
            # METHOD 3: UNIT CONVERSION
            # ═══════════════════════════════════════════════════════
            
            elif scale_method == "Unit Conversion":
                st.markdown("**Unit Conversion**")
                
                from_unit = st.selectbox(
                    "File is in:",
                    ["millimeters", "centimeters", "inches", "meters"],
                    index=0,
                    key="unit_select"
                )
                
                conversion_factor = UNIT_CONVERSION_FACTORS[from_unit]
                st.caption(f"Will multiply by {conversion_factor} to convert to mm")
                
                if st.button("✓ Apply Conversion", use_container_width=True, type="primary", key="apply_unit"):
                    try:
                        scaled_mesh = copy.deepcopy(st.session_state.original_mesh)
                        scaled_mesh = apply_scale_factor(scaled_mesh, conversion_factor)
                        calc_result = calculate_volume_and_dimensions(scaled_mesh)
                        
                        st.session_state.model_data.update(calc_result)
                        st.session_state.scaled_mesh = scaled_mesh
                        st.session_state.was_scaled = True
                        
                        st.success(f"✅ Converted from {from_unit} to mm")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # ═══════════════════════════════════════════════════════════════
        # 3D PREVIEW (Shows scaled model)
        # ═══════════════════════════════════════════════════════════════
        
        st.markdown("---")
        if st.checkbox("🎨 Show 3D Preview", value=True, key="show_preview"):
            mesh_to_preview = st.session_state.scaled_mesh
            file_bytes = st.session_state.get('original_file_bytes')
            file_ext = st.session_state.get('original_file_ext') or ''
            was_scaled = st.session_state.get('was_scaled', False)

            # Decide which GLB to feed <model-viewer>:
            #   - Unmodified GLB upload  → original bytes (animations preserved)
            #   - Anything else          → trimesh.export(glb)  (geometry+textures only)
            use_original_glb = (
                file_ext == '.glb'
                and not was_scaled
                and file_bytes is not None
            )

            glb_bytes = None
            note = None
            try:
                with st.spinner("Preparing 3D preview..."):
                    if use_original_glb:
                        glb_bytes = file_bytes
                        note = "🎬 Original GLB — embedded textures and animations preserved."
                    else:
                        glb_bytes = trimesh_to_glb_bytes(mesh_to_preview)
                        if file_ext in ('.glb', '.gltf') and was_scaled:
                            note = (
                                "📐 Scaled geometry — embedded animations are stripped "
                                "when the mesh is re-exported after scaling."
                            )
                        elif file_ext in ('.stl', '.3mf', '.obj'):
                            note = (
                                f"ℹ️ {file_ext.lstrip('.').upper()} files do not carry "
                                "textures or animations by spec — rendering geometry only."
                            )
            except Exception as e:
                st.error(f"Could not prepare GLB for preview: {e}")

            if glb_bytes is not None:
                if note:
                    st.caption(note)
                # Heuristic: disable auto-rotate when an animation is likely to
                # play, so the two don't fight. Original GLB → likely animated.
                auto_rotate = not use_original_glb
                try:
                    html = create_model_viewer_html(
                        glb_bytes,
                        height=550,
                        autoplay=True,
                        auto_rotate=auto_rotate,
                    )
                    # components.html height needs to fit the viewer + the small
                    # hint strip below it; +30 is enough for the 11px caption.
                    components.html(html, height=580, scrolling=False)
                except Exception as e:
                    st.error(f"Error rendering 3D preview: {e}")
    else:
        st.info("👆 Upload a 3D model to get started")


# ═══════════════════════════════════════════════════════════════════
# TAB 2: EXPORT RESULTS
# ═══════════════════════════════════════════════════════════════════

with tab2:
    st.header("📤 Export Results")
    
    if st.session_state.model_data is None:
        st.info("Calculate volume first (see Upload & Calculate tab)")
    else:
        data = st.session_state.model_data
        
        # Summary
        st.markdown("### Results Summary")
        volume_cm3 = data['volume_mm3'] / 1000
        st.success(f"""
        **Volume:** {volume_cm3:,.2f} cm³ ({data['volume_mm3']:,.0f} mm³)  
        **Dimensions:** {data['length_mm']:.2f} × {data['width_mm']:.2f} × {data['height_mm']:.2f} mm  
        **Source:** 3D Model ({data['format']})
        """)
        
        st.markdown("---")
        
        # Export options
        st.markdown("### Export Options")
        
        # Create export data
        export_data = {
            'volume_mm3': data['volume_mm3'],
            'volume_cm3': volume_cm3,
            'dimensions_mm': {
                'length': data['length_mm'],
                'width': data['width_mm'],
                'height': data['height_mm']
            },
            'source': '3D_MODEL',
            'filename': data['filename'],
            'format': data['format'],
            'is_watertight': data['is_watertight'],
            'mesh_info': {
                'triangles': data['triangles'],
                'vertices': data['vertices']
            },
            'timestamp': data['timestamp']
        }
        
        # Option 1: Download JSON for DVA
        st.markdown("#### 🔗 Export to DVA")
        st.markdown("Download this file and import it in DVA's Primary Calculator")
        
        json_str = json.dumps(export_data, indent=2)
        
        st.download_button(
            label="📥 Download for DVA (.json)",
            data=json_str,
            file_name=f"volume_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        
        # Option 2: Copy data
        st.markdown("---")
        st.markdown("#### 📋 Copy Data")
        st.markdown("Or copy this data manually:")
        
        st.code(json_str, language='json')
        
        # Option 3: View formatted
        st.markdown("---")
        st.markdown("#### 📊 Formatted View")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Volume Data**")
            st.write(f"Volume: {volume_cm3:,.2f} cm³")
            st.write(f"Volume: {data['volume_mm3']:,.0f} mm³")
            st.write(f"Source: 3D Model")
            st.write(f"File: {data['filename']}")
        
        with col2:
            st.markdown("**Dimensions**")
            st.write(f"Length: {data['length_mm']:.2f} mm")
            st.write(f"Width: {data['width_mm']:.2f} mm")
            st.write(f"Height: {data['height_mm']:.2f} mm")
            st.write(f"Watertight: {'Yes' if data['is_watertight'] else 'No'}")


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>3D Volume Calculator | Built with Streamlit | Trimesh | Plotly</p>
    <p>Export to <b>DVA (Design Volume Analyzer)</b> or use standalone</p>
</div>
""", unsafe_allow_html=True)
