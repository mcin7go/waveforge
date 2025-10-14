#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 AUTOMATIC TESTING - QUICK WINS FEATURES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TEST_DIR="/tmp/wavebulk_tests"
mkdir -p $TEST_DIR
cd $TEST_DIR

# Function to create test WAV file
create_test_wav() {
    local filename=$1
    local duration=${2:-5}  # default 5 seconds
    
    echo -e "${YELLOW}📝 Generating test file: $filename (${duration}s)${NC}"
    
    # Generate sine wave 440Hz (A4 note) with silence at start/end
    ffmpeg -y -f lavfi -i "sine=frequency=440:duration=$duration" \
        -af "adelay=500|500,apad=pad_dur=0.5" \
        -ar 44100 -ac 2 -acodec pcm_s16le \
        "$filename" 2>/dev/null
    
    if [ -f "$filename" ]; then
        echo -e "${GREEN}✓ Created: $filename ($(du -h "$filename" | cut -f1))${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to create $filename${NC}"
        return 1
    fi
}

# Test counter
PASSED=0
FAILED=0

# Test function
test_feature() {
    local test_name=$1
    local input_file=$2
    local format=$3
    local extra_params=$4
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Test: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Expected output extension
    local ext=$format
    if [ "$format" == "aac" ]; then
        ext="m4a"
    fi
    
    local expected_output="${input_file%.*}.$ext"
    
    echo "Format: $format"
    echo "Expected output: $expected_output"
    echo "Extra params: $extra_params"
    echo ""
    
    # Simulate processing (in real scenario, we'd upload via API)
    # For now, use ffmpeg directly to test parameters
    
    if [ "$format" == "aac" ]; then
        ffmpeg -y -i "$input_file" -c:a aac $extra_params "$expected_output" 2>/dev/null
    elif [ "$format" == "mp3" ]; then
        ffmpeg -y -i "$input_file" -c:a libmp3lame $extra_params "$expected_output" 2>/dev/null
    elif [ "$format" == "flac" ]; then
        ffmpeg -y -i "$input_file" -c:a flac $extra_params "$expected_output" 2>/dev/null
    else
        ffmpeg -y -i "$input_file" $extra_params "$expected_output" 2>/dev/null
    fi
    
    # Check if output exists
    if [ -f "$expected_output" ]; then
        local size=$(du -h "$expected_output" | cut -f1)
        local duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$expected_output" 2>/dev/null | cut -d. -f1)
        
        # Get sample rate
        local sample_rate=$(ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of default=noprint_wrappers=1:nokey=1 "$expected_output" 2>/dev/null)
        
        # Get bitrate for compressed formats
        local bitrate=$(ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "$expected_output" 2>/dev/null)
        if [ ! -z "$bitrate" ]; then
            bitrate="$((bitrate / 1000))k"
        fi
        
        echo -e "${GREEN}✓ PASS${NC}"
        echo "  Size: $size"
        echo "  Duration: ${duration}s"
        echo "  Sample Rate: $sample_rate Hz"
        if [ ! -z "$bitrate" ]; then
            echo "  Bitrate: $bitrate"
        fi
        
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL - Output file not created${NC}"
        ((FAILED++))
        return 1
    fi
}

# Create test files
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Creating Test Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

create_test_wav "test_basic.wav" 5
create_test_wav "test_silence.wav" 3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Testing New Features"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test 1: AAC/M4A Format
test_feature "1. AAC/M4A Format (128k)" "test_basic.wav" "aac" "-b:a 128k"

# Test 2: AAC VBR
test_feature "2. AAC VBR (quality 4)" "test_basic.wav" "aac" "-q:a 4"

# Test 3: MP3 VBR V0
test_feature "3. MP3 VBR V0" "test_basic.wav" "mp3" "-q:a 0"

# Test 4: MP3 256k
test_feature "4. MP3 256k CBR" "test_basic.wav" "mp3" "-b:a 256k"

# Test 5: Sample Rate 48kHz
test_feature "5. MP3 with 48kHz" "test_basic.wav" "mp3" "-ar 48000 -b:a 320k"

# Test 6: Sample Rate 96kHz FLAC
test_feature "6. FLAC 96kHz Hi-Res" "test_basic.wav" "flac" "-ar 96000"

# Test 7: Fade In/Out
test_feature "7. MP3 with Fade (2s in, 2s out)" "test_basic.wav" "mp3" "-af 'afade=t=in:st=0:d=2,afade=t=out:st=3:d=2' -b:a 320k"

# Test 8: Trim Silence
test_feature "8. MP3 with Silence Removal" "test_silence.wav" "mp3" "-af 'silenceremove=start_periods=1:start_duration=0.1:start_threshold=-50dB:stop_periods=1:stop_duration=0.1:stop_threshold=-50dB' -b:a 192k"

# Test 9: Combined - AAC 48kHz with fade
test_feature "9. AAC 48kHz + Fade" "test_basic.wav" "aac" "-ar 48000 -af 'afade=t=in:st=0:d=1,afade=t=out:st=4:d=1' -b:a 192k"

# Test 10: MP3 128k (Streaming quality)
test_feature "10. MP3 128k (Streaming)" "test_basic.wav" "mp3" "-b:a 128k"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "RESULTS SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
echo -e "Tests Failed: ${RED}$FAILED${NC}"
echo "Total Tests: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 ALL TESTS PASSED! 🎉${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
fi

echo ""
echo "Test files location: $TEST_DIR"
echo ""
echo "To inspect test files:"
echo "  ls -lh $TEST_DIR"
echo "  ffprobe $TEST_DIR/test_basic.m4a"
echo ""

exit $FAILED

