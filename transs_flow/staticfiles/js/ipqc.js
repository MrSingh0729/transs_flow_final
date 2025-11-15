// IPQC System JavaScript Utilities

class IPQCUtils {
    // Form validation
    static validateForm(formId) {
        const form = document.getElementById(formId);
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('is-invalid');
                input.classList.remove('is-valid');
            } else if (input.checkValidity && !input.checkValidity()) {
                isValid = false;
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            }
        });
        
        return isValid;
    }
    
    // Auto-save functionality
    static autoSave(formId, storageKey) {
        const form = document.getElementById(formId);
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                localStorage.setItem(storageKey, JSON.stringify(data));
            });
        });
        
        // Restore saved data
        const saved = localStorage.getItem(storageKey);
        if (saved) {
            const data = JSON.parse(saved);
            Object.entries(data).forEach(([key, value]) => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input && !input.value) {
                    input.value = value;
                    // Trigger change event for select2 and other components
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
    }
    
    // Calculate totals for BTB form
    static calculateBTBTotals() {
        const hours = ['9', '10', '11', '12', '1', '2', '3', '4', '5', '6'];
        let totals = {
            input: 0,
            camBtb: 0,
            lcdFitment: 0,
            mainFpc: 0,
            battery: 0,
            fingerPrinter: 0
        };
        
        hours.forEach(hour => {
            const inputs = ['cam_btb', 'lcd_fitment', 'main_fpc', 'battery', 'finger_printer'];
            inputs.forEach(field => {
                const value = parseFloat(document.querySelector(`[name="${field}_${hour}"]`)?.value || 0;
                if (!isNaN(value)) {
                    totals[field] += value;
                }
            });
        });
        
        // Update total displays
        document.getElementById('input_total').textContent = totals.input;
        document.getElementById('cam_btb_total').textContent = totals.camBtb;
        document.getElementById('lcd_fitment_total').textContent = totals.lcdFitment;
        document.getElementById('main_fpc_total').textContent = totals.mainFpc;
        document.getElementById('battery_total').textContent = totals.battery;
        document.getElementById('finger_printer_total').textContent = totals.fingerPrinter;
        
        // Calculate grand total
        const grandTotal = totals.camBtb + totals.lcdFitment + totals.mainFpc + totals.battery + totals.fingerPrinter;
        document.getElementById('grand_total').textContent = grandTotal;
    }
    
    // Export to Excel functionality
    static exportTable(tableId, filename) {
        const table = document.getElementById(tableId);
        const rows = [];
        const headers = [];
        
        // Get headers
        table.querySelectorAll('thead th').forEach(th => {
            headers.push(th.textContent.trim());
        });
        
        // Get rows
        table.querySelectorAll('tbody tr').forEach(tr => {
            const rowData = [];
            tr.querySelectorAll('td').forEach(td => {
                rowData.push(td.textContent.trim());
            });
            rows.push(rowData);
        });
        
        // Create CSV
        let csv = headers.join(',') + '\n';
        rows.forEach(row => {
            csv += row.join(',') + '\n';
        });
        
        // Download
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
    
    // Print functionality
    static printElement(elementId) {
        const element = document.getElementById(elementId);
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Print Report</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        table { border-collapse: collapse; width: 100%; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background: #f4f4f4; font-weight: bold; }
                        @media print { body { padding: 0; } }
                    </style>
                </head>
                <body>
                    ${element.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
    
    // Notification system
    static showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()">&times;</button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, duration);
    }
    
    // Offline detection
    static checkOnlineStatus() {
        const statusIndicator = document.getElementById('onlineStatus');
        if (navigator.onLine) {
            statusIndicator.textContent = 'Online';
            statusIndicator.className = 'text-success';
        } else {
            statusIndicator.textContent = 'Offline';
            statusIndicator.className = 'text-warning';
        }
    }
    
    // Date and time utilities
    static formatDate(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day);
    }
    
    // Touch gestures for mobile
    static initTouchGestures() {
        let touchStartX = 0;
        let touchEndX = 0;
        
        document.addEventListener('touchstart', e => {
            touchStartX = e.touches[0].clientX;
        });
        
        document.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].clientX;
            const diff = touchStartX - touchEndX;
            
            if (Math.abs(diff) > 50) {
                // Swipe detected
                if (diff > 0) {
                    // Swipe right - next
                    console.log('Swipe right detected');
                } else {
                    // Swipe left - previous
                    console.log('Swipe left detected');
                }
            }
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize form validation
    const forms = document.querySelectorAll('form.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!IPQCUtils.validateForm(form.id)) {
                e.preventDefault();
                IPQCUtils.showNotification('Please fill in all required fields correctly', 'danger');
            }
        });
    });
    
    // Check online status
    IPQCUtils.checkOnlineStatus();
    
    // Initialize touch gestures on mobile
    if ('ontouchstart' in window) {
        IPQCUtils.initTouchGestures();
    }
    
    // Periodic auto-save check
    setInterval(() => {
        const forms = document.querySelectorAll('form[data-auto-save]');
        forms.forEach(form => {
            if (form.dataset.autoSave) {
                IPQCUtils.autoSave(form.id, form.id + '_draft');
            }
        });
    }, 30000); // Check every 30 seconds
});

// Export global functions for use in templates
window.IPQCUtils = IPQCUtils;