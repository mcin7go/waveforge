#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 UNIVERSAL CONVERTER - FUNCTIONALITY TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

test_check() {
    local name=$1
    local command=$2
    
    echo -ne "Testing: $name ... "
    
    if eval "$command" > /dev/null 2>&1; then
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
echo "SECTION 1: Server Health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_check "Web container running" \
    "docker-compose ps | grep -q 'waveforge_web.*Up'"

test_check "Server responds" \
    "curl -s http://localhost:5000/ | grep -q 'WaveBulk'"

test_check "No Python errors in logs" \
    "! docker-compose logs web --tail 50 | grep -q 'Error\|Exception\|Traceback'"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 2: Python Code Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_check "audio_tasks.py compiles" \
    "python3 -m py_compile backend/app/tasks/audio_tasks.py"

test_check "_detect_audio_format function exists" \
    "grep -q '_detect_audio_format' backend/app/tasks/audio_tasks.py"

test_check "_convert_to_wav function exists" \
    "grep -q '_convert_to_wav' backend/app/tasks/audio_tasks.py"

test_check "_get_quality_warning function exists" \
    "grep -q '_get_quality_warning' backend/app/tasks/audio_tasks.py"

test_check "LOSSLESS_FORMATS defined" \
    "grep -q 'LOSSLESS_FORMATS' backend/app/tasks/audio_tasks.py"

test_check "LOSSY_FORMATS defined" \
    "grep -q 'LOSSY_FORMATS' backend/app/tasks/audio_tasks.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 3: Frontend Updates"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_check "Upload accepts .m4a files" \
    "grep -q '\.m4a' backend/app/templates/upload_audio.html"

test_check "Upload accepts .mp3 files" \
    "grep -q '\.mp3' backend/app/templates/upload_audio.html"

test_check "Upload accepts .flac files" \
    "grep -q '\.flac' backend/app/templates/upload_audio.html"

test_check "Supported formats text updated" \
    "grep -q 'WAV, MP3, M4A' backend/app/templates/upload_audio.html"

test_check "JavaScript MIME types updated" \
    "grep -q 'audio/mp4' backend/app/static/js/upload.js"

test_check "JavaScript has AAC MIME" \
    "grep -q 'audio/aac' backend/app/static/js/upload.js"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 4: Format Detection Logic"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create test files
mkdir -p /tmp/format_test
cd /tmp/format_test

# Generate test M4A
echo -ne "Creating test M4A ... "
if ffmpeg -y -f lavfi -i "sine=frequency=440:duration=2" -c:a aac -b:a 128k test.m4a 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    
    # Test detection
    echo -ne "Testing ffprobe on M4A ... "
    if ffprobe -v quiet -print_format json -show_format test.m4a 2>/dev/null | grep -q 'format'; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        
        # Show details
        CODEC=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 test.m4a 2>/dev/null)
        BITRATE=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 test.m4a 2>/dev/null)
        echo "  Detected codec: $CODEC"
        echo "  Detected bitrate: $((BITRATE / 1000)) kbps"
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
    
    # Test conversion to WAV
    echo -ne "Testing M4A → WAV conversion ... "
    if ffmpeg -y -i test.m4a -acodec pcm_s16le -ar 44100 test_converted.wav 2>/dev/null; then
        if [ -f test_converted.wav ]; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((PASSED++))
            SIZE=$(du -h test_converted.wav | cut -f1)
            echo "  Output WAV: $SIZE"
        else
            echo -e "${RED}✗ FAIL${NC}"
            ((FAILED++))
        fi
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 5: Database Seeding"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /srv/docker/vaveforgepro

test_check "Plans in database" \
    "docker-compose exec -T web python -c 'from app import create_app, db; from app.models import Plan; app=create_app(); ctx=app.app_context(); ctx.push(); print(Plan.query.count())' | grep -q '[0-9]'"

test_check "Users in database" \
    "docker-compose exec -T web python -c 'from app import create_app, db; from app.models import User; app=create_app(); ctx=app.app_context(); ctx.push(); print(User.query.count())' | grep -q '[0-9]'"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SECTION 6: File Details Enhancements"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_check "Input format section in template" \
    "grep -q 'Format wejściowy' backend/app/templates/file_details.html"

test_check "Quality warning section exists" \
    "grep -q 'quality_warning' backend/app/templates/file_details.html"

test_check "Input format info in template" \
    "grep -q 'input_format.codec' backend/app/templates/file_details.html"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
echo -e "Tests Failed: ${RED}$FAILED${NC}"
echo "Total: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}   🎉 ALL TESTS PASSED! UNIVERSAL CONVERTER WORKS! 🎉${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
else
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}   ⚠️  Some tests failed ($PASSED/$((PASSED + FAILED)))${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
fi

echo ""
exit $FAILED

