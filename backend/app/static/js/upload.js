/**
 * WaveBulk - Upload & Processing
 * Handles file upload, drag-and-drop, and batch processing
 */

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    if (!uploadForm) return;

    const fileInput = document.getElementById('file-input');
    const submitButton = document.getElementById('submit-button');
    const dropArea = document.getElementById('drop-area');
    const browseButton = document.getElementById('browse-button');
    const fileListContainer = document.getElementById('file-list-container');
    const fileErrorDiv = document.getElementById('file-error');
    const optionsSection = document.getElementById('options-section');
    const queueSection = document.getElementById('queue-section');
    const queueSummary = document.getElementById('queue-summary');
    const formatSelect = document.getElementById('format-select');
    const bitrateContainer = document.getElementById('bitrate-container');
    const bitrateSelect = document.getElementById('bitrate-select');
    const bitDepthContainer = document.getElementById('bit-depth-container');
    const bitDepthSelect = document.getElementById('bit-depth-select');
    const presetSelect = document.getElementById('preset-select');
    const customNormalizationSection = document.getElementById('custom-normalization-section');
    const normalizeToggle = document.getElementById('normalize-toggle');
    const targetLufsContainer = document.getElementById('target-lufs-container');
    const targetLufsInput = document.getElementById('target-lufs-input');
    const truePeakToggle = document.getElementById('true-peak-toggle');
    const ditherContainer = document.getElementById('dither-container');
    const ditherSelect = document.getElementById('dither-select');
    const resamplerContainer = document.getElementById('resampler-container');
    const resamplerSelect = document.getElementById('resampler-select');
    const sampleRateSelect = document.getElementById('sample-rate-select');
    const trimSilenceToggle = document.getElementById('trim-silence-toggle');
    const fadeToggle = document.getElementById('fade-toggle');
    const fadeDurationContainer = document.getElementById('fade-duration-container');
    const fadeInInput = document.getElementById('fade-in-input');
    const fadeOutInput = document.getElementById('fade-out-input');
    const artistInput = document.getElementById('artist-input');
    const albumInput = document.getElementById('album-input');
    const titleInput = document.getElementById('title-input');
    const trackNumberInput = document.getElementById('track-number-input');
    const isrcInput = document.getElementById('isrc-input');
    const coverArtInput = document.getElementById('cover-art-input');
    const coverArtButton = document.getElementById('cover-art-button');
    const coverArtFilename = document.getElementById('cover-art-filename');
    
    // Accordion functionality
    const processingOptionsHeader = document.getElementById('processing-options-header');
    const processingOptionsContent = document.getElementById('processing-options-content');
    const metadataHeader = document.getElementById('metadata-header');
    const metadataContent = document.getElementById('metadata-content');
    
    if (processingOptionsHeader) {
        processingOptionsHeader.addEventListener('click', () => {
            processingOptionsContent.classList.toggle('expanded');
            processingOptionsHeader.querySelector('.accordion-icon').classList.toggle('rotated');
        });
    }
    
    if (metadataHeader) {
        metadataHeader.addEventListener('click', () => {
            metadataContent.classList.toggle('expanded');
            metadataHeader.querySelector('.accordion-icon').classList.toggle('rotated');
        });
    }

    const LufsIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75z" /></svg>`;
    const DurationIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
    const SuccessIcon = `<svg style="width: 24px; height: 24px; color: #198754;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
    const ErrorIcon = `<svg style="width: 24px; height: 24px; color: #dc3545;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;

    // Configuration
    const MAX_FILE_SIZE_MB = 100;
    const ALLOWED_MIME_TYPES = [
        'audio/wav', 'audio/x-wav',          // WAV
        'audio/mpeg', 'audio/mp3',           // MP3
        'audio/mp4', 'audio/x-m4a',          // M4A/AAC
        'audio/aac', 'audio/aacp',
        'audio/flac', 'audio/x-flac',        // FLAC
        'audio/ogg', 'audio/vorbis',         // OGG
        'audio/x-ms-wma',                     // WMA
        'audio/aiff', 'audio/x-aiff'         // AIFF
    ];
    const POLLING_INTERVAL = 2500; // ms
    
    // State
    let fileQueue = [];
    let isProcessingQueue = false;

    function toggleAdvancedOptions() {
        const isLossless = formatSelect.value === 'wav' || formatSelect.value === 'flac';
        const is16bit = bitDepthSelect.value === '16';
        
        bitrateContainer.style.display = isLossless ? 'none' : 'block';
        bitDepthContainer.style.display = isLossless ? 'block' : 'none';
        ditherContainer.style.display = isLossless && is16bit ? 'block' : 'none';
        resamplerContainer.style.display = isLossless ? 'block' : 'none';
    }

    formatSelect.addEventListener('change', toggleAdvancedOptions);
    bitDepthSelect.addEventListener('change', toggleAdvancedOptions);

    presetSelect.addEventListener('change', () => {
        const isCustom = presetSelect.value === 'custom';
        customNormalizationSection.style.display = isCustom ? 'block' : 'none';
        truePeakToggle.checked = !isCustom;
        truePeakToggle.disabled = !isCustom;
    });
    normalizeToggle.addEventListener('change', () => { targetLufsContainer.style.display = normalizeToggle.checked ? 'block' : 'none'; });
    fadeToggle.addEventListener('change', () => { fadeDurationContainer.style.display = fadeToggle.checked ? 'block' : 'none'; });
    dropArea.addEventListener('click', () => fileInput.click());
    browseButton.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
    coverArtButton.addEventListener('click', () => coverArtInput.click());
    coverArtInput.addEventListener('change', () => {
        coverArtFilename.textContent = coverArtInput.files.length > 0 ? coverArtInput.files[0].name : '';
    });
    setupDragAndDrop();
    uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (fileQueue.length > 0) processQueue();
    });

    window.addEventListener('beforeunload', function (e) {
        if (isProcessingQueue) {
            e.preventDefault(); 
            e.returnValue = ''; 
        }
    });

    function handleFiles(files) {
        fileErrorDiv.style.display = 'none';
        const validFiles = Array.from(files).filter(validateFile);
        if (validFiles.length > 0) {
            validFiles.forEach(file => fileQueue.push({ file: file, status: 'waiting' }));
            renderFileList();
            updateQueueSummary();
            submitButton.disabled = false;
            optionsSection.style.display = 'block';
            queueSection.style.display = 'block';
        }
    }

    function renderFileList() {
        fileListContainer.innerHTML = '';
        fileQueue.forEach((item, index) => {
            const card = document.createElement('div');
            card.className = 'file-card';
            card.id = `file-item-${index}`;
            card.innerHTML = `
                <div class="file-card-header">
                    <span class="file-card-name">${item.file.name}</span>
                    <button type="button" class="btn-close" style="background-color: #fff;" data-index="${index}"></button>
                </div>
                <div class="file-card-status">Oczekuje...</div>
                <div class="progress mt-2" style="display: none; height: 8px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%;"></div>
                </div>
                <div class="file-card-results" style="display: none;"></div>
            `;
            fileListContainer.appendChild(card);
        });
        document.querySelectorAll('.btn-close').forEach(button => {
            button.addEventListener('click', (e) => {
                const indexToRemove = parseInt(e.target.getAttribute('data-index'));
                fileQueue.splice(indexToRemove, 1);
                renderFileList();
                updateQueueSummary();
                if (fileQueue.length === 0) {
                    submitButton.disabled = true;
                    optionsSection.style.display = 'none';
                    queueSection.style.display = 'none';
                }
            });
        });
    }

    async function processQueue() {
        isProcessingQueue = true;
        document.querySelectorAll('#options-section select, #options-section input, #options-section button').forEach(el => el.disabled = true);
        submitButton.disabled = true;
        dropArea.style.display = 'none';
        let completedCount = 0;

        const processingOptions = {
            format: formatSelect.value,
            bitrate: bitrateContainer.style.display !== 'none' ? bitrateSelect.value : null,
            bit_depth: bitDepthContainer.style.display !== 'none' ? bitDepthSelect.value : null,
            sample_rate: sampleRateSelect.value,
            lufs_preset: presetSelect.value,
            normalize: customNormalizationSection.style.display !== 'none' ? normalizeToggle.checked : false,
            target_lufs: targetLufsContainer.style.display !== 'none' ? targetLufsInput.value : null,
            limit_true_peak: truePeakToggle.checked,
            dither_method: ditherContainer.style.display !== 'none' ? ditherSelect.value : 'none',
            resampler: resamplerContainer.style.display !== 'none' ? resamplerSelect.value : 'swr',
            trim_silence: trimSilenceToggle.checked,
            fade_in: fadeToggle.checked ? fadeInInput.value : null,
            fade_out: fadeToggle.checked ? fadeOutInput.value : null,
            artist: artistInput.value,
            album: albumInput.value,
            title: titleInput.value,
            track_number: trackNumberInput.value,
            isrc: isrcInput.value,
        };

        for (let i = 0; i < fileQueue.length; i++) {
            updateQueueSummary(i + 1, fileQueue.length);
            const item = fileQueue[i];
            const cardElement = document.getElementById(`file-item-${i}`);
            try {
                updateCardStatus(cardElement, 'processing', 'Wysyłanie...');
                const taskStatusUrl = await uploadFile(item.file, processingOptions, cardElement);
                updateCardStatus(cardElement, 'processing', 'Przetwarzanie...');
                const finalData = await pollForTaskResult(taskStatusUrl);
                updateCardStatus(cardElement, 'completed', 'Ukończono');
                displayResult(finalData.result, cardElement);
                completedCount++;
            } catch (error) {
                updateCardStatus(cardElement, 'failed', 'Błąd');
                displayError(error.message, cardElement);
            }
        }

        isProcessingQueue = false;
        updateQueueSummary(completedCount, fileQueue.length, true);
        submitButton.textContent = "Prześlij nowe pliki";
        submitButton.disabled = false;
        submitButton.onclick = () => location.reload();
    }

    function uploadFile(file, options, uiElement) {
        return new Promise((resolve, reject) => {
            const progressBar = uiElement.querySelector('.progress-bar');
            uiElement.querySelector('.progress').style.display = 'block';
            const formData = new FormData();
            formData.append('file', file);
            formData.append('options', JSON.stringify(options));
            const coverArtFile = coverArtInput.files[0];
            if (coverArtFile) {
                formData.append('cover_art', coverArtFile);
            }
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/audio/upload-and-process', true);
            xhr.upload.addEventListener('progress', e => {
                if (e.lengthComputable) progressBar.style.width = Math.round((e.loaded / e.total) * 100) + '%';
            });
            xhr.onload = function() {
                if (xhr.status === 202) resolve(JSON.parse(xhr.responseText).status_url);
                else reject(new Error(JSON.parse(xhr.responseText)?.error || `Błąd serwera ${xhr.status}`));
            };
            xhr.onerror = () => reject(new Error('Błąd sieciowy.'));
            xhr.send(formData);
        });
    }

    function pollForTaskResult(statusUrl) {
         return new Promise((resolve, reject) => {
            const interval = setInterval(() => {
                fetch(statusUrl)
                    .then(response => response.ok ? response.json() : Promise.reject(new Error(`Błąd HTTP ${response.status}`)))
                    .then(data => {
                        if (data.status === 'COMPLETED') {
                            clearInterval(interval); 
                            resolve(data);
                        } else if (data.status === 'FAILED') {
                            clearInterval(interval); 
                            reject(new Error(JSON.parse(data.result)?.error || 'Nieznany błąd wykonania.'));
                        }
                        // Still processing - continue polling
                    })
                    .catch(error => { 
                        clearInterval(interval); 
                        reject(error); 
                    });
            }, POLLING_INTERVAL);
        });
    }

    function displayResult(resultJsonString, uiElement) {
        const results = JSON.parse(resultJsonString);
        const resultsDiv = uiElement.querySelector('.file-card-results');
        uiElement.querySelector('.progress').style.display = 'none';
        resultsDiv.innerHTML = `
            <div class="file-card-metric">${LufsIcon}<span>${results.loudness_lufs.toFixed(1)} LUFS</span></div>
            <div class="file-card-metric">${DurationIcon}<span>${results.duration_seconds.toFixed(1)}s</span></div>
            <a href="${results.processed_file_url}" class="btn btn-success btn-sm" download>Pobierz</a>`;
        resultsDiv.style.display = 'grid';
    }
    
    function displayError(message, uiElement) {
        const resultsDiv = uiElement.querySelector('.file-card-results');
        uiElement.querySelector('.progress').style.display = 'none';
        resultsDiv.innerHTML = `<span class="text-danger small">${message}</span>`;
        resultsDiv.style.display = 'block';
    }

    function updateCardStatus(uiElement, status, text) {
        uiElement.className = `file-card status-${status}`;
        uiElement.querySelector('.file-card-status').textContent = text;
        const header = uiElement.querySelector('.file-card-header');
        if (header.querySelector('svg')) header.querySelector('svg').remove();
        if (status === 'completed') header.insertAdjacentHTML('beforeend', SuccessIcon);
        if (status === 'failed') header.insertAdjacentHTML('beforeend', ErrorIcon);
    }
    
    function updateQueueSummary(processed = 0, total = fileQueue.length, finished = false) {
        if (total === 0) {
            queueSection.style.display = 'none';
            return;
        }
        queueSummary.textContent = finished ? `Przetwarzanie zakończone: ${processed} z ${total} plików ukończono.` : `Postęp kolejki: ${processed} / ${total}`;
    }

    function validateFile(file) {
        if (!ALLOWED_MIME_TYPES.includes(file.type)) {
            showError(`Niewłaściwy typ pliku: ${file.name}.`); return false;
        }
        if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
            showError(`Plik ${file.name} jest za duży (max ${MAX_FILE_SIZE_MB} MB).`); return false;
        }
        return true;
    }

    function setupDragAndDrop() {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, e => { e.preventDefault(); e.stopPropagation(); }, false);
        });
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => dropArea.classList.add('is-dragover'), false);
        });
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => dropArea.classList.remove('is-dragover'), false);
        });
        dropArea.addEventListener('drop', (e) => handleFiles(e.dataTransfer.files), false);
    }
    
    function showError(message) {
        fileErrorDiv.textContent = message;
        fileErrorDiv.style.display = 'block';
    }
});
