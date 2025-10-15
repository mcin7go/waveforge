"""
Audio file generator for testing.
Uses FFmpeg to create real audio files in various formats.
"""
import subprocess
import tempfile
import os
import json


def generate_test_audio(format_name, duration=2, frequency=440, sample_rate=44100, channels=2):
    """
    Generate test audio file with sine wave using FFmpeg.
    
    Args:
        format_name: Audio format ('wav', 'mp3', 'flac', 'aac', 'm4a', 'ogg', 'opus', 'aiff', 'wma')
        duration: Length in seconds (default: 2)
        frequency: Tone frequency in Hz (default: 440 = A4)
        sample_rate: Sample rate in Hz (default: 44100)
        channels: Number of channels (default: 2 = stereo)
    
    Returns:
        str: Path to generated audio file
    
    Raises:
        RuntimeError: If FFmpeg command fails
    """
    # Create temp file with proper extension
    temp_file = tempfile.NamedTemporaryFile(suffix=f'.{format_name}', delete=False)
    output_path = temp_file.name
    temp_file.close()
    
    # Base FFmpeg command - generate sine wave
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', f'sine=frequency={frequency}:duration={duration}:sample_rate={sample_rate}',
        '-ac', str(channels),
    ]
    
    # Format-specific encoding parameters
    if format_name == 'wav':
        cmd.extend(['-codec:a', 'pcm_s16le'])
    
    elif format_name == 'mp3':
        cmd.extend(['-codec:a', 'libmp3lame', '-b:a', '320k'])
    
    elif format_name == 'flac':
        cmd.extend(['-codec:a', 'flac', '-compression_level', '5'])
    
    elif format_name in ['aac', 'm4a']:
        cmd.extend(['-codec:a', 'aac', '-b:a', '256k'])
        # M4A is AAC in MP4 container, FFmpeg handles this automatically by extension
    
    elif format_name == 'ogg':
        cmd.extend(['-codec:a', 'libvorbis', '-q:a', '5'])
    
    elif format_name == 'opus':
        cmd.extend(['-codec:a', 'libopus', '-b:a', '128k'])
        # OPUS prefers 48kHz
        cmd.extend(['-ar', '48000'])
    
    elif format_name == 'wma':
        cmd.extend(['-codec:a', 'wmav2', '-b:a', '192k'])
    
    elif format_name == 'aiff':
        cmd.extend(['-codec:a', 'pcm_s16be'])  # Big-endian for AIFF
    
    else:
        raise ValueError(f"Unsupported format: {format_name}")
    
    cmd.append(output_path)
    
    # Run FFmpeg
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        # Cleanup on error
        if os.path.exists(output_path):
            os.remove(output_path)
        raise RuntimeError(
            f"FFmpeg failed to generate {format_name} file.\n"
            f"Command: {' '.join(cmd)}\n"
            f"Error: {result.stderr}"
        )
    
    return output_path


def verify_audio_format(filepath, expected_format):
    """
    Verify audio file format using FFprobe.
    
    Args:
        filepath: Path to audio file
        expected_format: Expected format name ('mp3', 'flac', etc.)
    
    Returns:
        dict: Format information from FFprobe
    
    Raises:
        RuntimeError: If FFprobe fails or format doesn't match
    """
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        filepath
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"FFprobe failed: {result.stderr}")
    
    try:
        info = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse FFprobe output: {e}")
    
    if 'streams' not in info or len(info['streams']) == 0:
        raise RuntimeError(f"No audio streams found in {filepath}")
    
    stream = info['streams'][0]
    format_info = info.get('format', {})
    
    codec_name = stream.get('codec_name', '').lower()
    format_name = format_info.get('format_name', '').lower()
    
    # Format validation
    format_map = {
        'wav': ['wav'],
        'mp3': ['mp3'],
        'flac': ['flac'],
        'aac': ['aac', 'mov,mp4,m4a,3gp,3g2,mj2'],  # AAC can be in various containers
        'm4a': ['mov,mp4,m4a,3gp,3g2,mj2'],
        'ogg': ['ogg'],
        'opus': ['ogg', 'opus'],  # OPUS usually in OGG container
        'wma': ['asf'],
        'aiff': ['aiff'],
    }
    
    expected_formats = format_map.get(expected_format, [expected_format])
    format_matches = any(ef in format_name for ef in expected_formats)
    
    if not format_matches:
        raise RuntimeError(
            f"Format mismatch: expected {expected_format}, "
            f"got format_name='{format_name}', codec='{codec_name}'"
        )
    
    return {
        'codec': codec_name,
        'format': format_name,
        'sample_rate': int(stream.get('sample_rate', 0)),
        'channels': stream.get('channels', 0),
        'bitrate': int(stream.get('bit_rate', 0)) if stream.get('bit_rate') else None,
        'duration': float(format_info.get('duration', 0)),
    }


def cleanup_test_audio(*filepaths):
    """
    Clean up test audio files.
    
    Args:
        *filepaths: One or more file paths to delete
    """
    for filepath in filepaths:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass  # Ignore errors during cleanup

