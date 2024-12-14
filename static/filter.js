function filterByMonth() {
    const selectedMonth = document.getElementById('month-filter').value;
    const queryString = selectedMonth ? `?month=${selectedMonth}` : '';
    window.location.href = '/' + queryString;
}

function filterByPayment() {
    const selectedPayment = document.getElementById('payment-filter').value;
    const queryString = selectedPayment ? `?payment_method=${selectedPayment}` : '';
    window.location.href = '/' + queryString;  // Atualiza a URL com o filtro de pagamento
}

function filterByType() {
    const selectedType = document.getElementById('tipe-filter').value;
    const queryString = selectedType ? `?type=${selectedType}` : '';
    window.location.href = '/' + queryString;  // Atualiza a URL com o filtro de pagamento
}