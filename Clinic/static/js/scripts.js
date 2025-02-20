/* scripts.js */

document.addEventListener('DOMContentLoaded', function() {
    // Dynamic Consultation Fee Update
    const doctorSelect = document.getElementById('doctorSelect');
    const feeAmount = document.getElementById('feeAmount');

    if (doctorSelect && feeAmount) {
        doctorSelect.addEventListener('change', function() {
            const doctorId = this.value;

            fetch(`/get_doctor_fee/${doctorId}`)
                .then(response => response.json())
                .then(data => {
                    feeAmount.textContent = data.fee.toFixed(2);
                })
                .catch(error => {
                    console.error('Error fetching doctor fee:', error);
                    feeAmount.textContent = '0.00';
                });
        });
    }

    // Sidebar Toggle (for responsive design)
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }

});
function searchByPhoneNumber() {
    const phoneNumber = document.getElementById('phone_number_input').value;
    
    fetch(`/search_by_phone/${phoneNumber}`)
        .then(response => response.json())
        .then(data => {
            const resultDiv = document.getElementById('search-result');
            if (data.role) {
                resultDiv.innerHTML = `<div class="alert alert-success">Role: ${data.role} <br> Name: ${data.name}</div>`;
            } else {
                resultDiv.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
            }
        })
        .catch(error => console.error('Error:', error));
}