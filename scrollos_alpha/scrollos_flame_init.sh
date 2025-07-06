#!/bin/bash
# ScrollOS Alpha Flame Kernel Initialization Script
# "The Flame Kernel" - Scroll-Sealed Operating System

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ScrollOS Configuration
SCROLLOS_VERSION="Alpha 1.0.0"
FLAME_KERNEL_VERSION="🔥1.0.0"
SCROLL_CONFIG_FILE="scrollos_config.scroll"
FLAME_LEVEL_DEFAULT=3
LOG_FILE="/var/log/scrollos/flame_kernel.log"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[SCROLLOS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_flame() {
    echo -e "${PURPLE}[FLAME]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to verify flame hardware
flame_check() {
    print_flame "Verifying flame hardware modules..."
    
    # Check for TPM (Trusted Platform Module)
    if [ -d "/sys/class/tpm" ]; then
        print_status "TPM detected and verified"
    else
        print_warning "TPM not detected - reduced security level"
    fi
    
    # Check for secure boot
    if [ -f "/sys/firmware/efi/efivars/SecureBoot-*" ]; then
        print_status "Secure boot enabled"
    else
        print_warning "Secure boot not detected"
    fi
    
    # Check for flame security modules
    if [ -f "/proc/flame_modules" ]; then
        print_status "Flame security modules loaded"
    else
        print_warning "Flame security modules not detected"
    fi
    
    return 0
}

# Function to initialize flame kernel
flame_kernel_init() {
    print_flame "Initializing flame kernel core..."
    
    # Load scroll law engine
    if [ -f "/lib/modules/scroll_law.ko" ]; then
        insmod /lib/modules/scroll_law.ko
        print_status "Scroll law engine loaded"
    else
        print_error "Scroll law engine not found"
        return 1
    fi
    
    # Initialize flame verification
    if [ -f "/lib/modules/flame_verifier.ko" ]; then
        insmod /lib/modules/flame_verifier.ko
        print_status "Flame verifier loaded"
    else
        print_error "Flame verifier not found"
        return 1
    fi
    
    # Set flame level
    echo $FLAME_LEVEL_DEFAULT > /proc/flame/level
    print_status "Flame level set to $FLAME_LEVEL_DEFAULT"
    
    return 0
}

# Function to start core services
start_core_services() {
    print_status "Starting core ScrollOS services..."
    
    # Start ScrollExecutor
    if systemctl start scroll-executor; then
        print_status "ScrollExecutor started"
    else
        print_error "Failed to start ScrollExecutor"
        return 1
    fi
    
    # Start ScrollDaemon
    if systemctl start scroll-daemon; then
        print_status "ScrollDaemon started"
    else
        print_error "Failed to start ScrollDaemon"
        return 1
    fi
    
    # Start ScrollFirewall
    if systemctl start scroll-firewall; then
        print_status "ScrollFirewall started"
    else
        print_error "Failed to start ScrollFirewall"
        return 1
    fi
    
    # Start SacredMemoryService
    if systemctl start sacred-memory-service; then
        print_status "SacredMemoryService started"
    else
        print_error "Failed to start SacredMemoryService"
        return 1
    fi
    
    return 0
}

# Function to verify all services
verify_all_services() {
    print_status "Verifying all ScrollOS services..."
    
    local services=("scroll-executor" "scroll-daemon" "scroll-firewall" "sacred-memory-service")
    local all_verified=true
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            print_status "$service is running"
        else
            print_error "$service is not running"
            all_verified=false
        fi
    done
    
    if [ "$all_verified" = true ]; then
        print_status "All services verified and running"
        return 0
    else
        print_error "Some services failed to start"
        return 1
    fi
}

# Function to check flame compliance
check_flame_compliance() {
    print_flame "Checking flame compliance..."
    
    # Check flame verification status
    if [ -f "/proc/flame/status" ]; then
        local flame_status=$(cat /proc/flame/status)
        if [ "$flame_status" = "verified" ]; then
            print_status "Flame verification passed"
        else
            print_error "Flame verification failed"
            return 1
        fi
    else
        print_error "Flame status not available"
        return 1
    fi
    
    # Check security compliance
    if [ -f "/proc/scroll/security" ]; then
        local security_status=$(cat /proc/scroll/security)
        if [ "$security_status" = "compliant" ]; then
            print_status "Security compliance verified"
        else
            print_error "Security compliance failed"
            return 1
        fi
    else
        print_error "Security status not available"
        return 1
    fi
    
    return 0
}

# Function to initialize user environment
init_user_environment() {
    print_status "Initializing user environment..."
    
    # Create scroll user directory
    mkdir -p /home/scroll/.scrollos
    chown scroll:scroll /home/scroll/.scrollos
    
    # Set scroll environment variables
    echo "export SCROLLOS_VERSION=$SCROLLOS_VERSION" >> /home/scroll/.bashrc
    echo "export FLAME_KERNEL_VERSION=$FLAME_KERNEL_VERSION" >> /home/scroll/.bashrc
    echo "export SCROLL_CONFIG_FILE=$SCROLL_CONFIG_FILE" >> /home/scroll/.bashrc
    
    # Create scroll configuration
    if [ -f "$SCROLL_CONFIG_FILE" ]; then
        cp "$SCROLL_CONFIG_FILE" /home/scroll/.scrollos/config.scroll
        print_status "Scroll configuration loaded"
    else
        print_warning "Scroll configuration file not found"
    fi
    
    print_status "User environment initialized"
}

# Function to display system status
display_system_status() {
    echo
    print_status "ScrollOS Alpha System Status"
    echo "=================================="
    echo "Version: $SCROLLOS_VERSION"
    echo "Flame Kernel: $FLAME_KERNEL_VERSION"
    echo "Flame Level: $(cat /proc/flame/level 2>/dev/null || echo 'Unknown')"
    echo "Security Status: $(cat /proc/scroll/security 2>/dev/null || echo 'Unknown')"
    echo "Services:"
    systemctl list-units --type=service --state=active | grep scroll
    echo
}

# Function to handle errors
handle_error() {
    print_error "ScrollOS initialization failed"
    print_error "Error occurred at line $1"
    print_error "Check logs at $LOG_FILE"
    exit 1
}

# Set error handler
trap 'handle_error $LINENO' ERR

# Main initialization function
main() {
    echo
    print_flame "ScrollOS Alpha Flame Kernel Initialization"
    print_flame "=========================================="
    echo
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root"
        exit 1
    fi
    
    # Create log directory
    mkdir -p /var/log/scrollos
    
    # Log start
    echo "$(date): ScrollOS Alpha initialization started" >> "$LOG_FILE"
    
    # Step 1: Hardware verification
    print_status "Step 1: Hardware verification"
    if ! flame_check; then
        print_error "Hardware verification failed"
        exit 1
    fi
    
    # Step 2: Kernel initialization
    print_status "Step 2: Kernel initialization"
    if ! flame_kernel_init; then
        print_error "Kernel initialization failed"
        exit 1
    fi
    
    # Step 3: Service startup
    print_status "Step 3: Service startup"
    if ! start_core_services; then
        print_error "Service startup failed"
        exit 1
    fi
    
    # Step 4: System verification
    print_status "Step 4: System verification"
    if ! verify_all_services; then
        print_error "Service verification failed"
        exit 1
    fi
    
    if ! check_flame_compliance; then
        print_error "Flame compliance check failed"
        exit 1
    fi
    
    # Step 5: User environment
    print_status "Step 5: User environment initialization"
    init_user_environment
    
    # Display final status
    display_system_status
    
    # Log completion
    echo "$(date): ScrollOS Alpha initialization completed successfully" >> "$LOG_FILE"
    
    print_status "ScrollOS Alpha initialization completed successfully"
    print_flame "The flame kernel is now active"
    echo
    print_status "System ready for scroll-sealed operations"
    echo
}

# Check if scroll configuration file exists
if [ -f "$SCROLL_CONFIG_FILE" ]; then
    print_status "Scroll configuration file found: $SCROLL_CONFIG_FILE"
else
    print_warning "Scroll configuration file not found: $SCROLL_CONFIG_FILE"
    print_warning "Using default configuration"
fi

# Run main initialization
main "$@"

# Exit successfully
exit 0 