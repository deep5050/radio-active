<div align=center>
<p align=center><img src=images/logo.png width=250px></p>
<h1 align=center> RADIO-ACTIVE </h1>
<p align=center> Play any radios around the globe right from your terminal </p>


<img align=center src=images/example_1.png >

<hr>
</div>

### Features 
- [x] Supports more than 30K stations !!
- [x] Saves last station information 
- [ ] Supports user-added stations


### External Dependency 

It needs [FFmpeg](https://ffmpeg.org/download.html) to be installed on your system in order to play the audio

on Ubuntu based system > 20.04 Run

``` 

sudo apt update
sudo apt install ffmpeg
```

For other systems including windows see the above link

### Install

Run: `bash install.sh`

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

### Acknowledegements

<div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>

<div align=center>
<img src=images/footer.png>
<p align=center> Happy Listening </p>
</div>
