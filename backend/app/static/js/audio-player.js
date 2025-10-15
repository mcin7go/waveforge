/**
 * WaveBulk - Professional Audio Player
 * Features: Waveform, Spectrogram, Frequency Analyzer, Phase Correlation, A/B Comparison
 */

document.addEventListener('DOMContentLoaded', function() {
    try {
        // Check if we're on file details page
        if (!document.getElementById('waveform')) {
            return;
        }

    // Check if WaveSurfer is loaded
    if (typeof WaveSurfer === 'undefined') {
        console.error('WaveSurfer library not loaded');
        return;
    }

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
        if (typeof WaveSurfer === 'undefined') {
            console.error('WaveSurfer not loaded');
            return null;
        }
        
        const plugins = [];
        
        // Add plugins if available
        if (window.TimelinePlugin) {
            plugins.push(TimelinePlugin.create({
                container: '#waveform',
                height: 20,
                primaryLabelInterval: 5,
                secondaryLabelInterval: 1,
            }));
        }
        
        if (window.MinimapPlugin) {
            plugins.push(MinimapPlugin.create({
                container: '#waveform-minimap',
                waveColor: '#777',
                progressColor: '#999',
                height: 60,
            }));
        }
        
        // Check for regions plugin (different names in different versions)
        if (window.RegionsPlugin) {
            window.regionsPlugin = RegionsPlugin.create();
            plugins.push(window.regionsPlugin);
            console.log('[SETUP] RegionsPlugin created');
        } else if (window.WaveSurfer && window.WaveSurfer.Regions) {
            window.regionsPlugin = window.WaveSurfer.Regions.create();
            plugins.push(window.regionsPlugin);
            console.log('[SETUP] WaveSurfer.Regions created');
        } else {
            console.log('[SETUP] RegionsPlugin not available');
            console.log('[SETUP] Available plugins:', Object.keys(window).filter(k => k.includes('Plugin') || k.includes('Regions')));
        }

        
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
            plugins: plugins,
        });

        wavesurfer.load(audioUrl);
        
        // Setup Web Audio API analyzers when audio starts playing
        // Re-setup on each play because bufferNode changes
        wavesurfer.on('play', function() {
            setupAudioAnalyzers(wavesurfer);
            
            // Auto-connect analyzer when audio starts playing (if analyzer was requested)
            if (analyser && !window.audioSourceConnected && wavesurfer.media && wavesurfer.media.bufferNode) {
                try {
                    console.log('[SETUP] AUTO-CONNECTING analyzer on play...');
                    wavesurfer.media.bufferNode.connect(analyser);
                    analyser.connect(wavesurfer.media.bufferNode.context.destination);
                    
                    if (phaseAnalyser) {
                        wavesurfer.media.bufferNode.connect(phaseAnalyser);
                        phaseAnalyser.connect(wavesurfer.media.bufferNode.context.destination);
                    }
                    
                    window.audioSourceConnected = true;
                    console.log('[SETUP] ✓✓✓ AUTO-CONNECTED to bufferNode!');
                } catch (error) {
                    console.error('[SETUP] ERROR auto-connecting:', error);
                }
            }
        });

        // Time update
        wavesurfer.on('audioprocess', updateTimeDisplay);
        wavesurfer.on('seek', updateTimeDisplay);
        
        // Reset audio connection when audio stops
        wavesurfer.on('pause', function() {
            window.audioSourceConnected = false;
        });
        
        wavesurfer.on('finish', function() {
            window.audioSourceConnected = false;
        });
        
        return wavesurfer;
    }

    // ============================================
    // INITIALIZE A/B COMPARISON
    // ============================================
    
    function initComparisonPlayers() {
        if (typeof WaveSurfer === 'undefined') {
            console.error('WaveSurfer not loaded');
            return;
        }
        
        const pluginsAfter = [];
        const pluginsBefore = [];
        
        if (window.TimelinePlugin) {
            pluginsAfter.push(TimelinePlugin.create({
                container: '#waveform-after',
                height: 20,
            }));
            pluginsBefore.push(TimelinePlugin.create({
                container: '#waveform-before',
                height: 20,
            }));
        }
        
        // For now, load same file for both (in real app, you'd load original + processed)
        wavesurferAfter = WaveSurfer.create({
            container: '#waveform-after',
            waveColor: '#4ecdc4',
            progressColor: '#2aa198',
            height: 80,
            normalize: true,
            plugins: pluginsAfter
        });

        wavesurferBefore = WaveSurfer.create({
            container: '#waveform-before',
            waveColor: '#f39c12',
            progressColor: '#e67e22',
            height: 80,
            normalize: true,
            plugins: pluginsBefore
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
        console.log('[SETUP] Setting up audio analyzers');
        
        try {
            // CRITICAL: Must use WaveSurfer's AudioContext, not create a new one!
            if (ws.media && ws.media.audioContext) {
                console.log('[SETUP] ✓ Using ws.media.audioContext (WaveSurfer internal)');
                audioContext = ws.media.audioContext;
            } else if (ws.media && ws.media.bufferNode && ws.media.bufferNode.context) {
                console.log('[SETUP] ✓ Using ws.media.bufferNode.context');
                audioContext = ws.media.bufferNode.context;
            } else {
                console.error('[SETUP] ERROR: Cannot find WaveSurfer AudioContext!');
                return;
            }
            
            console.log('[SETUP] AudioContext:', audioContext);
            
            // Create analyzers only once
            if (!analyser) {
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 2048;
                analyser.smoothingTimeConstant = 0.8;
                
                phaseAnalyser = audioContext.createAnalyser();
                phaseAnalyser.fftSize = 2048;
                
                console.log('[SETUP] Analyzers created');
            }
            
            // bufferNode only exists when audio is playing
            if (!window.audioSourceConnected) {
                if (ws.media && ws.media.bufferNode) {
                    console.log('[SETUP] Connecting to bufferNode (audio is playing)');
                    ws.media.bufferNode.connect(analyser);
                    ws.media.bufferNode.connect(phaseAnalyser);
                    analyser.connect(audioContext.destination);
                    phaseAnalyser.connect(audioContext.destination);
                    window.audioSourceConnected = true;
                    console.log('[SETUP] ✓✓✓ Connected to bufferNode!');
                } else {
                    console.log('[SETUP] ⚠ bufferNode not available yet. Will auto-connect on play.');
                    // Connection will happen when audio starts playing
                }
            }
        } catch (error) {
            console.error('[SETUP] Error:', error);
        }
    }

    // ============================================
    // FREQUENCY ANALYZER VISUALIZATION
    // ============================================
    
    function drawFrequencyAnalyzer() {
        const canvas = document.getElementById('frequency-canvas');
        if (!canvas) {
            console.error('[FREQ] Canvas not found');
            return;
        }
        
        // Setup analyzer on first call
        if (!analyser) {
            console.log('[FREQ] Setting up analyzer for first time');
            
            if (!wavesurfer) {
                console.error('[FREQ] WaveSurfer instance not available');
                return;
            }
            
            try {
                if (!audioContext) {
                    audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    console.log('[FREQ] Created AudioContext');
                }
                
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 2048;
                analyser.smoothingTimeConstant = 0.8;
                console.log('[FREQ] Analyzer created');
                
                // Try to find and connect audio element
                const tryConnect = () => {
                    const audio = document.querySelector('#waveform audio') || document.querySelector('audio');
                    console.log('[FREQ] Looking for audio element:', !!audio);
                    
                    if (audio && !window.audioSourceConnected) {
                        try {
                            const source = audioContext.createMediaElementSource(audio);
                            source.connect(analyser);
                            analyser.connect(audioContext.destination);
                            window.audioSourceConnected = true;
                            console.log('[FREQ] ✓ Analyzer connected to audio successfully');
                        } catch (e) {
                            console.warn('[FREQ] Connection error:', e.message);
                        }
                    } else if (audio && window.audioSourceConnected) {
                        console.log('[FREQ] Audio already connected');
                    } else {
                        console.warn('[FREQ] Audio element not found yet');
                    }
                };
                
                tryConnect();
                setTimeout(tryConnect, 500);
                setTimeout(tryConnect, 1000);
            } catch (error) {
                console.error('[FREQ] Error creating analyzer:', error);
                return;
            }
        }

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

            // Draw phase correlation line
            ctx.beginPath();
            ctx.strokeStyle = '#4ecdc4';
            ctx.lineWidth = 2;

            const sliceWidth = width * 1.0 / bufferLength;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                const v = dataArray[i];
                const y = (v + 1) * height / 2;

                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }

                x += sliceWidth;
            }

            ctx.stroke();

            // Draw phase info
            ctx.fillStyle = '#4ecdc4';
            ctx.font = '14px monospace';
            ctx.fillText('Phase Correlation', 10, 20);
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
            
            if (isActive && wavesurfer && !window.spectrogramPluginInstance) {
                // Add spectrogram plugin dynamically
                try {
                    window.spectrogramPluginInstance = WaveSurfer.Spectrogram.create({
                        container: '#spectrogram',
                        labels: true,
                        height: 200,
                        fftSamples: 512,
                    });
                    wavesurfer.registerPlugin(window.spectrogramPluginInstance);
                    console.log('[SPECTRO] Plugin created and registered');
                } catch (error) {
                    console.error('[SPECTRO] Error creating plugin:', error);
                }
            }
            
            // Show/hide spectrogram container
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
                // Setup analyzers if not done yet
                if (!analyser && wavesurfer) {
                    setupAudioAnalyzers(wavesurfer);
                }
                drawFrequencyAnalyzer();
            } else {
                if (animationId) {
                    cancelAnimationFrame(animationId);
                    animationId = null;
                }
            }
        });
    }

    if (togglePhase) {
        togglePhase.addEventListener('click', function() {
            this.classList.toggle('active');
            const isActive = this.classList.contains('active');
            
            if (analyzersContainer) {
                analyzersContainer.style.display = isActive || toggleAnalyzer?.classList.contains('active') ? 'grid' : 'none';
                console.log('[PHASE] Container display set to:', analyzersContainer.style.display);
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
            
            console.log('[MARKERS] Toggle clicked, active:', isActive);
            console.log('[MARKERS] markersLegend exists:', !!markersLegend);
            console.log('[MARKERS] window.regionsPlugin exists:', !!window.regionsPlugin);
            
            if (markersLegend) {
                markersLegend.style.display = isActive ? 'flex' : 'none';
                console.log('[MARKERS] Legend display set to:', markersLegend.style.display);
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
        console.log('[MARKERS] addSmartMarkers called');
        console.log('[MARKERS] wavesurfer exists:', !!wavesurfer);
        console.log('[MARKERS] regionsPlugin exists:', !!window.regionsPlugin);
        
        if (!wavesurfer || !window.regionsPlugin) {
            console.error('WaveSurfer or Regions plugin not available');
            return;
        }

        try {
            // Get LUFS value from page
            const lufsElement = document.querySelector('.analysis-value');
            const lufsValue = lufsElement ? parseFloat(lufsElement.textContent) : null;
            
            const duration = wavesurfer.getDuration();
            
            // Clear existing regions
            window.regionsPlugin.clearRegions();
            
            // Example: Add regions based on LUFS threshold
            if (lufsValue) {
                let color;
                if (lufsValue > -10) {
                    color = 'rgba(220, 53, 69, 0.1)';
                } else if (lufsValue > -14) {
                    color = 'rgba(255, 193, 7, 0.1)';
                } else {
                    color = 'rgba(25, 135, 84, 0.1)';
                }
                
                window.regionsPlugin.addRegion({
                    start: 0,
                    end: duration,
                    color: color,
                    drag: false,
                    resize: false,
                });
            }

            // Simulate peak markers (in production, get from backend analysis)
            window.regionsPlugin.addRegion({
                start: 2,
                end: 2.1,
                color: 'rgba(220, 53, 69, 0.5)',
                drag: false,
                resize: false,
            });
            
            console.log('Markers added successfully');
        } catch (error) {
            console.error('Error adding markers:', error);
        }
    }

    function clearMarkers() {
        if (window.regionsPlugin) {
            window.regionsPlugin.clearRegions();
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
    
    } catch (error) {
        console.error('[DEBUG] Error in audio-player.js:', error);
    }
});


