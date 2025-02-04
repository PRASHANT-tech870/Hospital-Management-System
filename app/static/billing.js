// Load patient's invoices
async function loadInvoices() {
    const userData = JSON.parse(localStorage.getItem('user'));
    if (!userData) return;

    try {
        // Get patient ID from user data
        const patientResponse = await fetch(`/patients/${userData.id}`);
        if (!patientResponse.ok) throw new Error('Failed to fetch patient data');
        
        const patientData = await patientResponse.json();
        const patientId = patientData.id;

        // Fetch invoices using patient ID
        const response = await fetch(`/api/billing/patient/${patientId}/invoices`);
        if (!response.ok) throw new Error('Failed to fetch invoices');

        const invoices = await response.json();
        const invoicesList = document.getElementById('invoices-list');
        invoicesList.innerHTML = '';

        if (invoices.length === 0) {
            invoicesList.innerHTML = '<p class="no-invoices">No invoices found</p>';
            return;
        }

        invoices.forEach(invoice => {
            const invoiceElement = document.createElement('div');
            invoiceElement.className = `invoice-item ${invoice.status.toLowerCase()}`;
            invoiceElement.innerHTML = `
                <div class="invoice-header">
                    <span class="invoice-id">Invoice #${invoice.id}</span>
                    <span class="invoice-status ${invoice.status.toLowerCase()}">
                        ${invoice.status}
                        ${invoice.status === 'PAID' ? '✓' : ''}
                    </span>
                </div>
                <div class="invoice-details">
                    <p>Date: ${new Date(invoice.created_at).toLocaleDateString()}</p>
                    <p>Total Amount: $${invoice.total_amount.toFixed(2)}</p>
                    ${invoice.paid_at ? `<p>Paid on: ${new Date(invoice.paid_at).toLocaleDateString()}</p>` : ''}
                </div>
                <div class="invoice-items">
                    ${invoice.items.map(item => `
                        <div class="invoice-item-detail">
                            <span>${item.description}</span>
                            <span>$${item.amount.toFixed(2)}</span>
                        </div>
                    `).join('')}
                </div>
                ${invoice.status === 'PENDING' ? `
                    <button class="pay-btn" onclick="showPaymentModal(${invoice.id}, ${invoice.total_amount})">
                        Pay Now
                    </button>
                ` : ''}
            `;
            invoicesList.appendChild(invoiceElement);
        });
    } catch (error) {
        console.error('Error loading invoices:', error);
        document.getElementById('invoices-list').innerHTML = 
            '<p class="error-message">Error loading invoices</p>';
    }
}

// Show payment modal
function showPaymentModal(invoiceId, amount) {
    if (confirm(`Confirm payment of $${amount.toFixed(2)}?`)) {
        processPayment(invoiceId);
    }
}

// Process payment
async function processPayment(invoiceId) {
    try {
        const response = await fetch(`/api/billing/invoices/${invoiceId}/pay`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Payment failed');
        }

        const result = await response.json();
        alert('Payment successful!');
        loadInvoices(); // Refresh the invoices list
    } catch (error) {
        console.error('Error processing payment:', error);
        alert(error.message || 'Error processing payment');
    }
}

// Close modal when clicking the close button or outside the modal
document.querySelector('.close').addEventListener('click', () => {
    document.getElementById('payment-modal').style.display = 'none';
});

window.addEventListener('click', (e) => {
    const modal = document.getElementById('payment-modal');
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

// Format card number input
document.getElementById('card-number').addEventListener('input', (e) => {
    let value = e.target.value.replace(/\D/g, '');
    e.target.value = value.replace(/(\d{4})(?=\d)/g, '$1 ');
});

// Format expiry date input
document.getElementById('expiry').addEventListener('input', (e) => {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length >= 2) {
        value = value.slice(0, 2) + '/' + value.slice(2);
    }
    e.target.value = value;
});

// Initialize billing system
document.addEventListener('DOMContentLoaded', loadInvoices); 