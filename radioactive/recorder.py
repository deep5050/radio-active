import subprocess

from zenlog import log


def record_audio_auto_codec(input_stream_url):
    try:
        ffprobe_command = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_name",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_stream_url,
        ]
        codec_info = subprocess.check_output(ffprobe_command, text=True)
        audio_codec = codec_info.strip().split("\n", 1)[0]
        return audio_codec

    except subprocess.CalledProcessError as e:
        log.error(f"Error: could not fetch codec {e}")
        return None


def record_audio_from_url(input_url, output_file, force_mp3, loglevel):
    try:
        # Construct the FFmpeg command parts
        base_command = ["ffmpeg", "-i", input_url, "-vn", "-stats"]
        codec_command = ["-c:a", "libmp3lame" if force_mp3 else "copy"]
        loglevel_command = (["-loglevel", "info"]
                            if loglevel == "debug"
                            else ["-loglevel", "error", "-hide_banner"])

        # Concatenate commands in one go
        ffmpeg_command = base_command + codec_command + loglevel_command + [output_file]

        subprocess.run(ffmpeg_command, check=True)

        log.debug("Record: {}".format(ffmpeg_command))
        log.info("Audio recorded successfully.")

    except subprocess.CalledProcessError as e:
        log.debug("Error: {}".format(e))
        log.error(f"Error while recording audio: {e}")
    except Exception as ex:
        log.debug("Error: {}".format(ex))
        log.error(f"An error occurred: {ex}")
