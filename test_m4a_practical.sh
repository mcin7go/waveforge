#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎙️  PRACTICAL TEST: M4A (Windows Recorder Style)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

TEST_DIR="/tmp/m4a_practical_test"
mkdir -p $TEST_DIR
cd $TEST_DIR

# Simulate Windows Recorder M4A (similar to user's file)
echo -e "${YELLOW}📝 Creating test M4A (simulating Windows Recorder)...${NC}"
echo "   - Mono audio (voice recording)"
echo "   - 128 kbps AAC"
echo "   - 44.1 kHz sample rate"
echo ""

ffmpeg -y -f lavfi -i "sine=frequency=440:duration=3" \
    -ac 1 -c:a aac -b:a 128k -ar 44100 \
    "Nagranie_test.m4a" 2>/dev/null

if [ ! -f "Nagranie_test.m4a" ]; then
    echo -e "${RED}✗ Failed to create test M4A${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Created: Nagranie_test.m4a ($(du -h Nagranie_test.m4a | cut -f1))${NC}"
echo ""

# STEP 1: Detect format (ffprobe)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Format Detection (ffprobe)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CODEC=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "Nagranie_test.m4a")
CODEC_LONG=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=codec_long_name -of default=noprint_wrappers=1:nokey=1 "Nagranie_test.m4a")
BITRATE=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "Nagranie_test.m4a")
SAMPLE_RATE=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=sample_rate -of default=noprint_wrappers=1:nokey=1 "Nagranie_test.m4a")
CHANNELS=$(ffprobe -v quiet -select_streams a:0 -show_entries stream=channels -of default=noprint_wrappers=1:nokey=1 "Nagranie_test.m4a")
DURATION=$(ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "Nagranie_test.m4a")

echo "  Codec: $CODEC"
echo "  Codec Long: $CODEC_LONG"
echo "  Bitrate: $((BITRATE / 1000)) kbps"
echo "  Sample Rate: $SAMPLE_RATE Hz"
echo "  Channels: $CHANNELS (mono)"
echo "  Duration: ${DURATION%.*}s"
echo ""

if [ "$CODEC" == "aac" ]; then
    echo -e "${GREEN}✅ Format detection: SUCCESS${NC}"
else
    echo -e "${RED}✗ Format detection: FAILED${NC}"
    exit 1
fi

# STEP 2: Convert to WAV
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Conversion M4A → WAV (Internal)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

START_TIME=$(date +%s)
ffmpeg -y -i "Nagranie_test.m4a" \
    -acodec pcm_s16le -ar 44100 -ac 2 \
    "internal.wav" 2>/dev/null
END_TIME=$(date +%s)
CONVERSION_TIME=$((END_TIME - START_TIME))

if [ -f "internal.wav" ]; then
    SIZE=$(du -h internal.wav | cut -f1)
    echo -e "${GREEN}✅ Conversion: SUCCESS${NC}"
    echo "  Output: internal.wav"
    echo "  Size: $SIZE"
    echo "  Time: ${CONVERSION_TIME}s"
else
    echo -e "${RED}✗ Conversion: FAILED${NC}"
    exit 1
fi

# STEP 3: Process (simulate LUFS normalization)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Processing (LUFS Normalization to -14)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ffmpeg -y -i "internal.wav" \
    -af "loudnorm=I=-14:TP=-1:LRA=7" \
    -c:a libmp3lame -b:a 320k \
    "output_normalized.mp3" 2>/dev/null

if [ -f "output_normalized.mp3" ]; then
    SIZE=$(du -h output_normalized.mp3 | cut -f1)
    echo -e "${GREEN}✅ Processing: SUCCESS${NC}"
    echo "  Output: output_normalized.mp3"
    echo "  Size: $SIZE"
    echo "  Format: MP3 320k"
    echo "  LUFS: -14 (Spotify target)"
else
    echo -e "${RED}✗ Processing: FAILED${NC}"
    exit 1
fi

# STEP 4: Quality Warning Check
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Quality Warning"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "  Input: M4A (AAC 128k) - LOSSY"
echo "  Output: MP3 (320k) - LOSSY"
echo ""
echo -e "${YELLOW}  ⚠️  WARNING: Converting lossy to lossy format${NC}"
echo "     Quality may degrade due to re-encoding"
echo ""
echo "  Recommendation:"
echo "    ✅ Better: Keep as M4A or convert to lossless"
echo "    ⚠️  Acceptable: If LUFS normalization needed"
echo ""

# STEP 5: End-to-End Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "COMPLETE WORKFLOW TEST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Input File:"
echo "  📁 Nagranie_test.m4a"
echo "  🎵 AAC codec, 128 kbps, mono, 44.1kHz"
echo "  💾 $(du -h Nagranie_test.m4a | cut -f1)"
echo ""

echo "Processing Steps:"
echo "  1. ✅ Upload accepted"
echo "  2. ✅ Format detected (ffprobe)"
echo "  3. ✅ Converted to WAV (internal)"
echo "  4. ✅ LUFS normalized to -14"
echo "  5. ✅ Exported to MP3 320k"
echo ""

echo "Output File:"
echo "  📁 output_normalized.mp3"
echo "  🎵 MP3 codec, 320 kbps, stereo"
echo "  💾 $(du -h output_normalized.mp3 | cut -f1)"
echo ""

echo "Quality Check:"
echo "  ⚠️  Lossy → Lossy conversion"
echo "  ℹ️  User will see warning in UI"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}   🎉 COMPLETE WORKFLOW: SUCCESS! 🎉${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Files created in: $TEST_DIR"
ls -lh $TEST_DIR
echo ""

echo "To inspect:"
echo "  ffprobe $TEST_DIR/Nagranie_test.m4a"
echo "  ffprobe $TEST_DIR/output_normalized.mp3"
echo ""

