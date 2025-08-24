#!/bin/bash

# Playwright Installation Script
# Sets up Playwright with all necessary browsers and dependencies

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to install system dependencies on Linux
install_linux_deps() {
    print_status "Installing system dependencies on Linux..."
    
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        sudo apt-get update
        sudo apt-get install -y \
            libnss3-dev \
            libatk-bridge2.0-dev \
            libdrm-dev \
            libxcomposite-dev \
            libxdamage-dev \
            libxrandr-dev \
            libgbm-dev \
            libxss-dev \
            libasound2-dev \
            libatspi2.0-dev \
            libgtk-3-dev \
            libgdk-pixbuf2.0-dev
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL/Fedora
        sudo yum install -y \
            nss-devel \
            atk-devel \
            libdrm-devel \
            libXcomposite-devel \
            libXdamage-devel \
            libXrandr-devel \
            mesa-libgbm-devel \
            libXScrnSaver-devel \
            alsa-lib-devel \
            at-spi2-atk-devel \
            gtk3-devel \
            gdk-pixbuf2-devel
    else
        print_warning "Could not detect package manager. You may need to install browser dependencies manually."
    fi
}

# Main installation function
main() {
    print_status "Starting Playwright installation..."
    
    local os=$(detect_os)
    print_status "Detected OS: $os"
    
    # Check Node.js version
    if ! command -v node &> /dev/null; then
        echo "Error: Node.js is required but not installed"
        echo "Please install Node.js 18 or later"
        exit 1
    fi
    
    local node_version=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$node_version" -lt 18 ]; then
        echo "Error: Node.js 18 or later is required (found v$(node -v))"
        exit 1
    fi
    
    print_success "Node.js version check passed"
    
    # Install npm dependencies
    print_status "Installing npm dependencies..."
    npm install
    
    # Install Playwright
    print_status "Installing Playwright..."
    npx playwright install
    
    # Install system dependencies for browsers
    print_status "Installing browser dependencies..."
    if [ "$os" == "linux" ]; then
        install_linux_deps
    fi
    
    # Install browsers with dependencies
    print_status "Installing browsers with system dependencies..."
    npx playwright install-deps
    
    # Verify installation
    print_status "Verifying installation..."
    npx playwright --version
    
    # Test browser installation
    print_status "Testing browser installations..."
    node -e "
        const { chromium, firefox, webkit } = require('playwright');
        
        async function testBrowsers() {
            const browsers = [
                { name: 'Chromium', browser: chromium },
                { name: 'Firefox', browser: firefox },
                { name: 'WebKit', browser: webkit }
            ];
            
            for (const { name, browser } of browsers) {
                try {
                    const instance = await browser.launch();
                    await instance.close();
                    console.log('✅', name, 'installed successfully');
                } catch (error) {
                    console.log('❌', name, 'installation failed:', error.message);
                }
            }
        }
        
        testBrowsers().then(() => {
            console.log('Browser installation test completed');
        });
    "
    
    print_success "Playwright installation completed successfully!"
    
    # Show usage information
    echo ""
    echo "=== Usage Information ==="
    echo "Run tests: npm run test"
    echo "Run tests in headed mode: npm run test:headed"  
    echo "Run tests with UI: npm run test:ui"
    echo "Run tests in debug mode: npm run test:debug"
    echo "Run Docker tests: npm run test:docker"
    echo ""
    echo "Test files location: tests/e2e/"
    echo "Configuration: playwright.config.ts"
    echo ""
    echo "For more information, visit: https://playwright.dev/"
}

# Show help
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Playwright Installation Script"
    echo ""
    echo "This script installs Playwright with all necessary browsers and dependencies."
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message"
    echo ""
    echo "The script will:"
    echo "1. Check Node.js version (requires 18+)"
    echo "2. Install npm dependencies"
    echo "3. Install Playwright"
    echo "4. Install browser dependencies (Linux only)"
    echo "5. Install browsers with system dependencies"
    echo "6. Verify installation"
    echo ""
    exit 0
fi

# Run main function
main "$@"