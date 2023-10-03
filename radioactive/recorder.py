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

        codec_info = subprocess.check_output(ffprobe_command, text=True)

        # Determine the file extension based on the audio codec
        audio_codec = codec_info.strip()
        audio_codec = audio_codec.split("\n")[0]
        return audio_codec

    except subprocess.CalledProcessError as e:
        log.error(f"Error: could not fetch codec {e}")
        return None


def record_audio_from_url(input_url, output_file, force_mp3, loglevel):
    try:
        # Construct the FFmpeg command
        ffmpeg_command = [
            "ffmpeg",
            "-i",
            input_url,  # input URL
            "-vn",  # disable video recording
            "-stats",  # show stats
        ]

        # codec for audio stream
        ffmpeg_command.append("-c:a")
        if force_mp3:
            ffmpeg_command.append("libmp3lame")
            log.debug("Record: force libmp3lame")
        else:
            # file will be saved as as provided. this is more error prone
            # file extension must match the actual stream codec
            ffmpeg_command.append("copy")

        ffmpeg_command.append("-loglevel")
        if loglevel == "debug":
            ffmpeg_command.append("info")
        else:
            ffmpeg_command.append("error"),
            ffmpeg_command.append("-hide_banner")

        # output file
        ffmpeg_command.append(output_file)

        # Run FFmpeg command on foreground to catch 'q' without
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
