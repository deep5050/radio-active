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
- [x] Favorite stations (Aliasing)
- [ ] Supports user-added stations
- [ ] Finds nearby stations

### External Dependency 

It needs [FFmpeg](https://ffmpeg.org/download.html) to be installed on your system in order to play the audio

on Ubuntu based system >= 20.04 Run

``` 
sudo apt update
sudo apt install ffmpeg
```

For other systems including windows see the above link

### Install

``` bash
git clone https://github.com/deep5050/radio-active.git && cd radio-active

pip install -r requirements
```

####  Unix/Linux

you can add the path to the ENV and execute it from any where (optional)

``` bash
echo "alias radio-active='python3 $PWD/radio-active'" >> ~/.bashrc

source ~/.bashrc
```

### Other (Windows , Mac)

Add this directory to your ENV path manually

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

> `--station` : Expects a station name to be played ( if not provided it will try to get the last played station ). Example: "pehla nasha" , pehla_nasha, bbc_radio 

> `--uuid` : When station names are too long or confusing ( or multiple results for the same name )  use the station's uuid to play . --uuid gets the greater priority than --station. example: 96444e20-0601-11e8-ae97-52543be04c81

> `--log-level` : don't need to specify unless you are developing it. [ `info` , `warning` , `error` , `debug` ]

### Extra

You  can always alias your favorite stations' name with a custom name. radio-active firsts looks for stations in your favorite list.

To add a station to your favorite station list:

1. place a file named `radio-active-alias.txt` under your home directory.

2. Write a new line with pattern like `name`=`uuid`. Example:
 ```
 mirchi_ranbindra_sangeet=72e039a6-9ed9-4741-b45e-165eec3bec6d
 bongo_net=96444e20-0601-11e8-ae97-52543be04c81
 ````
### Acknowledgements

<div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>

<div align=center>
<img src=images/footer.png>
<p align=center> Happy Listening </p>
</div>
