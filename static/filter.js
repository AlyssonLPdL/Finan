function filterByMonthYear() {
    const selectedMonthYear = document.getElementById('month-year-filter').value;
    const queryString = selectedMonthYear ? `?month_year=${selectedMonthYear}` : '';
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