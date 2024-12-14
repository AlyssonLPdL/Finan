document.addEventListener('DOMContentLoaded', () => {
    const editPopup = document.getElementById('edit-popup');
    const editForm = document.getElementById('edit-form');

    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            const id = e.target.getAttribute('data-id');
            const response = await fetch(`/get_transaction/${id}`);
            const data = await response.json();

            // Verifique o que está sendo retornado
            console.log(data);  // Apenas para depuração

            // Preenchendo os campos com os dados
            document.getElementById('edit-id').value = data[0]; // Usando 'data.id' em vez de 'data[0]'
            document.getElementById('edit-date').value = data[1];
            document.getElementById('edit-quantia').value = data[6];
            document.getElementById('edit-description').value = data[2];
            document.getElementById('edit-value').value = data[3];
            document.getElementById('edit-payment-method').value = data[4];
            document.getElementById('edit-type').value = data[5];

            editPopup.classList.remove('hidden');
        });
    });

    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            const id = e.target.getAttribute('data-id');
            const response = await fetch(`/delete/${id}`, { method: 'POST' });
            if (response.ok) location.reload();
        });
    });

    document.getElementById('save-edit-btn').addEventListener('click', async () => {
        const id = document.getElementById('edit-id').value;
        const data = {
            date: document.getElementById('edit-date').value,
            quantia: document.getElementById('edit-quantia').value,
            description: document.getElementById('edit-description').value,
            value: document.getElementById('edit-value').value,
            payment_method: document.getElementById('edit-payment-method').value,
            type: document.getElementById('edit-type').value,
        };

        const response = await fetch(`/edit/${id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (response.ok) location.reload();
    });

    document.getElementById('cancel-edit-btn').addEventListener('click', () => {
        editPopup.classList.add('hidden');
    });
});