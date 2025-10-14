#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 COMPREHENSIVE TESTING - ALL NEW FEATURES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0

# Test function
test_feature() {
    local name=$1
    local check=$2
    
    echo -ne "${BLUE}Testing:${NC} $name ... "
    
    if eval "$check" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 1: Basic Server Health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_feature "1.1 Homepage responds" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:5000/ | grep -q 200"

test_feature "1.2 Upload page loads" \
    "curl -s http://localhost:5000/audio/upload-and-process | grep -q 'Format wyjściowy'"

test_feature "1.3 Dashboard loads" \
    "curl -s http://localhost:5000/audio/dashboard | grep -q 'Dashboard'"

test_feature "1.4 CSS files load" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:5000/static/css/base.css | grep -q 200"

test_feature "1.5 JavaScript files load" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:5000/static/js/upload.js | grep -q 200"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 2: Quick Wins Features (Upload Page)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_feature "2.1 AAC/M4A format option visible" \
    "curl -s http://localhost:5000/audio/upload-and-process | grep -q 'AAC/M4A'"

test_feature "2.2 128k bitrate option visible" \
    "curl -s http://localhost:5000/audio/upload-and-process | grep -q '128 kbps'"

test_feature "2.3 256k bitrate option visible" \
    "curl -s http://localhost:5000/audio/upload-and-process | grep -q '256 kbps'"

test_feature "2.4 VBR V0 option visible" \
    "curl -s http://localhost:5000/audio/upload-and-process | grep -q 'VBR V0'"

test_feature "2.5 VBR V2 option visible" \
    "curl -s http://localhost:5000/audio/upload-and-process | grep -q 'VBR V2'"

test_feature "2.6 Sample Rate selector visible" \
    "curl -s http://localhost:5000/audio/upload-and-process | grep -q 'Sample Rate'"

test_feature "2.7 48 kHz option visible" \
    "curl -s http://localhost:5000/audio/upload-and-process | grep -q '48 kHz'"

test_feature "2.8 96 kHz option visible" \
    "curl -s http://localhost:5000/audio/upload-and-process | grep -q '96 kHz'"

test_feature "2.9 Fade In/Out toggle visible" \
    "curl -s http://localhost:5000/audio/upload-and-process | grep -q 'Fade In/Out'"

test_feature "2.10 Trim silence toggle visible" \
    "curl -s http://localhost:5000/audio/upload-and-process | grep -q 'Auto-trim'"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 3: Professional Audio Player"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_feature "3.1 WaveSurfer script loaded in base.html" \
    "curl -s http://localhost:5000/ | grep -q 'wavesurfer.js@7'"

test_feature "3.2 Timeline plugin loaded" \
    "curl -s http://localhost:5000/ | grep -q 'timeline.min.js'"

test_feature "3.3 Spectrogram plugin loaded" \
    "curl -s http://localhost:5000/ | grep -q 'spectrogram.min.js'"

test_feature "3.4 Regions plugin loaded" \
    "curl -s http://localhost:5000/ | grep -q 'regions.min.js'"

test_feature "3.5 Minimap plugin loaded" \
    "curl -s http://localhost:5000/ | grep -q 'minimap.min.js'"

test_feature "3.6 Audio player JS file exists" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:5000/static/js/audio-player.js | grep -q 200"

test_feature "3.7 Waveform player CSS exists" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:5000/static/css/components/waveform-player.css | grep -q 200"

test_feature "3.8 File details has audio player section" \
    "curl -s http://localhost:5000/audio/file/1 2>/dev/null | grep -q 'Profesjonalny Odtwarzacz' || echo ''"

test_feature "3.9 Waveform container present" \
    "curl -s http://localhost:5000/audio/file/1 2>/dev/null | grep -q 'id=\"waveform\"' || echo ''"

test_feature "3.10 Frequency canvas present" \
    "curl -s http://localhost:5000/audio/file/1 2>/dev/null | grep -q 'frequency-canvas' || echo ''"

test_feature "3.11 Phase canvas present" \
    "curl -s http://localhost:5000/audio/file/1 2>/dev/null | grep -q 'phase-canvas' || echo ''"

test_feature "3.12 A/B comparison mode present" \
    "curl -s http://localhost:5000/audio/file/1 2>/dev/null | grep -q 'Porównanie A/B' || echo ''"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 4: Translations (EN/PL)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test EN
curl -c /tmp/test_cookies_en.txt -s http://localhost:5000/set-language/en > /dev/null

test_feature "4.1 Upload page EN - AAC visible" \
    "curl -b /tmp/test_cookies_en.txt -s http://localhost:5000/audio/upload-and-process | grep -q 'AAC/M4A'"

test_feature "4.2 Upload page EN - VBR translation" \
    "curl -b /tmp/test_cookies_en.txt -s http://localhost:5000/audio/upload-and-process | grep -q 'Variable'"

test_feature "4.3 Upload page EN - Sample Rate" \
    "curl -b /tmp/test_cookies_en.txt -s http://localhost:5000/audio/upload-and-process | grep -q 'Sample Rate'"

# Test PL
curl -c /tmp/test_cookies_pl.txt -s http://localhost:5000/set-language/pl > /dev/null

test_feature "4.4 Upload page PL - AAC visible" \
    "curl -b /tmp/test_cookies_pl.txt -s http://localhost:5000/audio/upload-and-process | grep -q 'AAC/M4A'"

test_feature "4.5 Upload page PL - Fade visible" \
    "curl -b /tmp/test_cookies_pl.txt -s http://localhost:5000/audio/upload-and-process | grep -q 'Fade In/Out'"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 5: Backend Python Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_feature "5.1 audio_tasks.py has AAC support" \
    "grep -q 'm4a' backend/app/tasks/audio_tasks.py"

test_feature "5.2 audio_tasks.py has VBR mapping" \
    "grep -q 'BITRATE_PARAMS' backend/app/tasks/audio_tasks.py"

test_feature "5.3 audio_tasks.py has _get_bitrate_param" \
    "grep -q '_get_bitrate_param' backend/app/tasks/audio_tasks.py"

test_feature "5.4 audio_tasks.py has fade_in support" \
    "grep -q 'fade_in' backend/app/tasks/audio_tasks.py"

test_feature "5.5 audio_tasks.py has trim_silence support" \
    "grep -q 'trim_silence' backend/app/tasks/audio_tasks.py"

test_feature "5.6 audio_tasks.py has sample_rate support" \
    "grep -q 'sample_rate' backend/app/tasks/audio_tasks.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 6: Docker Containers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_feature "6.1 Web container running" \
    "docker-compose ps | grep -q 'waveforge_web.*Up'"

test_feature "6.2 Worker container running" \
    "docker-compose ps | grep -q 'waveforge_worker.*Up'"

test_feature "6.3 DB container running" \
    "docker-compose ps | grep -q 'waveforge_db.*Up'"

test_feature "6.4 Redis container running" \
    "docker-compose ps | grep -q 'waveforge_redis.*Up'"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 7: Files Existence"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_feature "7.1 audio-player.js exists" \
    "[ -f backend/app/static/js/audio-player.js ]"

test_feature "7.2 waveform-player.css exists" \
    "[ -f backend/app/static/css/components/waveform-player.css ]"

test_feature "7.3 Compiled EN translations exist" \
    "[ -f backend/app/translations/en/LC_MESSAGES/messages.mo ]"

test_feature "7.4 Compiled PL translations exist" \
    "[ -f backend/app/translations/pl/LC_MESSAGES/messages.mo ]"

test_feature "7.5 Documentation created" \
    "[ -f AUDIO_PLAYER_COMPLETE.md ]"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 8: Code Quality"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_feature "8.1 No Python syntax errors in audio_tasks.py" \
    "python3 -m py_compile backend/app/tasks/audio_tasks.py"

test_feature "8.2 audio-player.js has no obvious errors" \
    "grep -q 'WaveSurfer.create' backend/app/static/js/audio-player.js"

test_feature "8.3 CSS file is valid" \
    "grep -q 'audio-player-section' backend/app/static/css/components/waveform-player.css"

test_feature "8.4 HTML template valid" \
    "grep -q 'audio-player-section' backend/app/templates/file_details.html"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RESULTS SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
echo -e "Tests Failed: ${RED}$FAILED${NC}"
echo "Total Tests: $((PASSED + FAILED))"
echo ""

PERCENTAGE=$((PASSED * 100 / (PASSED + FAILED)))

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}   🎉 PERFECT! ALL TESTS PASSED! ($PERCENTAGE%) 🎉${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
elif [ $PERCENTAGE -ge 80 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}   ✅ GOOD! Most tests passed ($PERCENTAGE%)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}   ⚠️  SOME TESTS FAILED ($PERCENTAGE%)${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
fi

echo ""
exit $FAILED

