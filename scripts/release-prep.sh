#!/bin/bash

# ============================================
# AI Dungeon Master - Release Preparation
# ============================================
# Run this script before creating a GitHub release

set -e  # Exit on error

echo "🎲 AI Dungeon Master - Release Prep v1.1.0"
echo "=========================================="
echo ""

# Check Python dependencies
echo "✓ Checking Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

# Check core files exist
echo "✓ Checking core files..."
required_files=(
    "README.md"
    "ROLL20_GUIDE.md"
    "CHANGELOG.md"
    "LICENSE"
    "server/main.py"
    "server/roll20_adapter.py"
    "roll20/aidm-roll20.js"
    "relay/roll20-relay.html"
    "roll20/macros.example"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing: $file"
        exit 1
    fi
done

echo "✓ All core files present"
echo ""

# Validate Python syntax
echo "✓ Validating Python syntax..."
python3 -m py_compile server/*.py || {
    echo "❌ Python syntax errors found"
    exit 1
}
echo "✓ Python syntax valid"
echo ""

# Check for common issues
echo "✓ Checking for common issues..."

# Check for TODO or FIXME comments
if grep -r "TODO\|FIXME" server/ --include="*.py" | grep -v "# TODO (optional)"; then
    echo "⚠️  Warning: Found TODO/FIXME comments in code"
    echo "   Review before release"
fi

# Check for hardcoded localhost URLs (except in relay HTML which is configurable)
if grep -r "localhost" server/ --include="*.py"; then
    echo "⚠️  Warning: Found localhost references in server code"
    echo "   Ensure these are environment-configurable"
fi

echo ""
echo "✓ Pre-release checks complete"
echo ""

# Generate release checklist
echo "📋 Release Checklist:"
echo "===================="
echo ""
echo "Before pushing to GitHub:"
echo "  [ ] Update version numbers in:"
echo "      - CHANGELOG.md"
echo "      - server/roll20_adapter.py (health check)"
echo "  [ ] Test Roll20 integration locally"
echo "  [ ] Test relay page with backend"
echo "  [ ] Review all documentation for accuracy"
echo "  [ ] Add actual screenshots to screenshots/"
echo ""
echo "After pushing:"
echo "  [ ] Create GitHub Release (tag: v1.1.0)"
echo "  [ ] Update deployed backend (Render/Fly.io)"
echo "  [ ] Test with live Roll20 game"
echo "  [ ] Announce in GitHub Discussions"
echo "  [ ] Update Roll20 forums/communities (if applicable)"
echo ""
echo "Optional:"
echo "  [ ] Create demo video"
echo "  [ ] Write blog post"
echo "  [ ] Share on r/Roll20 subreddit"
echo "  [ ] Cross-post to r/RPG, r/DnD"
echo ""
echo "🚀 Ready to release!"
echo ""
echo "Next steps:"
echo "  git add ."
echo "  git commit -m 'Release v1.1.0: Roll20 Integration'"
echo "  git tag v1.1.0"
echo "  git push origin main --tags"
