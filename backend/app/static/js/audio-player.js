/**
 * WaveBulk - Professional Audio Player
 * Features: Waveform, Spectrogram, Frequency Analyzer, Phase Correlation, A/B Comparison
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on file details page
    if (!document.getElementById('waveform')) return;

    // Get audio file URL from template
    const audioUrl = document.querySelector('.file-actions a[download]')?.href;
    if (!audioUrl) {
        console.error('No audio file URL found');
        return;
    }

    // ============================================
    // WAVESURFER INSTANCES
    // ============================================
    
    let wavesurfer = null;
    let wavesurferBefore = null;
    let wavesurferAfter = null;
    let currentMode = 'single';
    
    // Audio context for analyzers
    let audioContext = null;
    let analyser = null;
    let phaseAnalyser = null;
    let animationId = null;

    // ============================================
    // INITIALIZE WAVESURFER (SINGLE MODE)
    // ============================================
    
    function initSinglePlayer() {
        wavesurfer = WaveSurfer.create({
            container: '#waveform',
            waveColor: '#4a9eff',
            progressColor: '#007bff',
            cursorColor: '#fff',
            barWidth: 2,
            barGap: 1,
            barRadius: 2,
            height: 120,
            normalize: true,
            backend: 'WebAudio',
            plugins: [
                WaveSurfer.timeline.create({
                    container: '#waveform',
                    height: 20,
                    primaryLabelInterval: 5,
                    secondaryLabelInterval: 1,
                }),
                WaveSurfer.minimap.create({
                    container: '#waveform-minimap',
                    waveColor: '#777',
                    progressColor: '#999',
                    height: 60,
                }),
                WaveSurfer.regions.create(),
            ]
        });

        wavesurfer.load(audioUrl);
        
        // Setup Web Audio API analyzers
        wavesurfer.on('ready', function() {
            setupAudioAnalyzers(wavesurfer);
        });

        // Time update
        wavesurfer.on('audioprocess', updateTimeDisplay);
        wavesurfer.on('seek', updateTimeDisplay);
        
        return wavesurfer;
    }

    // ============================================
    // INITIALIZE A/B COMPARISON
    // ============================================
    
    function initComparisonPlayers() {
        // For now, load same file for both (in real app, you'd load original + processed)
        wavesurferAfter = WaveSurfer.create({
            container: '#waveform-after',
            waveColor: '#4ecdc4',
            progressColor: '#2aa198',
            height: 120,
            normalize: true,
            plugins: [
                WaveSurfer.timeline.create({
                    container: '#waveform-after',
                    height: 20,
                }),
            ]
        });

        wavesurferBefore = WaveSurfer.create({
            container: '#waveform-before',
            waveColor: '#f39c12',
            progressColor: '#e67e22',
            height: 120,
            normalize: true,
            plugins: [
                WaveSurfer.timeline.create({
                    container: '#waveform-before',
                    height: 20,
                }),
            ]
        });

        // Load files (in production, load different files)
        wavesurferAfter.load(audioUrl);
        wavesurferBefore.load(audioUrl); // This would be original file URL

        // Sync playback
        wavesurferAfter.on('audioprocess', () => {
            if (wavesurferBefore && !wavesurferBefore.isPlaying()) {
                const currentTime = wavesurferAfter.getCurrentTime();
                wavesurferBefore.seekTo(currentTime / wavesurferBefore.getDuration());
            }
        });
    }

    // ============================================
    // AUDIO ANALYZERS (Web Audio API)
    // ============================================
    
    function setupAudioAnalyzers(ws) {
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }

        const backend = ws.backend;
        if (!backend.ac) return;

        // Frequency Analyzer
        analyser = backend.ac.createAnalyser();
        analyser.fftSize = 2048;
        analyser.smoothingTimeConstant = 0.8;
        
        // Phase Analyzer (for stereo correlation)
        phaseAnalyser = backend.ac.createAnalyser();
        phaseAnalyser.fftSize = 2048;
        
        // Connect to audio graph
        if (backend.gainNode) {
            backend.gainNode.connect(analyser);
            backend.gainNode.connect(phaseAnalyser);
        }
    }

    // ============================================
    // FREQUENCY ANALYZER VISUALIZATION
    // ============================================
    
    function drawFrequencyAnalyzer() {
        const canvas = document.getElementById('frequency-canvas');
        if (!canvas || !analyser) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width = canvas.offsetWidth;
        const height = canvas.height = canvas.offsetHeight;

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        function draw() {
            if (!document.getElementById('toggle-analyzer')?.classList.contains('active')) {
                return;
            }

            analyser.getByteFrequencyData(dataArray);

            // Clear canvas
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(0, 0, width, height);

            const barWidth = width / bufferLength * 2.5;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                const barHeight = (dataArray[i] / 255) * height;

                // Color gradient based on frequency
                const hue = (i / bufferLength) * 120; // 0 (red) to 120 (green)
                ctx.fillStyle = `hsl(${hue + 200}, 80%, ${50 + dataArray[i] / 255 * 20}%)`;

                ctx.fillRect(x, height - barHeight, barWidth, barHeight);
                x += barWidth + 1;
            }

            animationId = requestAnimationFrame(draw);
        }

        draw();
    }

    // ============================================
    // PHASE CORRELATION METER (Lissajous)
    // ============================================
    
    function drawPhaseCorrelation() {
        const canvas = document.getElementById('phase-canvas');
        if (!canvas || !phaseAnalyser) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width = canvas.offsetWidth;
        const height = canvas.height = canvas.offsetHeight;

        const bufferLength = phaseAnalyser.fftSize;
        const dataArray = new Float32Array(bufferLength);

        function draw() {
            if (!document.getElementById('toggle-phase')?.classList.contains('active')) {
                return;
            }

            phaseAnalyser.getFloatTimeDomainData(dataArray);

            // Clear canvas
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(0, 0, width, height);

            // Draw grid
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(width / 2, 0);
            ctx.lineTo(width / 2, height);
            ctx.moveTo(0, height / 2);
            ctx.lineTo(width, height / 2);
            ctx.stroke();

            // Draw Lissajous figure
            ctx.beginPath();
            ctx.strokeStyle = '#4ecdc4';
            ctx.lineWidth = 2;

            let correlation = 0;
            let count = 0;

            for (let i = 0; i < bufferLength; i += 2) {
                const left = dataArray[i];
                const right = dataArray[i + 1] || left;

                const x = ((left + 1) / 2) * width;
                const y = ((right + 1) / 2) * height;

                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }

                // Calculate correlation
                correlation += left * right;
                count++;
            }

            ctx.stroke();

            // Update correlation value
            const correlationValue = count > 0 ? (correlation / count).toFixed(2) : 0;
            const phaseValueEl = document.getElementById('phase-value');
            if (phaseValueEl) {
                phaseValueEl.textContent = correlationValue;
                
                // Color code based on correlation
                if (Math.abs(correlationValue) < 0.3) {
                    phaseValueEl.className = 'analyzer-value good';
                } else if (Math.abs(correlationValue) < 0.7) {
                    phaseValueEl.className = 'analyzer-value warning';
                } else {
                    phaseValueEl.className = 'analyzer-value danger';
                }
            }

            animationId = requestAnimationFrame(draw);
        }

        draw();
    }

    // ============================================
    // PLAYER CONTROLS
    // ============================================
    
    function updateTimeDisplay() {
        const current = wavesurfer.getCurrentTime();
        const duration = wavesurfer.getDuration();
        const timeEl = document.getElementById('time-display');
        
        if (timeEl) {
            timeEl.textContent = `${formatTime(current)} / ${formatTime(duration)}`;
        }
    }

    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    // ============================================
    // MODE SWITCHING (Single vs Comparison)
    // ============================================
    
    const modeBtns = document.querySelectorAll('.mode-btn');
    const singleView = document.getElementById('single-player-view');
    const comparisonView = document.getElementById('comparison-player-view');

    modeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const mode = this.dataset.mode;
            
            // Update button states
            modeBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Switch views
            if (mode === 'single') {
                singleView.style.display = 'block';
                comparisonView.style.display = 'none';
                
                if (!wavesurfer) {
                    wavesurfer = initSinglePlayer();
                }
                
                // Stop comparison players
                if (wavesurferBefore) wavesurferBefore.pause();
                if (wavesurferAfter) wavesurferAfter.pause();
                
                currentMode = 'single';
            } else {
                singleView.style.display = 'none';
                comparisonView.style.display = 'block';
                
                if (!wavesurferBefore || !wavesurferAfter) {
                    initComparisonPlayers();
                }
                
                // Stop single player
                if (wavesurfer) wavesurfer.pause();
                
                currentMode = 'comparison';
            }
        });
    });

    // ============================================
    // PLAYBACK CONTROLS (Single Mode)
    // ============================================
    
    const playPauseBtn = document.getElementById('play-pause');
    const playIcon = document.getElementById('play-icon');
    const stopBtn = document.getElementById('stop-btn');
    const volumeSlider = document.getElementById('volume');
    const speedSelect = document.getElementById('playback-speed');
    const zoomSlider = document.getElementById('zoom');
    const zoomValue = document.getElementById('zoom-value');

    if (playPauseBtn) {
        playPauseBtn.addEventListener('click', () => {
            if (wavesurfer) {
                wavesurfer.playPause();
                playIcon.textContent = wavesurfer.isPlaying() ? '⏸' : '▶';
            }
        });
    }

    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            if (wavesurfer) {
                wavesurfer.stop();
                playIcon.textContent = '▶';
            }
        });
    }

    if (volumeSlider) {
        volumeSlider.addEventListener('input', (e) => {
            const volume = e.target.value / 100;
            if (wavesurfer) wavesurfer.setVolume(volume);
        });
    }

    if (speedSelect) {
        speedSelect.addEventListener('change', (e) => {
            const speed = parseFloat(e.target.value);
            if (wavesurfer) wavesurfer.setPlaybackRate(speed);
        });
    }

    if (zoomSlider) {
        zoomSlider.addEventListener('input', (e) => {
            const zoom = parseInt(e.target.value);
            if (wavesurfer) wavesurfer.zoom(zoom);
            zoomValue.textContent = `${zoom}x`;
        });
    }

    // ============================================
    // A/B COMPARISON CONTROLS
    // ============================================
    
    const playPauseComparisonBtn = document.getElementById('play-pause-comparison');
    const switchABBtn = document.getElementById('switch-ab');
    let currentPlayer = 'after'; // 'before' or 'after'

    if (playPauseComparisonBtn) {
        playPauseComparisonBtn.addEventListener('click', () => {
            const activePlayer = currentPlayer === 'after' ? wavesurferAfter : wavesurferBefore;
            if (activePlayer) {
                activePlayer.playPause();
                const icon = playPauseComparisonBtn.querySelector('span');
                icon.textContent = activePlayer.isPlaying() ? '⏸' : '▶';
            }
        });
    }

    if (switchABBtn) {
        switchABBtn.addEventListener('click', () => {
            // Pause current
            const currentWS = currentPlayer === 'after' ? wavesurferAfter : wavesurferBefore;
            const nextWS = currentPlayer === 'after' ? wavesurferBefore : wavesurferAfter;
            
            const currentTime = currentWS.getCurrentTime();
            currentWS.pause();
            
            // Switch
            currentPlayer = currentPlayer === 'after' ? 'before' : 'after';
            
            // Update UI
            document.getElementById('player-before').classList.toggle('active');
            document.getElementById('player-after').classList.toggle('active');
            
            // Start new player at same position
            nextWS.seekTo(currentTime / nextWS.getDuration());
            nextWS.play();
        });
    }

    // ============================================
    // FEATURE TOGGLES
    // ============================================
    
    const toggleSpectrogram = document.getElementById('toggle-spectrogram');
    const toggleAnalyzer = document.getElementById('toggle-analyzer');
    const togglePhase = document.getElementById('toggle-phase');
    const toggleMarkers = document.getElementById('toggle-markers');
    
    const spectrogramContainer = document.getElementById('spectrogram');
    const analyzersContainer = document.getElementById('analyzers-container');
    const markersLegend = document.getElementById('markers-legend');

    if (toggleSpectrogram) {
        toggleSpectrogram.addEventListener('click', function() {
            this.classList.toggle('active');
            const isActive = this.classList.contains('active');
            
            if (isActive && wavesurfer && !wavesurfer.params.plugins.find(p => p.name === 'spectrogram')) {
                // Add spectrogram plugin dynamically
                const spectrogramPlugin = WaveSurfer.spectrogram.create({
                    container: '#spectrogram',
                    labels: true,
                    height: 200,
                    fftSamples: 512,
                });
                wavesurfer.registerPlugin(spectrogramPlugin);
            }
            
            if (spectrogramContainer) {
                spectrogramContainer.style.display = isActive ? 'block' : 'none';
            }
        });
    }

    if (toggleAnalyzer) {
        toggleAnalyzer.addEventListener('click', function() {
            this.classList.toggle('active');
            const isActive = this.classList.contains('active');
            
            if (analyzersContainer) {
                analyzersContainer.style.display = isActive || togglePhase?.classList.contains('active') ? 'grid' : 'none';
            }
            
            if (isActive) {
                drawFrequencyAnalyzer();
            } else {
                if (animationId) cancelAnimationFrame(animationId);
            }
        });
    }

    if (togglePhase) {
        togglePhase.addEventListener('click', function() {
            this.classList.toggle('active');
            const isActive = this.classList.contains('active');
            
            if (analyzersContainer) {
                analyzersContainer.style.display = isActive || toggleAnalyzer?.classList.contains('active') ? 'grid' : 'none';
            }
            
            if (isActive) {
                drawPhaseCorrelation();
            } else {
                if (animationId) cancelAnimationFrame(animationId);
            }
        });
    }

    if (toggleMarkers) {
        toggleMarkers.addEventListener('click', function() {
            this.classList.toggle('active');
            const isActive = this.classList.contains('active');
            
            if (markersLegend) {
                markersLegend.style.display = isActive ? 'flex' : 'none';
            }
            
            if (isActive) {
                addSmartMarkers();
            } else {
                clearMarkers();
            }
        });
    }

    // ============================================
    // SMART MARKERS (Based on LUFS/Peaks)
    // ============================================
    
    function addSmartMarkers() {
        if (!wavesurfer) return;

        // Get LUFS value from page
        const lufsElement = document.querySelector('.analysis-value');
        const lufsValue = lufsElement ? parseFloat(lufsElement.textContent) : null;
        
        const duration = wavesurfer.getDuration();
        
        // Example: Add regions based on LUFS threshold
        if (lufsValue) {
            if (lufsValue > -10) {
                // High LUFS - mark entire file as warning
                wavesurfer.addRegion({
                    start: 0,
                    end: duration,
                    color: 'rgba(220, 53, 69, 0.1)',
                    drag: false,
                    resize: false,
                });
            } else if (lufsValue > -14) {
                wavesurfer.addRegion({
                    start: 0,
                    end: duration,
                    color: 'rgba(255, 193, 7, 0.1)',
                    drag: false,
                    resize: false,
                });
            } else {
                wavesurfer.addRegion({
                    start: 0,
                    end: duration,
                    color: 'rgba(25, 135, 84, 0.1)',
                    drag: false,
                    resize: false,
                });
            }
        }

        // Simulate peak markers (in production, get from backend analysis)
        // Add marker at 2s (example peak)
        wavesurfer.addRegion({
            start: 2,
            end: 2.1,
            color: 'rgba(220, 53, 69, 0.5)',
            drag: false,
            resize: false,
        });
    }

    function clearMarkers() {
        if (wavesurfer) {
            wavesurfer.clearRegions();
        }
    }

    // ============================================
    // INITIALIZATION
    // ============================================
    
    // Initialize single player by default
    wavesurfer = initSinglePlayer();

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (wavesurfer) wavesurfer.destroy();
        if (wavesurferBefore) wavesurferBefore.destroy();
        if (wavesurferAfter) wavesurferAfter.destroy();
        if (animationId) cancelAnimationFrame(animationId);
    });
});

