#!/bin/bash
# Setup script for IBM Cloud Native Ansible Collection

set -e

echo "=========================================="
echo "IBM Cloud Native Ansible Collection Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.10 or higher is required. Found: $python_version"
    exit 1
fi
echo "✓ Python $python_version detected"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "build/venv" ]; then
    echo "Creating virtual environment..."
    mkdir -p build
    python3 -m venv build/venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source build/venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo "✓ Dependencies installed from requirements.txt"
else
    echo "Warning: requirements.txt not found"
fi
echo ""


echo ""

# Set up Ansible collection path
echo "Setting up Ansible collection..."
ANSIBLE_COLLECTIONS_PATH="${HOME}/.ansible/collections/ansible_collections/ibm/cloudcollection"
mkdir -p "$ANSIBLE_COLLECTIONS_PATH"

# Create symlinks for plugins
ln -sf "$(pwd)/plugins" "$ANSIBLE_COLLECTIONS_PATH/plugins" 2>/dev/null || true
echo "✓ Ansible collection path configured"
echo ""

# Verify installation
echo "Verifying installation..."
python3 -c "import ibm_cloud_sdk_core; print('✓ ibm-cloud-sdk-core installed')"
python3 -c "import ibm_vpc; print('✓ ibm-vpc installed')"
python3 -c "import ansible; print('✓ ansible-core installed')"
echo ""

# Display environment information
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Environment Information:"
echo "  Python: $(python3 --version)"
echo "  Virtual Environment: $(pwd)/build/venv"
echo "  Ansible Collections: $ANSIBLE_COLLECTIONS_PATH"
echo ""
echo "To activate the environment:"
echo "  source build/venv/bin/activate"
echo ""
echo "To test the collection:"
echo "  ansible-playbook examples/create_vpc_infrastructure.yml --check"
echo ""
echo "Set your IBM Cloud API key:"
echo "  export IC_API_KEY='your-api-key-here'"
echo ""
echo "=========================================="
