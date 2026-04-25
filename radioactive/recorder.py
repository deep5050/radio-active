import subprocess

from zenlog import log


def record_audio_auto_codec(input_stream_url):
    try:
        # Run FFprobe to get the audio codec information
        ffprobe_command = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            input_stream_url,
        ]

        codec_info = subprocess.check_output(ffprobe_command, text=True, timeout=10)

        # Determine the file extension based on the audio codec
        audio_codec = codec_info.strip()
        audio_codec = audio_codec.split("\n")[0]
        return audio_codec

    except FileNotFoundError:
        log.error("ffprobe not found! Please install FFmpeg/ffprobe to use the recording feature.")
        return None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        log.error(f"Error: could not fetch codec {e}")
        return None


def record_audio_from_url(input_url, output_file, force_mp3, loglevel, duration=None):
    """
    Record audio from a URL using FFmpeg.
    Returns the subprocess.Popen object to allow UI tracking.
    """
    log.debug(f"Recording audio from {input_url} to {output_file}")
    try:
        ffmpeg_command = [
            "ffmpeg",
            "-i",
            input_url,
            "-vn",
            "-stats",
        ]

        ffmpeg_command.append("-c:a")
        if force_mp3:
            ffmpeg_command.append("libmp3lame")
        else:
            ffmpeg_command.append("copy")

        ffmpeg_command.append("-loglevel")
        if loglevel == "debug":
            ffmpeg_command.append("info")
        else:
            ffmpeg_command.append("error")
            ffmpeg_command.append("-hide_banner")

        if duration:
            seconds = int(duration) * 60
            ffmpeg_command.append("-t")
            ffmpeg_command.append(str(seconds))

        ffmpeg_command.append(output_file)

        # Run FFmpeg command in background to allow UI tracking
        # Use DEVNULL to prevent hangs and terminal corruption
        process = subprocess.Popen(
            ffmpeg_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return process

    except FileNotFoundError:
        log.error(
            "FFmpeg not found! Please install FFmpeg to use the recording feature."
        )
        return None
    except Exception as ex:
        log.debug("Error: {}".format(ex))
        log.error(f"Error while starting recording: {ex}")
        return None
