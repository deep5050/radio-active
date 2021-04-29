<div align=center>
<p align=center><img src=images/logo.png width=250px></p>
<h1 align=center> RADIO-ACTIVE </h1>
<p align=center> Play any radios around the globe right from your terminal </p>

<p align=center>
<img align=center src=images/banner.png >
<hr>
<img alt="GitHub" src="https://img.shields.io/github/license/deep5050/radio-active?style=for-the-badge">
<img alt="PyPI" src="https://img.shields.io/pypi/v/radio-active?style=for-the-badge">
<img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/radio-active?style=for-the-badge">
<img alt="CodeFactor Grade" src="https://img.shields.io/codefactor/grade/github/deep5050/radio-active/main?style=for-the-badge">

</p>
</div>

### Features

- [x] Supports more than 30K stations !!
- [x] Saves last station information
- [x] Favorite stations (Aliasing)
- [ ] Supports user-added stations
- [ ] Finds nearby stations

### External Dependency

It needs [FFmpeg](https://ffmpeg.org/download.html) to be installed on your
system in order to play the audio

on Ubuntu based system >= 20.04 Run

```
sudo apt update
sudo apt install ffmpeg
```

For other systems including windows see the above link

### Install

Just run: `pip3 install radio-active`

### Run

Run with `radioactive --station [STATION_NAME]`

### Options

```bash
deep@lubuntu:~/Desktop$ radioactive --help
usage: radio-active [-h] [--version] [--station STATION_NAME] [--uuid STATION_UUID]
                    [--log-level LOG_LEVEL]

Play any radio around the globe right from the CLI

optional arguments:
  -h, --help            show this help message and exit
  --version, -V
  --station STATION_NAME, -S STATION_NAME
                        Specify a station name
  --uuid STATION_UUID, -U STATION_UUID
                        Specify a station UUID
  --log-level LOG_LEVEL, -L LOG_LEVEL
                        Specify log level

```

> `--station`, `-S` : Expects a station name to be played ( if not provided it
> will try to get the last played station ). Example: "pehla nasha" ,
> pehla_nasha, bbc_radio

> `--uuid`,`-U` : When station names are too long or confusing ( or multiple
> results for the same name ) use the station's uuid to play . --uuid gets the
> greater priority than --station. example: 96444e20-0601-11e8-ae97-52543be04c81

> `--log-level`, `-L` : don't need to specify unless you are developing it. [ >
> > `info` , `warning` , `error` , `debug` ]

### Extra

You can always alias your favorite stations' name with a custom name.
radio-active firsts looks for stations in your favorite list.

To add a station to your favorite station list:

1. place a file named `radio-active-alias.txt` under your home directory.

2. Write a new line with pattern like `name`=`uuid`. Example:

```
mirchi_ranbindra_sangeet=72e039a6-9ed9-4741-b45e-165eec3bec6d
bongo_net=96444e20-0601-11e8-ae97-52543be04c81
```

### Acknowledgements

<div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>

<div align=center>
<img src=images/footer.png>
<p align=center> Happy Listening </p>
<img src=https://forthebadge.com/images/badges/built-with-love.svg>
</div>
