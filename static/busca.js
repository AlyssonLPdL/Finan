function filterTable() {
    const searchInput = document.getElementById('search-input').value.toLowerCase();
    const tableRows = document.querySelectorAll('table tbody tr');
    
    // Verifica se há um prefixo (maior ou menor que)
    let prefix = '';
    let searchValue = searchInput;

    if (searchInput.startsWith('>')) {
        prefix = '>';
        searchValue = searchInput.substring(1);  // Remove o prefixo ">"
    } else if (searchInput.startsWith('<')) {
        prefix = '<';
        searchValue = searchInput.substring(1);  // Remove o prefixo "<"
    }

    tableRows.forEach(row => {
        const rowData = Array.from(row.children).map(cell => cell.textContent.toLowerCase());
        let matches = false;

        // Se o prefixo foi usado para filtrar valores
        if (prefix === '>' || prefix === '<') {
            const valueCell = rowData[3]; // O valor está na quarta célula (índice 3) da linha
            
            // Se o valor for numérico, compara com o prefixo
            if (!isNaN(valueCell)) {
                const rowValue = parseFloat(valueCell);
                const searchNumber = parseFloat(searchValue);

                if (prefix === '>' && rowValue > searchNumber) {
                    matches = true;
                } else if (prefix === '<' && rowValue < searchNumber) {
                    matches = true;
                }
            }
        } else {
            // Caso não tenha prefixo, faz a busca por qualquer outro dado
            matches = rowData.some(data => data.includes(searchValue));
        }

        // Mostra ou esconde a linha com base no resultado da busca
        if (matches) {
            row.style.display = ''; // Mostra a linha
        } else {
            row.style.display = 'none'; // Oculta a linha
        }
    });
}
