"""
3D Volume Calculator - Standalone Application
==============================================

Calculate volume and dimensions from 3D model files.
Supports: STL, 3MF, OBJ, GLB, GLTF

Export results to DVA (Design Volume Analyzer) or use standalone.
"""

import streamlit as st
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
    from core.preview_generator import create_3d_preview
    from core.scale_handler_enhanced import (
        apply_scale_factor, 
        apply_non_uniform_scale,
        apply_dimensional_scale,
        calculate_proportional_dimension,
        UNIT_CONVERSION_FACTORS
    )
except ImportError:
    # Fallback: try importing directly (if files are in same directory)
    try:
        from mesh_loader import load_3d_model
        from volume_calculator import calculate_volume_and_dimensions
        from preview_generator import create_3d_preview
        from scale_handler_enhanced import (
            apply_scale_factor,
            apply_non_uniform_scale,
            apply_dimensional_scale,
            calculate_proportional_dimension,
            UNIT_CONVERSION_FACTORS
        )
    except ImportError:
        # Try old scale_handler
        try:
            from core.scale_handler import apply_scale_factor, UNIT_CONVERSION_FACTORS
            # Define missing functions as fallbacks
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
            
            Cannot find required modules. Please check:
            
            1. **Folder structure on GitHub:**
               - streamlit_app.py (root)
               - core/ folder with:
                 - __init__.py
                 - mesh_loader.py
                 - volume_calculator.py
                 - preview_generator.py
                 - scale_handler_enhanced.py
            
            2. **All files uploaded to GitHub**
            
            3. **Try redeploying on Streamlit Cloud**
            
            Error details: {str(e)}
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
if 'scale_factor' not in st.session_state:
    st.session_state.scale_factor = 1.0
if 'original_dimensions' not in st.session_state:
    st.session_state.original_dimensions = None
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'proportional_scaling' not in st.session_state:
    st.session_state.proportional_scaling = True

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

# Main content
tab1, tab2, tab3 = st.tabs(["📁 Upload & Calculate", "🔧 Scale & Adjust", "📤 Export Results"])

# ═══════════════════════════════════════════════════════════════════
# TAB 1: UPLOAD & CALCULATE
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
                    st.session_state.scaled_mesh = mesh
                    st.session_state.scale_factor = 1.0
                    
                    # Store original dimensions for dimensional editing
                    st.session_state.original_dimensions = {
                        'length': calc_result['length_mm'],
                        'width': calc_result['width_mm'],
                        'height': calc_result['height_mm']
                    }
                    
                    st.success(f"✅ Model loaded: {uploaded_file.name}")
                else:
                    st.error(f"❌ Error: {mesh_result['error']}")
                    
        except Exception as e:
            st.error(f"❌ Error loading model: {str(e)}")
    
    # Display results if model loaded
    if st.session_state.model_data:
        st.markdown("---")
        st.header("📊 Calculated Results")
        
        data = st.session_state.model_data
        
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
        
        # 3D Preview
        st.markdown("---")
        if st.checkbox("🎨 Show 3D Preview", value=False):
            try:
                with st.spinner("Generating 3D preview..."):
                    fig = create_3d_preview(st.session_state.scaled_mesh)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error generating preview: {str(e)}")
    else:
        st.info("👆 Upload a 3D model to get started")


# ═══════════════════════════════════════════════════════════════════
# TAB 2: SCALE & ADJUST
# ═══════════════════════════════════════════════════════════════════

with tab2:
    st.header("🔧 Scale & Resize Model")
    
    if st.session_state.model_data is None:
        st.info("Upload a 3D model first (see Upload & Calculate tab)")
    else:
        st.markdown("""
        Adjust the model using:
        - **Scale Factor:** Uniform scaling (proportional)
        - **Unit Conversion:** Change measurement units
        - **Dimensional Editing:** Set exact dimensions (proportional or distorted)
        """)
        
        st.markdown("---")
        
        # Scale method selection
        scale_method = st.radio(
            "Scaling Method:",
            ["Scale Factor", "Unit Conversion", "Edit Dimensions"],
            horizontal=True
        )
        
        # ═══════════════════════════════════════════════════════════════
        # METHOD 1: SCALE FACTOR
        # ═══════════════════════════════════════════════════════════════
        
        if scale_method == "Scale Factor":
            st.markdown("**Uniform Scale Factor**")
            st.markdown("Enter a multiplier (1.0 = no change, 2.0 = double, 0.5 = half)")
            
            scale_factor = st.number_input(
                "Scale factor",
                min_value=0.01,
                max_value=100.0,
                value=1.0,
                step=0.1,
                format="%.2f",
                key="scale_factor_input"
            )
            
            percentage = scale_factor * 100
            st.caption(f"= {percentage:.0f}% of current size")
            
            if st.button("✓ Apply Scale Factor", use_container_width=True, type="primary"):
                try:
                    import copy
                    # Apply uniform scale
                    scaled_mesh = copy.deepcopy(st.session_state.scaled_mesh)
                    scaled_mesh = apply_scale_factor(scaled_mesh, scale_factor)
                    
                    # Recalculate
                    calc_result = calculate_volume_and_dimensions(scaled_mesh)
                    
                    # Update session state
                    st.session_state.model_data.update(calc_result)
                    st.session_state.scaled_mesh = scaled_mesh
                    
                    st.success(f"✅ Scale applied: {scale_factor:.2f}x")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error applying scale: {str(e)}")
        
        # ═══════════════════════════════════════════════════════════════
        # METHOD 2: UNIT CONVERSION
        # ═══════════════════════════════════════════════════════════════
        
        elif scale_method == "Unit Conversion":
            st.markdown("**Unit Conversion**")
            st.markdown("Specify what units the file is actually in")
            
            from_unit = st.selectbox(
                "File is in:",
                ["millimeters", "centimeters", "inches", "meters"],
                index=0,
                key="unit_conversion_select"
            )
            
            to_unit = "millimeters"
            
            conversion_factor = UNIT_CONVERSION_FACTORS[from_unit]
            
            st.caption(f"Will multiply by {conversion_factor} to convert to mm")
            
            if st.button("✓ Apply Unit Conversion", use_container_width=True, type="primary"):
                try:
                    import copy
                    # Apply conversion
                    scaled_mesh = copy.deepcopy(st.session_state.scaled_mesh)
                    scaled_mesh = apply_scale_factor(scaled_mesh, conversion_factor)
                    
                    # Recalculate
                    calc_result = calculate_volume_and_dimensions(scaled_mesh)
                    
                    # Update session state
                    st.session_state.model_data.update(calc_result)
                    st.session_state.scaled_mesh = scaled_mesh
                    
                    st.success(f"✅ Converted from {from_unit} to {to_unit}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error converting units: {str(e)}")
        
        # ═══════════════════════════════════════════════════════════════
        # METHOD 3: DIMENSIONAL EDITING (NEW!)
        # ═══════════════════════════════════════════════════════════════
        
        elif scale_method == "Edit Dimensions":
            st.markdown("**Edit Dimensions Directly**")
            st.markdown("Set exact dimensions in millimeters")
            
            # Current dimensions
            data = st.session_state.model_data
            current_length = data['length_mm']
            current_width = data['width_mm']
            current_height = data['height_mm']
            
            # Proportional scaling checkbox
            proportional = st.checkbox(
                "🔗 Proportional Scaling",
                value=True,
                help="When checked, changing one dimension scales others proportionally. When unchecked, allows distortion."
            )
            
            st.markdown("---")
            
            # Dimension editing section
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📏 Length (X)**")
                new_length = st.number_input(
                    "Length (mm)",
                    min_value=0.01,
                    max_value=10000.0,
                    value=float(current_length),
                    step=0.1,
                    format="%.2f",
                    key="edit_length",
                    label_visibility="collapsed"
                )
                st.caption(f"Current: {current_length:.2f} mm")
            
            with col2:
                st.markdown("**📏 Width (Y)**")
                
                # If proportional and length changed, calculate proportional width
                if proportional and new_length != current_length:
                    proportional_width = calculate_proportional_dimension(
                        new_length, current_length, current_width
                    )
                    new_width = st.number_input(
                        "Width (mm)",
                        min_value=0.01,
                        max_value=10000.0,
                        value=float(proportional_width),
                        step=0.1,
                        format="%.2f",
                        key="edit_width",
                        label_visibility="collapsed",
                        disabled=True  # Disabled when proportional
                    )
                else:
                    new_width = st.number_input(
                        "Width (mm)",
                        min_value=0.01,
                        max_value=10000.0,
                        value=float(current_width),
                        step=0.1,
                        format="%.2f",
                        key="edit_width",
                        label_visibility="collapsed"
                    )
                st.caption(f"Current: {current_width:.2f} mm")
            
            with col3:
                st.markdown("**📏 Height (Z)**")
                
                # If proportional and length changed, calculate proportional height
                if proportional and new_length != current_length:
                    proportional_height = calculate_proportional_dimension(
                        new_length, current_length, current_height
                    )
                    new_height = st.number_input(
                        "Height (mm)",
                        min_value=0.01,
                        max_value=10000.0,
                        value=float(proportional_height),
                        step=0.1,
                        format="%.2f",
                        key="edit_height",
                        label_visibility="collapsed",
                        disabled=True  # Disabled when proportional
                    )
                else:
                    new_height = st.number_input(
                        "Height (mm)",
                        min_value=0.01,
                        max_value=10000.0,
                        value=float(current_height),
                        step=0.1,
                        format="%.2f",
                        key="edit_height",
                        label_visibility="collapsed"
                    )
                st.caption(f"Current: {current_height:.2f} mm")
            
            # Show scale factors that will be applied
            st.markdown("---")
            st.markdown("**Preview Changes:**")
            
            x_scale = new_length / current_length if current_length > 0 else 1.0
            y_scale = new_width / current_width if current_width > 0 else 1.0
            z_scale = new_height / current_height if current_height > 0 else 1.0
            
            # Calculate new volume estimate
            volume_scale = x_scale * y_scale * z_scale
            estimated_volume = data['volume_mm3'] * volume_scale
            estimated_volume_cm3 = estimated_volume / 1000
            
            col_preview1, col_preview2, col_preview3 = st.columns(3)
            
            with col_preview1:
                st.metric(
                    "Length Change",
                    f"{new_length:.2f} mm",
                    f"{(x_scale - 1) * 100:+.1f}%"
                )
            
            with col_preview2:
                st.metric(
                    "Width Change",
                    f"{new_width:.2f} mm",
                    f"{(y_scale - 1) * 100:+.1f}%"
                )
            
            with col_preview3:
                st.metric(
                    "Height Change",
                    f"{new_height:.2f} mm",
                    f"{(z_scale - 1) * 100:+.1f}%"
                )
            
            # Volume preview
            st.markdown("**Estimated New Volume:**")
            current_vol_cm3 = data['volume_mm3'] / 1000
            st.metric(
                "Volume",
                f"{estimated_volume_cm3:.2f} cm³",
                f"{(volume_scale - 1) * 100:+.1f}%"
            )
            
            # Warning if non-proportional
            if not proportional and (x_scale != y_scale or y_scale != z_scale or x_scale != z_scale):
                st.warning("⚠️ **Non-proportional scaling will distort the model!** The shape will change.")
            
            # Apply button
            if st.button("✓ Apply Dimensions", use_container_width=True, type="primary"):
                try:
                    import copy
                    # Apply dimensional scale
                    scaled_mesh = copy.deepcopy(st.session_state.scaled_mesh)
                    
                    current_dims = {
                        'length': current_length,
                        'width': current_width,
                        'height': current_height
                    }
                    
                    target_dims = {
                        'length': new_length,
                        'width': new_width,
                        'height': new_height
                    }
                    
                    scaled_mesh, scales = apply_dimensional_scale(
                        scaled_mesh,
                        current_dims,
                        target_dims,
                        proportional=proportional
                    )
                    
                    # Recalculate volume
                    calc_result = calculate_volume_and_dimensions(scaled_mesh)
                    
                    # Update session state
                    st.session_state.model_data.update(calc_result)
                    st.session_state.scaled_mesh = scaled_mesh
                    
                    scaling_type = "proportionally" if proportional else "non-proportionally (distorted)"
                    st.success(f"✅ Dimensions applied {scaling_type}!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error applying dimensions: {str(e)}")
        
        # ═══════════════════════════════════════════════════════════════
        # CURRENT VALUES DISPLAY (All Methods)
        # ═══════════════════════════════════════════════════════════════
        
        st.markdown("---")
        st.markdown("### 📊 Current Model Values")
        
        data = st.session_state.model_data
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


# ═══════════════════════════════════════════════════════════════════
# TAB 3: EXPORT RESULTS
# ═══════════════════════════════════════════════════════════════════

with tab3:
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
            'scale_factor': st.session_state.scale_factor,
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
