import subprocess

from zenlog import log


def record_audio_from_url(input_url, output_file, codec="mp3"):
    try:
        # Construct the FFmpeg command
        ffmpeg_command = [
            "ffmpeg",
            "-i",
            input_url,  # Input URL
            "-c:a",
            "copy",  # Codec (copy) audio
            "-vn",  # Disable video recording
            # "-n",  # no overwrite file, possible on foreground only
            "-loglevel",
            "error",  # stop showing build and metadata info
            "-hide_banner",
            "-stats",  # show stats
            output_file,  # Output file path
        ]

        # Run FFmpeg command on frouground to catch 'q' without
        # any complex thread for now
        subprocess.run(ffmpeg_command, check=True)

        log.debug("Record: {}".format(str(ffmpeg_command)))
        log.info(f"Audio recorded successfully.")

    except subprocess.CalledProcessError as e:
        log.debug("Error: {}".format(e))
        log.error(f"Error while recording audio: {e}")
    except Exception as ex:
        log.debug("Error: {}".format(ex))
        log.error(f"An error occurred: {ex}")
