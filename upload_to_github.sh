#!/bin/bash

# 3D Volume Calculator - GitHub Upload Script
# =============================================

echo "🚀 3D Volume Calculator - GitHub Upload"
echo "========================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is not installed"
    echo "Install git first: https://git-scm.com/downloads"
    exit 1
fi

# Get GitHub username
echo "Enter your GitHub username:"
read username

# Get repository name
echo "Enter repository name (e.g., 3D-Volume-Calculator):"
read repo_name

echo ""
echo "📋 Summary:"
echo "  GitHub URL: https://github.com/$username/$repo_name"
echo ""
echo "⚠️  Make sure you've created this repository on GitHub first!"
echo "   Go to: https://github.com/new"
echo ""
read -p "Ready to proceed? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Initialize git if needed
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✓ Git initialized"
fi

# Add all files
echo "📝 Adding files..."
git add .
echo "✓ Files added"

# Commit
echo "💾 Creating commit..."
git commit -m "Initial commit: 3D Volume Calculator - Phase 1 complete

Features:
- 5 file format support (STL, 3MF, OBJ, GLB, GLTF)
- Accurate volume calculation
- Interactive 3D preview
- Scale and resize tools
- Export to DVA (JSON)
- Complete documentation"
echo "✓ Commit created"

# Add remote
echo "🔗 Adding GitHub remote..."
git remote remove origin 2>/dev/null  # Remove if exists
git remote add origin "https://github.com/$username/$repo_name.git"
echo "✓ Remote added"

# Rename branch to main
echo "🌿 Setting branch to main..."
git branch -M main
echo "✓ Branch set"

# Push
echo "⬆️  Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Your project is now on GitHub!"
    echo ""
    echo "🌐 View at: https://github.com/$username/$repo_name"
    echo ""
    echo "Next steps:"
    echo "  1. Add repository description on GitHub"
    echo "  2. Add topics: 3d-models, volume-calculation, streamlit"
    echo "  3. Consider deploying to Streamlit Cloud"
    echo ""
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "  1. Repository doesn't exist - create it first at https://github.com/new"
    echo "  2. Authentication failed - set up GitHub credentials"
    echo "  3. Permission denied - check repository access"
    echo ""
    echo "See GITHUB_UPLOAD_GUIDE.md for detailed troubleshooting"
fi
