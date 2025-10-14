#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 UNIVERSAL AUDIO CONVERTER - COMPREHENSIVE TESTING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TEST_DIR="/tmp/universal_converter_tests"
mkdir -p $TEST_DIR
cd $TEST_DIR

PASSED=0
FAILED=0

# Generate test audio file (base WAV)
generate_base_wav() {
    echo -e "${YELLOW}📝 Generating base WAV file (440Hz, 5s)...${NC}"
    ffmpeg -y -f lavfi -i "sine=frequency=440:duration=5" \
        -ar 44100 -ac 2 -acodec pcm_s16le \
        "test_base.wav" 2>/dev/null
    
    if [ -f "test_base.wav" ]; then
        echo -e "${GREEN}✓ Base WAV created ($(du -h test_base.wav | cut -f1))${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to create base WAV${NC}"
        return 1
    fi
}

# Convert base to different formats
convert_to_format() {
    local format=$1
    local extra_params=$2
    local output="test_input.$format"
    
    echo -e "${YELLOW}📝 Creating $format test file...${NC}"
    
    case $format in
        mp3)
            ffmpeg -y -i test_base.wav -c:a libmp3lame -b:a 192k "$output" 2>/dev/null
            ;;
        m4a)
            ffmpeg -y -i test_base.wav -c:a aac -b:a 192k "$output" 2>/dev/null
            ;;
        flac)
            ffmpeg -y -i test_base.wav -c:a flac "$output" 2>/dev/null
            ;;
        ogg)
            ffmpeg -y -i test_base.wav -c:a libvorbis -q:a 6 "$output" 2>/dev/null
            ;;
        wma)
            ffmpeg -y -i test_base.wav -c:a wmav2 -b:a 192k "$output" 2>/dev/null
            ;;
        aiff)
            ffmpeg -y -i test_base.wav -c:a pcm_s16be "$output" 2>/dev/null
            ;;
        *)
            echo -e "${RED}✗ Unknown format: $format${NC}"
            return 1
            ;;
    esac
    
    if [ -f "$output" ]; then
        local size=$(du -h "$output" | cut -f1)
        echo -e "${GREEN}✓ Created $output ($size)${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to create $format${NC}"
        return 1
    fi
}

# Test format detection
test_format_detection() {
    local input_file=$1
    local expected_codec=$2
    
    echo ""
    echo -e "${BLUE}Testing format detection: $input_file${NC}"
    
    # Run ffprobe
    local codec=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$input_file" 2>/dev/null)
    local bitrate=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "$input_file" 2>/dev/null)
    local sample_rate=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=sample_rate -of default=noprint_wrappers=1:nokey=1 "$input_file" 2>/dev/null)
    
    echo "  Codec: $codec"
    if [ ! -z "$bitrate" ] && [ "$bitrate" != "N/A" ]; then
        echo "  Bitrate: $((bitrate / 1000)) kbps"
    fi
    echo "  Sample Rate: $sample_rate Hz"
    
    if [ "$codec" == "$expected_codec" ]; then
        echo -e "  ${GREEN}✓ PASS - Codec detected correctly${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "  ${RED}✗ FAIL - Expected $expected_codec, got $codec${NC}"
        ((FAILED++))
        return 1
    fi
}

# Test conversion to WAV
test_conversion_to_wav() {
    local input_file=$1
    local output_wav="converted_${input_file%.*}.wav"
    
    echo ""
    echo -e "${BLUE}Testing conversion: $input_file → WAV${NC}"
    
    ffmpeg -y -i "$input_file" -acodec pcm_s16le -ar 44100 -ac 2 "$output_wav" 2>/dev/null
    
    if [ -f "$output_wav" ]; then
        local size=$(du -h "$output_wav" | cut -f1)
        local duration=$(ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$output_wav" 2>/dev/null | cut -d. -f1)
        
        echo "  Output: $output_wav ($size)"
        echo "  Duration: ${duration}s"
        echo -e "  ${GREEN}✓ PASS - Conversion successful${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "  ${RED}✗ FAIL - Conversion failed${NC}"
        ((FAILED++))
        return 1
    fi
}

# Test end-to-end: Input → Process → Output
test_end_to_end() {
    local input_format=$1
    local output_format=$2
    local input_file="test_input.$input_format"
    local output_file="test_output.$output_format"
    
    echo ""
    echo -e "${BLUE}Testing E2E: $input_format → $output_format${NC}"
    
    # Step 1: Convert to WAV
    local temp_wav="temp_${input_file%.*}.wav"
    ffmpeg -y -i "$input_file" -acodec pcm_s16le -ar 44100 "$temp_wav" 2>/dev/null
    
    # Step 2: Process (simulate LUFS normalization)
    if [ "$output_format" == "mp3" ]; then
        ffmpeg -y -i "$temp_wav" -c:a libmp3lame -b:a 320k "$output_file" 2>/dev/null
    elif [ "$output_format" == "m4a" ]; then
        ffmpeg -y -i "$temp_wav" -c:a aac -b:a 256k "$output_file" 2>/dev/null
    elif [ "$output_format" == "flac" ]; then
        ffmpeg -y -i "$temp_wav" -c:a flac "$output_file" 2>/dev/null
    else
        ffmpeg -y -i "$temp_wav" "$output_file" 2>/dev/null
    fi
    
    if [ -f "$output_file" ]; then
        local size=$(du -h "$output_file" | cut -f1)
        echo "  Result: $output_file ($size)"
        echo -e "  ${GREEN}✓ PASS - E2E successful${NC}"
        ((PASSED++))
        rm -f "$temp_wav"
        return 0
    else
        echo -e "  ${RED}✗ FAIL - E2E failed${NC}"
        ((FAILED++))
        rm -f "$temp_wav"
        return 1
    fi
}

# ============================================
# MAIN TEST SEQUENCE
# ============================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Generate Test Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

generate_base_wav

convert_to_format "mp3"
convert_to_format "m4a"
convert_to_format "flac"
convert_to_format "ogg"
# convert_to_format "wma"  # May not be available on all systems
convert_to_format "aiff"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Test Format Detection (ffprobe)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_format_detection "test_base.wav" "pcm_s16le"
test_format_detection "test_input.mp3" "mp3"
test_format_detection "test_input.m4a" "aac"
test_format_detection "test_input.flac" "flac"
test_format_detection "test_input.ogg" "vorbis"
test_format_detection "test_input.aiff" "pcm_s16be"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Test Conversion to WAV"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_conversion_to_wav "test_input.mp3"
test_conversion_to_wav "test_input.m4a"
test_conversion_to_wav "test_input.flac"
test_conversion_to_wav "test_input.ogg"
test_conversion_to_wav "test_input.aiff"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Test End-to-End Conversions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test popular conversion scenarios
test_end_to_end "mp3" "mp3"    # Lossy → Lossy (warning)
test_end_to_end "mp3" "flac"   # Lossy → Lossless (no improvement)
test_end_to_end "flac" "mp3"   # Lossless → Lossy (quality loss)
test_end_to_end "flac" "flac"  # Lossless → Lossless (OK!)
test_end_to_end "m4a" "mp3"    # M4A → MP3 (your case!)
test_end_to_end "m4a" "m4a"    # M4A → M4A (reencoding)

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
echo "Test files location: $TEST_DIR"
echo "Files created:"
ls -lh $TEST_DIR | grep -E "\.mp3|\.m4a|\.flac|\.ogg|\.wav|\.aiff"
echo ""

exit $FAILED

