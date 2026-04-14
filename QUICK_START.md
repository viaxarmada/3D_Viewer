# 3D Volume Calculator - Quick Start Guide

## 📥 You've Downloaded All Files!

This guide helps you set up and run the 3D Volume Calculator.

---

## 📂 Project Structure

After extracting, you should have this structure:

```
3D_Volume_Calculator/
├── streamlit_app.py          # Main application (START HERE)
├── requirements.txt           # Python dependencies
├── README.md                  # User documentation
├── DEPLOYMENT.md              # Deployment guide
├── GITHUB_UPLOAD_GUIDE.md     # GitHub instructions
├── LICENSE                    # MIT License
├── .gitignore                 # Git configuration
├── upload_to_github.sh        # GitHub upload script
│
├── core/                      # Python modules (DON'T MODIFY)
│   ├── __init__.py
│   ├── mesh_loader.py         # Loads 3D files
│   ├── volume_calculator.py   # Calculates volume
│   ├── preview_generator.py   # 3D visualization
│   └── scale_handler.py       # Scale/resize tools
│
└── skills/                    # Developer resources
    └── 3d-model-import/
        └── SKILL.md           # Development guide
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Python Dependencies

Open terminal/command prompt in the project folder:

```bash
cd 3D_Volume_Calculator
pip install -r requirements.txt
```

**What this installs:**
- Streamlit (web framework)
- Trimesh (3D processing)
- Plotly (visualization)
- NumPy, NetworkX (dependencies)

**Time:** ~2 minutes

---

### Step 2: Run the Application

```bash
streamlit run streamlit_app.py
```

**What happens:**
- Streamlit server starts
- Browser opens automatically
- App available at: `http://localhost:8501`

**Time:** ~10 seconds

---

### Step 3: Use the App

1. **Upload Tab:** Upload 3D model (STL, 3MF, OBJ, GLB, GLTF)
2. **Scale Tab:** Adjust size if needed
3. **Export Tab:** Download results for DVA

**Done!** 🎉

---

## 📁 File Descriptions

### **Main Application**

**streamlit_app.py** (376 lines)
- Complete 3-tab Streamlit interface
- File upload & processing
- Results display
- 3D preview
- Export functionality

### **Core Modules**

**core/mesh_loader.py** (104 lines)
- Loads all 5 file formats
- Handles format detection
- 3MF unit conversion
- GLB/GLTF scene handling

**core/volume_calculator.py** (81 lines)
- Volume calculation from mesh
- Dimension extraction
- Watertight check
- Mesh statistics

**core/preview_generator.py** (141 lines)
- Interactive 3D preview with Plotly
- Professional rendering
- Camera controls
- Wireframe option

**core/scale_handler.py** (85 lines)
- Scale by factor
- Unit conversion
- Percentage scaling
- Helper functions

**core/__init__.py** (19 lines)
- Package initialization
- Export core functions

### **Documentation**

**README.md**
- User guide
- Features overview
- Troubleshooting
- Performance info

**DEPLOYMENT.md**
- Local deployment
- Docker instructions
- Streamlit Cloud setup
- Production checklist

**GITHUB_UPLOAD_GUIDE.md**
- Step-by-step GitHub upload
- Automated script usage
- Troubleshooting

**SKILL.md**
- Developer guide
- Code templates
- Error patterns
- Best practices

### **Configuration**

**requirements.txt**
- Python package list
- Version requirements

**.gitignore**
- Git exclusions
- Python cache files
- Temp directories

**LICENSE**
- MIT License
- Copyright info

**upload_to_github.sh**
- Automated GitHub upload
- Interactive prompts

---

## 🧪 Testing the App

### Test 1: Upload Simple File

1. Create or download a simple STL file
2. Upload in "Upload & Calculate" tab
3. Verify volume appears
4. Check dimensions

### Test 2: Try 3D Preview

1. After uploading file
2. Check "Show 3D Preview"
3. Rotate model with mouse
4. Verify it displays correctly

### Test 3: Scale Model

1. Go to "Scale & Adjust" tab
2. Enter scale factor: 2.0
3. Click "Apply Scale"
4. Verify volume doubles (2³ = 8x)

### Test 4: Export Data

1. Go to "Export Results" tab
2. Click "Download for DVA"
3. Verify JSON file downloads
4. Check JSON contains volume data

---

## 🔧 Installation Troubleshooting

### "pip: command not found"

**Solution:** Install Python first
- Download: https://www.python.org/downloads/
- Make sure "Add to PATH" is checked

### "ModuleNotFoundError: No module named 'streamlit'"

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### "Port 8501 already in use"

**Solution:** Use different port
```bash
streamlit run streamlit_app.py --server.port 8502
```

### "File too large" error

**Solution:** Current limit is 50 MB
- Simplify mesh in CAD software
- Or split into smaller parts

---

## 🌐 Deploying to Streamlit Cloud

### Prerequisites
1. GitHub account
2. Repository created
3. Files uploaded to GitHub

### Steps

1. **Upload to GitHub**
   ```bash
   ./upload_to_github.sh
   ```

2. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io
   - Click "New app"

3. **Configure Deployment**
   - Repository: Your GitHub repo
   - Branch: main
   - Main file: streamlit_app.py

4. **Deploy**
   - Click "Deploy"
   - Wait ~3 minutes

5. **Access**
   - Your app: https://your-app.streamlit.app

---

## 📊 Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| STL | .stl | Binary or ASCII |
| 3MF | .3mf | Auto unit conversion |
| OBJ | .obj | Material support |
| GLB | .glb | Web 3D binary |
| GLTF | .gltf | Web 3D JSON |

**Max file size:** 50 MB

---

## 💡 Tips & Best Practices

### For Best Results

1. **Use watertight meshes** (closed, no holes)
2. **Check units** before upload (3MF auto-converts)
3. **Simplify complex models** for faster processing
4. **Preview large files** after calculation (not during)

### Performance

- Small files (<1 MB): Instant
- Medium files (1-10 MB): 1-5 seconds
- Large files (10-50 MB): 5-15 seconds

### File Preparation

- Export from CAD as STL or 3MF
- Set units to millimeters
- Ensure mesh is closed (watertight)
- Simplify if >100k triangles

---

## 🔗 DVA Integration

### Workflow

1. **Calculate volume** in 3D Calculator
2. **Download JSON** from Export tab
3. **Open DVA** (separate app)
4. **Import JSON** in Primary Calculator
5. **Volume auto-populates**
6. **Continue DVA workflow**

### JSON Format

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
  "format": "STL"
}
```

---

## 📚 Additional Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Trimesh Docs:** https://trimsh.org
- **Plotly Docs:** https://plotly.com/python

---

## 🆘 Getting Help

### Common Questions

**Q: Can I use formats other than listed?**
A: Not currently. Supported: STL, 3MF, OBJ, GLB, GLTF

**Q: Why is my volume negative?**
A: Using absolute value automatically. Check mesh normals in CAD.

**Q: Preview not showing?**
A: Large meshes may take time. Check browser console for errors.

**Q: Can I batch process files?**
A: Not in current version. Upload one at a time.

---

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Run locally and test
3. ✅ Upload to GitHub
4. ✅ Deploy to Streamlit Cloud (optional)
5. ✅ Integrate with DVA (Phase 2)

---

## ✨ You're All Set!

**Everything you need is in these files. Just follow the Quick Start above!**

Questions? Check the documentation files or deployment guide.

**Happy calculating!** 🚀
