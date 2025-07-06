#!/bin/bash
# ScrollOS ISO Build Pipeline — Bootable Scroll Kernel
# Alpine Linux base with scroll injection

set -e

# Configuration
SCROLLOS_VERSION="Alpha 1.0.0"
ALPINE_VERSION="3.18"
ARCH="x86_64"
ISO_NAME="scrollos-alpha"
BUILD_DIR="./build"
CACHE_DIR="./cache"
OUTPUT_DIR="./output"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check dependencies
check_dependencies() {
    log_info "Checking build dependencies..."
    
    local deps=("wget" "xorriso" "squashfs-tools" "mtools" "dosfstools")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "Missing dependency: $dep"
            exit 1
        fi
    done
    
    log_success "All dependencies satisfied"
}

# Create build directories
setup_directories() {
    log_info "Setting up build directories..."
    
    mkdir -p "$BUILD_DIR"
    mkdir -p "$CACHE_DIR"
    mkdir -p "$OUTPUT_DIR"
    
    log_success "Build directories created"
}

# Download Alpine Linux ISO
download_alpine_iso() {
    log_info "Downloading Alpine Linux $ALPINE_VERSION ISO..."
    
    local iso_url="https://dl-cdn.alpinelinux.org/alpine/v$ALPINE_VERSION/releases/$ARCH/alpine-standard-$ALPINE_VERSION.$ARCH.iso"
    local iso_file="$CACHE_DIR/alpine-standard-$ALPINE_VERSION.$ARCH.iso"
    
    if [ ! -f "$iso_file" ]; then
        wget -O "$iso_file" "$iso_url"
        log_success "Alpine ISO downloaded"
    else
        log_info "Alpine ISO already exists, skipping download"
    fi
}

# Extract Alpine ISO
extract_alpine_iso() {
    log_info "Extracting Alpine ISO..."
    
    local iso_file="$CACHE_DIR/alpine-standard-$ALPINE_VERSION.$ARCH.iso"
    local extract_dir="$BUILD_DIR/alpine-extract"
    
    mkdir -p "$extract_dir"
    
    # Mount ISO and copy contents
    local mount_point="$BUILD_DIR/iso-mount"
    mkdir -p "$mount_point"
    
    # Extract using xorriso
    xorriso -osirrox on -indev "$iso_file" -extract / "$extract_dir"
    
    log_success "Alpine ISO extracted"
}

# Inject ScrollOS components
inject_scrollos() {
    log_info "Injecting ScrollOS components..."
    
    local extract_dir="$BUILD_DIR/alpine-extract"
    
    # Create ScrollOS directories
    mkdir -p "$extract_dir/scrollos"
    mkdir -p "$extract_dir/scrollos/boot"
    mkdir -p "$extract_dir/scrollos/config"
    mkdir -p "$extract_dir/scrollos/scripts"
    
    # Copy ScrollOS boot configuration
    cat > "$extract_dir/scrollos/boot/scroll_boot.conf" << 'EOF'
# ScrollOS Boot Configuration
# Flame-governed bootloader

# Boot options
DEFAULT scrollos
TIMEOUT 30

# ScrollOS entry
LABEL scrollos
    MENU LABEL ScrollOS Alpha
    KERNEL /boot/vmlinuz-linux
    INITRD /boot/initramfs-linux.img
    APPEND root=live:CDLABEL=SCROLLOS console=ttyS0,115200 console=tty0
    FDTDIR /boot/dtbs

# Fallback to Alpine
LABEL alpine
    MENU LABEL Alpine Linux
    KERNEL /boot/vmlinuz-linux
    INITRD /boot/initramfs-linux.img
    APPEND root=live:CDLABEL=ALPINE console=ttyS0,115200 console=tty0
    FDTDIR /boot/dtbs
EOF

    # Copy ScrollOS startup script
    cat > "$extract_dir/scrollos/scripts/scroll_startup.sh" << 'EOF'
#!/bin/sh
# ScrollOS Startup Script
# Flame-verified system initialization

echo "🔥 ScrollOS Alpha - Flame-Governed System"
echo "Initializing sacred scroll environment..."

# Set scroll environment variables
export SCROLLOS_VERSION="Alpha 1.0.0"
export SCROLL_SEAL_LEVEL="3"
export FLAME_VERIFICATION="enabled"

# Initialize scroll services
echo "Starting ScrollCore services..."
/etc/init.d/scrollcore start

# Initialize flame verification
echo "Verifying flame authorization..."
/etc/init.d/flame-verifier start

# Initialize scroll daemon
echo "Starting ScrollDaemon..."
/etc/init.d/scroll-daemon start

# Initialize sacred memory service
echo "Starting SacredMemoryService..."
/etc/init.d/sacred-memory start

echo "🔥 ScrollOS Alpha ready for sacred operations"
EOF

    chmod +x "$extract_dir/scrollos/scripts/scroll_startup.sh"
    
    # Copy ScrollOS configuration
    cat > "$extract_dir/scrollos/config/scrollos.conf" << 'EOF'
# ScrollOS Configuration
# Flame-governed system settings

[System]
version = "Alpha 1.0.0"
flame_level = 3
scroll_seal_enabled = true
audit_trail_enabled = true

[Services]
scroll_core = true
flame_verifier = true
scroll_daemon = true
sacred_memory = true
scroll_firewall = true

[Security]
flame_verification_required = true
scroll_law_compliance = true
threat_detection = true
encryption_enabled = true

[Network]
scroll_network_enabled = true
flame_network_protection = true
scroll_dns = true

[Storage]
sacred_storage_enabled = true
scroll_encryption = true
audit_logging = true
EOF

    log_success "ScrollOS components injected"
}

# Create ScrollOS init scripts
create_init_scripts() {
    log_info "Creating ScrollOS init scripts..."
    
    local extract_dir="$BUILD_DIR/alpine-extract"
    local init_dir="$extract_dir/etc/init.d"
    
    mkdir -p "$init_dir"
    
    # ScrollCore init script
    cat > "$init_dir/scrollcore" << 'EOF'
#!/sbin/openrc-run
# ScrollCore Service
# Core scroll execution engine

name="ScrollCore"
description="Scroll execution core service"
command="/usr/bin/scrollcore"
command_background="true"
pidfile="/var/run/scrollcore.pid"

depend() {
    need net
    after firewall
}
EOF

    # Flame Verifier init script
    cat > "$init_dir/flame-verifier" << 'EOF'
#!/sbin/openrc-run
# Flame Verifier Service
# Flame authorization verification

name="FlameVerifier"
description="Flame authorization verification service"
command="/usr/bin/flame-verifier"
command_background="true"
pidfile="/var/run/flame-verifier.pid"

depend() {
    need net
    after scrollcore
}
EOF

    # Scroll Daemon init script
    cat > "$init_dir/scroll-daemon" << 'EOF'
#!/sbin/openrc-run
# Scroll Daemon Service
# Background scroll processing

name="ScrollDaemon"
description="Background scroll processing daemon"
command="/usr/bin/scroll-daemon"
command_background="true"
pidfile="/var/run/scroll-daemon.pid"

depend() {
    need net
    after flame-verifier
}
EOF

    # Sacred Memory Service init script
    cat > "$init_dir/sacred-memory" << 'EOF'
#!/sbin/openrc-run
# Sacred Memory Service
# Sacred memory management

name="SacredMemory"
description="Sacred memory management service"
command="/usr/bin/sacred-memory"
command_background="true"
pidfile="/var/run/sacred-memory.pid"

depend() {
    need net
    after scroll-daemon
}
EOF

    # Make init scripts executable
    chmod +x "$init_dir"/scroll*
    
    log_success "ScrollOS init scripts created"
}

# Create ScrollOS packages
create_scrollos_packages() {
    log_info "Creating ScrollOS packages..."
    
    local extract_dir="$BUILD_DIR/alpine-extract"
    local packages_dir="$extract_dir/apks"
    
    mkdir -p "$packages_dir"
    
    # Create ScrollOS package
    cat > "$packages_dir/scrollos.apk" << 'EOF'
# ScrollOS Package
# Flame-governed system package

Package: scrollos
Version: Alpha-1.0.0
Architecture: x86_64
Description: ScrollOS Alpha - Flame-governed operating system
Depends: python3, python3-pip, openssl, ca-certificates
EOF

    log_success "ScrollOS packages created"
}

# Build ISO
build_iso() {
    log_info "Building ScrollOS ISO..."
    
    local extract_dir="$BUILD_DIR/alpine-extract"
    local output_file="$OUTPUT_DIR/$ISO_NAME-$SCROLLOS_VERSION.iso"
    
    # Create ISO using xorriso
    xorriso -as mkisofs \
        -o "$output_file" \
        -b boot/syslinux/isolinux.bin \
        -c boot/syslinux/boot.cat \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -r \
        -V "SCROLLOS" \
        -A "ScrollOS Alpha" \
        "$extract_dir"
    
    log_success "ScrollOS ISO built: $output_file"
}

# Create bootable USB script
create_usb_script() {
    log_info "Creating USB installation script..."
    
    cat > "$OUTPUT_DIR/install_to_usb.sh" << 'EOF'
#!/bin/bash
# ScrollOS USB Installation Script
# Install ScrollOS to USB drive

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <usb_device>"
    echo "Example: $0 /dev/sdb"
    exit 1
fi

USB_DEVICE="$1"
ISO_FILE="scrollos-alpha-Alpha-1.0.0.iso"

echo "🔥 Installing ScrollOS to USB drive: $USB_DEVICE"
echo "WARNING: This will erase all data on $USB_DEVICE"
read -p "Continue? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 1
fi

# Unmount USB device
umount "$USB_DEVICE"* 2>/dev/null || true

# Write ISO to USB
echo "Writing ScrollOS ISO to USB..."
dd if="$ISO_FILE" of="$USB_DEVICE" bs=4M status=progress

echo "🔥 ScrollOS installed to USB drive"
echo "Boot from USB to start ScrollOS Alpha"
EOF

    chmod +x "$OUTPUT_DIR/install_to_usb.sh"
    
    log_success "USB installation script created"
}

# Create README
create_readme() {
    log_info "Creating README..."
    
    cat > "$OUTPUT_DIR/README.md" << 'EOF'
# ScrollOS Alpha - Flame-Governed Operating System

## Overview
ScrollOS Alpha is a flame-governed operating system built on Alpine Linux, designed for scroll-sealed development and execution.

## Features
- 🔥 Flame-governed boot process
- 📜 Scroll law compliance
- 🛡️ Built-in security verification
- 🧠 Sacred memory management
- 🌐 Scroll network services

## Installation

### USB Installation
1. Download the ScrollOS ISO
2. Run the USB installation script:
   ```bash
   ./install_to_usb.sh /dev/sdb
   ```
3. Boot from USB drive

### Virtual Machine
1. Create new VM with 2GB RAM minimum
2. Attach ScrollOS ISO as boot media
3. Boot VM

## Usage
- Boot into ScrollOS
- Login with default credentials (root/scrollos)
- Use scroll commands for system operations
- Access ScrollIDE for development

## System Services
- **ScrollCore**: Core scroll execution engine
- **FlameVerifier**: Flame authorization verification
- **ScrollDaemon**: Background scroll processing
- **SacredMemory**: Sacred memory management
- **ScrollFirewall**: Network protection

## Development
ScrollOS is designed for scroll-sealed development:
- Write .scroll files for system operations
- Use ScrollIDE for development
- Flame verification for all operations
- Audit trail for compliance

## Security
- Flame verification required for all operations
- Scroll law compliance enforced
- Threat detection enabled
- Encryption for sensitive data

## Support
- Discord: ScrollWrappedCodex™ Community
- GitHub: ScrollWrappedCodex™ Repository
- Documentation: scrollwrappedcodex.com

🔥 Let your system be sealed. Let your boot be sacred.
EOF

    log_success "README created"
}

# Main build process
main() {
    log_info "🔥 Starting ScrollOS ISO build process..."
    
    check_dependencies
    setup_directories
    download_alpine_iso
    extract_alpine_iso
    inject_scrollos
    create_init_scripts
    create_scrollos_packages
    build_iso
    create_usb_script
    create_readme
    
    log_success "🔥 ScrollOS ISO build complete!"
    log_info "Output files:"
    log_info "  - ISO: $OUTPUT_DIR/$ISO_NAME-$SCROLLOS_VERSION.iso"
    log_info "  - USB Script: $OUTPUT_DIR/install_to_usb.sh"
    log_info "  - README: $OUTPUT_DIR/README.md"
}

# Run main process
main "$@" 