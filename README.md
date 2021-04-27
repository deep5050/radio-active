# RADIO-ACTIVE

Play any radios around the globe right from your terminal


## Example

```bash
(.venv) deep@lubuntu:~/Desktop/radio-active$ python radio-active 
     [!]    | No station information provided, trying to get the last station information
      i     | Station found: Radio Mirchi - 90s Hit Songs
      i     | Radio started successfully


```

### Note 

It needs [FFmpeg](https://ffmpeg.org/download.html) to be installed on your system in order to play the audio

on Ubuntu based system > 20.04 Run

```
sudo apt update
sudo apt install ffmpeg
```
For other systems including windows see the above link
### Install
```
git clone https://github.com/deep5050/radio-active.git && cd radio-active

pip install -r requirements
```
Run with `python radio-active --station [STATION_NAME]`

### Options

```
usage: radio-active [-h] [--version] [--station STATION_NAME] [--uuid STATION_UUID] [--log-level LOG_LEVEL]

Play any radios around the globe right from the Terminal!

optional arguments:
  -h, --help              Show this help message and exit
  --version               Show program's version number and exit
  --station STATION_NAME  Specify a station name
  --uuid STATION_UUID     Specify a station UUID
  --log-level LOG_LEVEL   Specify log level
```