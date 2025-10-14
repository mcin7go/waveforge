/**
 * WaveBulk - Processing History
 * Handles file history display, status polling, bulk operations, and filtering
 */

document.addEventListener('DOMContentLoaded', function() {
    const POLLING_INTERVAL = 3000; // ms
    
    // === SEKCJA POLLINGU ===
    const pendingRows = document.querySelectorAll('tr[data-status-url]');
    if (pendingRows.length > 0) {
        pendingRows.forEach(row => {
            const statusUrl = row.dataset.statusUrl;
            const taskId = row.id.split('-').pop();
            startPolling(statusUrl, taskId);
        });
    }

    // === OBSŁUGA FILTRÓW I WYSZUKIWANIA ===
    const searchInput = document.getElementById('search-input');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const historyTable = document.getElementById('history-table');
    
    let currentFilter = 'all';
    let currentSearch = '';
    
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearch = e.target.value.toLowerCase();
            applyFilters();
        });
    }
    
    if (filterBtns) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.filter;
                applyFilters();
            });
        });
    }
    
    function applyFilters() {
        const rows = historyTable ? historyTable.querySelectorAll('tbody tr') : [];
        
        rows.forEach(row => {
            const filename = row.querySelector('.file-link')?.textContent.toLowerCase() || '';
            const status = row.dataset.status || '';
            
            // Search filter
            const matchesSearch = !currentSearch || filename.includes(currentSearch);
            
            // Status filter
            let matchesFilter = true;
            if (currentFilter === 'completed') {
                matchesFilter = status === 'COMPLETED';
            } else if (currentFilter === 'processing') {
                matchesFilter = ['PENDING', 'QUEUED', 'PROCESSING'].includes(status);
            } else if (currentFilter === 'failed') {
                matchesFilter = status === 'FAILED';
            }
            
            // Show/hide row
            row.style.display = (matchesSearch && matchesFilter) ? '' : 'none';
        });
    }

    // === OBSŁUGA USUWANIA I POBIERANIA ===
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    const deleteBtn = document.getElementById('delete-selected-btn');
    const downloadBtn = document.getElementById('download-selected-btn');
    const historyContainer = document.getElementById('history-container');

    // Sprawdzamy, czy te elementy istnieją, zanim dodamy listenery
    if (selectAllCheckbox && deleteBtn && historyContainer) {
        
        // Używamy delegacji zdarzeń dla pojedynczych checkboxów
        historyContainer.addEventListener('change', (e) => {
            if (e.target.classList.contains('file-checkbox')) {
                toggleBulkButtonsState();
            }
        });

        selectAllCheckbox.addEventListener('change', (e) => {
            const visibleCheckboxes = Array.from(document.querySelectorAll('.file-checkbox')).filter(
                cb => cb.closest('tr').style.display !== 'none'
            );
            visibleCheckboxes.forEach(checkbox => {
                checkbox.checked = e.target.checked;
            });
            toggleBulkButtonsState();
        });

        deleteBtn.addEventListener('click', handleDeleteClick);
        if (downloadBtn) {
            downloadBtn.addEventListener('click', handleDownloadClick);
        }
    }
    
    function toggleBulkButtonsState() {
        // Zawsze pobieraj aktualną listę checkboxów
        const anyChecked = Array.from(document.querySelectorAll('.file-checkbox')).some(cb => cb.checked);
        deleteBtn.disabled = !anyChecked;
        if (downloadBtn) {
            downloadBtn.disabled = !anyChecked;
        }
    }
    
    function handleDownloadClick() {
        const selectedIds = Array.from(document.querySelectorAll('.file-checkbox:checked'))
            .map(cb => cb.value);

        if (selectedIds.length === 0) return;

        // Disable button during download
        downloadBtn.disabled = true;
        downloadBtn.textContent = 'Przygotowywanie...';

        fetch('/audio/download-multiple', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: selectedIds })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Download failed');
            }
            return response.blob();
        })
        .then(blob => {
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `wavebulk_files_${new Date().toISOString().split('T')[0]}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            
            downloadBtn.textContent = 'Pobierz zaznaczone (ZIP)';
            toggleBulkButtonsState();
        })
        .catch(error => {
            alert('Błąd podczas pobierania plików: ' + error.message);
            downloadBtn.textContent = 'Pobierz zaznaczone (ZIP)';
            toggleBulkButtonsState();
        });
    }

    function handleDeleteClick() {
        // Zawsze pobieraj aktualną listę zaznaczonych checkboxów
        const selectedIds = Array.from(document.querySelectorAll('.file-checkbox:checked'))
            .map(cb => cb.value);

        if (selectedIds.length === 0) return;

        if (confirm(`Czy na pewno chcesz usunąć ${selectedIds.length} plików? Tej operacji nie można cofnąć.`)) {
            // Zablokuj przycisk na czas operacji
            deleteBtn.disabled = true;
            deleteBtn.textContent = 'Usuwanie...';

            fetch('/audio/delete-files', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: selectedIds })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || 'Błąd serwera.') });
                }
                return response.json();
            })
            .then(data => {
                console.log(data.message);
                selectedIds.forEach(id => {
                    // Poprawiony, bezpieczniejszy selektor
                    const checkbox = document.querySelector(`.file-checkbox[value="${id}"]`);
                    if (checkbox) {
                        const row = checkbox.closest('tr');
                        if (row) row.remove();
                    }
                });
                
                // Zresetuj stan przycisku i checkboxów
                deleteBtn.textContent = 'Usuń zaznaczone';
                selectAllCheckbox.checked = false;
                toggleBulkButtonsState();

                if (document.querySelectorAll('.file-checkbox').length === 0) {
                     historyContainer.innerHTML = '<p class="text-center text-secondary" style="padding-top: 2rem;">Nie masz już żadnych przetworzonych plików.</p>';
                }
            })
            .catch(error => {
                alert(error.message);
                deleteBtn.textContent = 'Usuń zaznaczone';
                toggleBulkButtonsState();
            });
        }
    }

    // Funkcje pollingu (bez zmian)
    function startPolling(statusUrl, taskId) {
        const interval = setInterval(() => {
            fetch(statusUrl)
                .then(response => {
                    if (!response.ok) {
                        if (response.status === 404) clearInterval(interval);
                        throw new Error(`Błąd HTTP ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'COMPLETED' || data.status === 'FAILED') {
                        clearInterval(interval);
                        updateTableRow(taskId, data);
                    }
                })
                .catch(error => { 
                    console.error(`Błąd podczas sprawdzania statusu dla zadania ${taskId}:`, error); 
                });
        }, POLLING_INTERVAL);
    }
    function updateTableRow(taskId, taskData) {
        const statusCell = document.getElementById(`task-status-cell-${taskId}`);
        const actionsCell = document.getElementById(`task-actions-cell-${taskId}`);
        if (!statusCell) return;
        let statusBadge = '';
        if (taskData.status === 'COMPLETED') {
            statusBadge = '<span class="badge bg-success">Ukończono</span>';
            if (taskData.result) {
                try {
                    const results = JSON.parse(taskData.result);
                    if (results.processed_file_url && actionsCell) {
                        actionsCell.innerHTML = `<a href="${results.processed_file_url}" class="btn btn-primary btn-sm" download>Pobierz</a>`;
                    }
                } catch (e) { console.error("Błąd parsowania wyników dla zadania " + taskId, e); }
            }
        } else if (taskData.status === 'FAILED') {
            statusBadge = '<span class="badge bg-danger">Błąd</span>';
        }
        statusCell.innerHTML = statusBadge;
    }
});