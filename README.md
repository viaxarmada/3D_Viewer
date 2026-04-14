# 3D Volume Calculator

**Calculate accurate volumes and dimensions from 3D model files**

Upload STL, 3MF, OBJ, GLB, or GLTF files to instantly calculate volume, dimensions, and preview your 3D model. Export results to DVA (Design Volume Analyzer) or use standalone.

---

## ✨ Features

- 📁 **Multi-format support**: STL, 3MF, OBJ, GLB, GLTF
- 📐 **Accurate calculations**: Exact volume from mesh geometry
- 🎨 **3D Preview**: Interactive visualization with Plotly
- 🔧 **Scale & resize**: Adjust model scale and units
- 📤 **Export to DVA**: JSON export for integration
- 🚀 **Fast processing**: Up to 50 MB file size

---

## 🚀 Quick Start

### Installation

```bash
# Clone or navigate to directory
cd 3D_Volume_Calculator

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📖 Usage

### 1. Upload Model

- Click "Browse files" or drag & drop
- Supported formats: STL, 3MF, OBJ, GLB, GLTF
- Max file size: 50 MB

### 2. View Results

**Calculated automatically:**
- Volume (cm³ and mm³)
- Dimensions (L × W × H in mm)
- Mesh quality (watertight check)
- File information

### 3. Scale (Optional)

**Adjust if needed:**
- Scale by factor (2.0 = double, 0.5 = half)
- Convert units (inches → mm, cm → mm, etc.)

### 4. Export

**For DVA integration:**
- Download JSON file
- Import into DVA Primary Calculator
- Volume auto-populates

---

## 🔗 DVA Integration

### Method 1: JSON Export (Phase 1)

1. Calculate volume in 3D Volume Calculator
2. Click "Download for DVA (.json)"
3. In DVA → Primary Calculator → "Import from 3D Model"
4. Upload JSON file
5. Volume auto-fills

### Method 2: Direct Link (Phase 1)

Run both apps simultaneously:

```bash
# Terminal 1: Run 3D Calculator
streamlit run streamlit_app.py --server.port 8502

# Terminal 2: Run DVA
cd ../DVA_Modernized
streamlit run streamlit_app.py --server.port 8501
```

Access:
- DVA: `http://localhost:8501`
- 3D Calculator: `http://localhost:8502`

---

## 📂 Project Structure

```
3D_Volume_Calculator/
├── streamlit_app.py          # Main application
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── core/                      # Core modules
│   ├── __init__.py
│   ├── mesh_loader.py         # Load 3D files
│   ├── volume_calculator.py   # Calculate volume
│   ├── preview_generator.py   # 3D visualization
│   └── scale_handler.py       # Resize/scale
│
└── skills/                    # Development resources
    └── 3d-model-import/
        └── SKILL.md           # Complete guide
```

---

## 🎯 Supported Formats

| Format | Extension | Type | Use Case |
|--------|-----------|------|----------|
| **STL** | `.stl` | Binary/ASCII | Universal 3D printing |
| **3MF** | `.3mf` | ZIP | Modern 3D printing, includes units |
| **OBJ** | `.obj` | Text | Universal interchange |
| **GLB** | `.glb` | Binary | Web 3D, AR/VR |
| **GLTF** | `.gltf` | JSON | Web 3D, "JPEG of 3D" |

---

## 🔧 Technical Details

### Volume Calculation

**Method:** Signed volume from triangle mesh
- For watertight meshes: Exact volume
- For non-watertight: Bounding box approximation
- Always uses absolute value (handles inverted normals)

### Units

**Default:** Millimeters (mm)

**Supported conversions:**
- Millimeters ↔ Centimeters ↔ Inches ↔ Meters

**3MF files:** Auto-detects and converts from metadata

### File Size Limits

- Maximum: 50 MB
- Typical sizes:
  - Simple part: 0.1 - 5 MB
  - Complex assembly: 5 - 50 MB

---

## 📊 Export Format

### JSON Structure

```json
{
  "volume_mm3": 125430.0,
  "volume_cm3": 125.43,
  "dimensions_mm": {
    "length": 85.2,
    "width": 62.4,
    "height": 41.8
  },
  "source": "3D_MODEL",
  "filename": "product.stl",
  "format": "STL",
  "is_watertight": true,
  "mesh_info": {
    "triangles": 5234,
    "vertices": 2618
  },
  "scale_factor": 1.0,
  "timestamp": "2026-04-13T18:30:00"
}
```

---

## 🐛 Troubleshooting

### "File too large" error
- **Solution:** Simplify mesh in CAD software
- Or split into smaller parts

### "File contains no geometry"
- **Solution:** Check that file is valid 3D model
- Re-export from CAD software

### Wrong volume calculation
- **Check units:** File may be in inches, not mm
- **Solution:** Use "Scale & Adjust" tab → Unit conversion

### Volume seems approximate
- **Cause:** Mesh is not watertight (has holes)
- **Note:** App uses bounding box approximation
- **Solution:** Fix mesh in CAD software for exact volume

---

## 🔮 Roadmap

### Phase 1 (Current)
- ✅ 5 file format support
- ✅ Volume calculation
- ✅ 3D preview
- ✅ Scale/resize
- ✅ JSON export for DVA

### Phase 2 (Next)
- 🔄 DVA direct integration (Python module)
- 🔄 Mesh repair tools
- 🔄 Batch processing

### Phase 3 (Future)
- 📋 Additional formats (STEP, IGES)
- 📋 Cloud storage
- 📋 Model library

---

## 📚 Documentation

- **Skill Guide:** `skills/3d-model-import/SKILL.md`
- **API Reference:** See core module docstrings
- **DVA Integration:** See DVA project README

---

## 🤝 Integration with DVA

This tool is designed to work with **DVA (Design Volume Analyzer)** for packaging analysis.

**Workflow:**
1. Calculate volume here (exact from 3D model)
2. Export to DVA
3. DVA uses volume for packaging analysis

**Standalone use:** Tool also works independently for any volume calculation needs.

---

## ⚡ Performance

**Typical processing times:**
- Small file (<1 MB): < 1 second
- Medium file (1-10 MB): 1-5 seconds
- Large file (10-50 MB): 5-15 seconds

**3D Preview:**
- Fast for simple meshes (<10k triangles)
- May take 5-10s for complex meshes (>100k triangles)

---

## 💻 Requirements

- Python 3.8+
- Streamlit 1.28+
- Trimesh 3.20+
- Plotly 5.14+
- 2 GB RAM minimum
- Modern web browser

---

## 📝 License

Part of the DVA project suite.

---

## 🆘 Support

For issues or questions:
1. Check troubleshooting section above
2. Review skill guide: `skills/3d-model-import/SKILL.md`
3. Check DVA documentation

---

## 🎉 Credits

**Built with:**
- [Streamlit](https://streamlit.io/) - Web framework
- [Trimesh](https://trimsh.org/) - 3D mesh processing
- [Plotly](https://plotly.com/) - Interactive visualization
- [NumPy](https://numpy.org/) - Numerical computing

**Created for:** DVA (Design Volume Analyzer) integration

---

**Ready to calculate volumes from your 3D models!** 🚀
