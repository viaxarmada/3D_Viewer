# Deployment Guide - 3D Volume Calculator

## Local Development

### Setup

```bash
# Navigate to project
cd 3D_Volume_Calculator

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Locally

```bash
# Run on default port (8501)
streamlit run streamlit_app.py

# Run on custom port
streamlit run streamlit_app.py --server.port 8502

# Run alongside DVA
# Terminal 1:
streamlit run streamlit_app.py --server.port 8502

# Terminal 2:
cd ../DVA_Modernized
streamlit run streamlit_app.py --server.port 8501
```

---

## Streamlit Community Cloud

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: 3D Volume Calculator"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Main file: `streamlit_app.py`
   - Click "Deploy"

3. **Configuration**
   - Python version: 3.9+
   - Requirements auto-detected from `requirements.txt`

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build & Run

```bash
# Build image
docker build -t 3d-volume-calculator .

# Run container
docker run -p 8501:8501 3d-volume-calculator

# Run with volume (for data persistence)
docker run -p 8501:8501 -v $(pwd)/data:/app/data 3d-volume-calculator
```

---

## Environment Variables

### Optional Configuration

```bash
# .streamlit/config.toml
[server]
port = 8502
headless = true
enableCORS = false

[theme]
primaryColor = "#0066CC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[browser]
gatherUsageStats = false
```

---

## Performance Optimization

### For Large Files

```toml
# .streamlit/config.toml
[server]
maxUploadSize = 50  # MB
enableXsrfProtection = true

[runner]
maxMessageSize = 200  # MB
```

### Memory Management

```bash
# Increase memory limit
streamlit run streamlit_app.py --server.maxUploadSize=50
```

---

## Monitoring

### Basic Health Check

```python
# Add to streamlit_app.py (optional)
import time

if st.checkbox("Show Performance Metrics", value=False):
    start_time = time.time()
    # ... processing ...
    elapsed = time.time() - start_time
    st.info(f"Processing time: {elapsed:.2f}s")
```

---

## Security

### File Validation

Already implemented:
- ✅ File size limit (50 MB)
- ✅ Format validation
- ✅ Temp file cleanup
- ✅ Error handling

### Recommended

```bash
# Run with HTTPS (production)
streamlit run streamlit_app.py --server.sslCertFile=cert.pem --server.sslKeyFile=key.pem
```

---

## Backup & Data

### No Persistent Data

App is stateless:
- No database required
- Files processed in memory
- Temp files auto-cleaned
- Session state only

### Export Data

Users download:
- JSON export files
- Results stored client-side

---

## Troubleshooting

### Port Already in Use

```bash
# Find process
lsof -i :8501

# Kill process
kill -9 <PID>

# Or use different port
streamlit run streamlit_app.py --server.port 8502
```

### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Memory Issues

```bash
# Increase Python memory
export PYTHONMAXMEMORY=4096

# Or restart app periodically (for continuous use)
```

---

## Production Checklist

- [ ] Dependencies installed (`requirements.txt`)
- [ ] App runs locally without errors
- [ ] File upload works (all 5 formats)
- [ ] Volume calculation accurate
- [ ] 3D preview displays
- [ ] Scale/resize works
- [ ] JSON export downloads
- [ ] Performance acceptable (<15s for 50MB)
- [ ] Error messages helpful
- [ ] Documentation complete

---

## Scaling

### For High Traffic

**Option 1: Streamlit Cloud (easiest)**
- Auto-scaling
- No server management
- Free tier available

**Option 2: Cloud Provider**
- AWS/GCP/Azure
- Container orchestration
- Load balancing

**Option 3: Local Server**
- NGINX reverse proxy
- Multiple instances
- Process manager (PM2, supervisord)

---

## Updates & Maintenance

### Update Dependencies

```bash
# Check outdated
pip list --outdated

# Update specific package
pip install --upgrade trimesh

# Update all
pip install -r requirements.txt --upgrade
```

### Version Control

```bash
# Tag releases
git tag -a v1.0.0 -m "Phase 1 Release"
git push origin v1.0.0
```

---

## Integration with DVA

### Same Server

```bash
# Run both apps
# Terminal 1:
cd 3D_Volume_Calculator
streamlit run streamlit_app.py --server.port 8502

# Terminal 2:
cd DVA_Modernized
streamlit run streamlit_app.py --server.port 8501
```

### Different Servers

**3D Calculator:** `https://3d-calc.yourcompany.com`
**DVA:** `https://dva.yourcompany.com`

Users manually transfer JSON files between apps.

---

## Support

For deployment issues:
1. Check Streamlit docs: https://docs.streamlit.io
2. Review error logs
3. Test locally first
4. Check resource limits

---

**Ready to deploy!** 🚀
