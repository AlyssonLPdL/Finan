uploadForm.addEventListener('submit', (event) => {
    event.preventDefault(); // Evita o recarregamento da página
    
    // Preenche a data com o dia de hoje, caso não tenha sido fornecida
    const dateInput = document.getElementById('date');
    if (!dateInput.value) {
        const today = new Date().toISOString().split('T')[0]; // Formata a data para o formato YYYY-MM-DD
        dateInput.value = today;
    }

    // Preenche a quantia com 1, caso não tenha sido fornecida
    const quantiaInput = document.getElementById('quantia');
    if (!quantiaInput.value) {
        quantiaInput.value = 1;
    }
    
    // Exibe o spinner
    spinner.style.display = 'block';
    
    // Fecha o popup imediatamente
    uploadPopup.style.display = 'none';
    
    // Cria um objeto FormData para enviar o formulário
    const formData = new FormData(uploadForm);
    
    // Envia o formulário via fetch (AJAX)
    fetch(uploadForm.action, {
        method: 'POST',
        body: formData,
    })
    .then((response) => {
        if (response.ok) {
            // Espera o processamento do arquivo, então oculta o spinner
            spinner.style.display = 'none';
            // Recarrega a página após o processamento
            location.reload();
        } else {
            // Em caso de erro, exibe uma mensagem
            alert('Erro ao enviar a planilha. Verifique o arquivo e tente novamente.');
            spinner.style.display = 'none'; // Garante que o spinner seja ocultado
        }
    })
    .catch((error) => {
        // Em caso de erro, oculta o spinner e exibe a mensagem de erro
        spinner.style.display = 'none';
        alert('Ocorreu um erro ao enviar a planilha.');
        console.error(error);
    });
});
