#!/bin/bash
"""
Logrotate Setup Script for Jaston Real Estate Platform

This script installs and configures logrotate for all daemon service logs
to ensure proper log management, prevent disk space issues, and maintain
organized log files for debugging and monitoring.

Author: Douglas Mutethia (Eleso Solutions)
Version: 1.0.0
"""

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOGROTATE_CONFIG="${PROJECT_ROOT}/infrastructure/config/logrotate.conf"
SYSTEM_LOGROTATE_DIR="/etc/logrotate.d"
JASTON_LOGROTATE_FILE="${SYSTEM_LOGROTATE_DIR}/jaston-real-estate"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Check if running as root or with sudo
check_privileges() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root or with sudo"
        log "Usage: sudo $0"
        exit 1
    fi
}

# Check if logrotate is installed
check_logrotate() {
    log "🔍 Checking if logrotate is installed..."
    
    if ! command -v logrotate &> /dev/null; then
        log_warning "logrotate is not installed. Installing..."
        
        # Detect package manager and install
        if command -v apt-get &> /dev/null; then
            apt-get update
            apt-get install -y logrotate
        elif command -v yum &> /dev/null; then
            yum install -y logrotate
        elif command -v dnf &> /dev/null; then
            dnf install -y logrotate
        else
            log_error "Could not detect package manager. Please install logrotate manually."
            exit 1
        fi
        
        log_success "logrotate installed successfully"
    else
        log_success "logrotate is already installed"
    fi
}

# Validate logrotate configuration
validate_config() {
    log "🔍 Validating logrotate configuration..."
    
    if [[ ! -f "$LOGROTATE_CONFIG" ]]; then
        log_error "Logrotate configuration file not found: $LOGROTATE_CONFIG"
        exit 1
    fi
    
    # Test the configuration
    if logrotate -d "$LOGROTATE_CONFIG" &> /dev/null; then
        log_success "Logrotate configuration is valid"
    else
        log_error "Logrotate configuration validation failed"
        log "Running debug mode to show errors:"
        logrotate -d "$LOGROTATE_CONFIG"
        exit 1
    fi
}

# Install logrotate configuration
install_config() {
    log "📦 Installing logrotate configuration..."
    
    # Create backup of existing configuration if it exists
    if [[ -f "$JASTON_LOGROTATE_FILE" ]]; then
        log_warning "Existing configuration found. Creating backup..."
        cp "$JASTON_LOGROTATE_FILE" "${JASTON_LOGROTATE_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        log_success "Backup created"
    fi
    
    # Copy configuration to system directory
    cp "$LOGROTATE_CONFIG" "$JASTON_LOGROTATE_FILE"
    
    # Set proper permissions
    chmod 644 "$JASTON_LOGROTATE_FILE"
    chown root:root "$JASTON_LOGROTATE_FILE"
    
    log_success "Logrotate configuration installed to $JASTON_LOGROTATE_FILE"
}

# Create log directories if they don't exist
create_log_directories() {
    log "📁 Ensuring log directories exist..."
    
    local log_dir="${PROJECT_ROOT}/infrastructure/logs"
    
    if [[ ! -d "$log_dir" ]]; then
        mkdir -p "$log_dir"
        log_success "Created log directory: $log_dir"
    fi
    
    # Set proper ownership and permissions
    chown -R douglas:douglas "$log_dir"
    chmod -R 755 "$log_dir"
    
    log_success "Log directory permissions set correctly"
}

# Test logrotate configuration
test_logrotate() {
    log "🧪 Testing logrotate configuration..."
    
    # Run logrotate in debug mode
    log "Running logrotate in debug mode..."
    if logrotate -d "$JASTON_LOGROTATE_FILE"; then
        log_success "Logrotate test completed successfully"
    else
        log_error "Logrotate test failed"
        return 1
    fi
    
    # Force a rotation test (dry run)
    log "Testing forced rotation (dry run)..."
    if logrotate -f -v "$JASTON_LOGROTATE_FILE" --state /tmp/logrotate.state.test; then
        log_success "Forced rotation test completed successfully"
        rm -f /tmp/logrotate.state.test
    else
        log_error "Forced rotation test failed"
        return 1
    fi
}

# Setup cron job for logrotate (if not already configured)
setup_cron() {
    log "⏰ Checking logrotate cron configuration..."
    
    # Check if logrotate is already in cron
    if crontab -l 2>/dev/null | grep -q logrotate; then
        log_success "Logrotate cron job already configured"
    else
        log_warning "Logrotate cron job not found in system cron"
        log "Note: Most systems have logrotate configured in /etc/cron.daily/"
        
        if [[ -f "/etc/cron.daily/logrotate" ]]; then
            log_success "System logrotate cron job found in /etc/cron.daily/"
        else
            log_warning "System logrotate cron job not found"
            log "You may need to configure logrotate to run daily"
        fi
    fi
}

# Display configuration summary
show_summary() {
    log "📋 Configuration Summary:"
    echo
    echo "  📁 Project Root: $PROJECT_ROOT"
    echo "  📄 Config Source: $LOGROTATE_CONFIG"
    echo "  📄 Config Target: $JASTON_LOGROTATE_FILE"
    echo "  📁 Log Directory: ${PROJECT_ROOT}/infrastructure/logs"
    echo
    echo "  🔄 Rotation Schedule:"
    echo "    • Django logs: Daily (30 days retention)"
    echo "    • Celery logs: Daily (30 days retention)"
    echo "    • Redis logs: Daily (30 days retention)"
    echo "    • Manager logs: Weekly (12 weeks retention)"
    echo "    • Health check logs: Weekly (12 weeks retention)"
    echo "    • Setup/Test logs: Monthly (6 months retention)"
    echo
    echo "  📏 Size Limits:"
    echo "    • Maximum log size before rotation: 100MB"
    echo "    • Compression: Enabled (delayed)"
    echo "    • Date extension: Enabled"
    echo
}

# Main execution
main() {
    echo
    log "🚀 Starting Jaston Real Estate Logrotate Setup"
    echo "=============================================="
    
    check_privileges
    check_logrotate
    validate_config
    create_log_directories
    install_config
    test_logrotate
    setup_cron
    
    echo
    log_success "🎉 Logrotate setup completed successfully!"
    echo
    show_summary
    
    echo "📝 Next Steps:"
    echo "  1. Logs will be automatically rotated according to the schedule"
    echo "  2. Monitor log rotation with: sudo logrotate -d $JASTON_LOGROTATE_FILE"
    echo "  3. Force rotation for testing: sudo logrotate -f $JASTON_LOGROTATE_FILE"
    echo "  4. Check logrotate status: sudo cat /var/lib/logrotate/status"
    echo
}

# Handle script interruption
trap 'log_error "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@"