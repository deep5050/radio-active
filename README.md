<div align=center>
<p align=center><img src=images/logo.png width=250px></p>
<h1 align=center> RADIO-ACTIVE </h1>
<p align=center> Play any radios around the globe right from your terminal </p>

<p align=center>
<img align=center src=images/example.png >
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
- [x] Supports user-added stations
- [x] Looks minimal and user-friendly
- [x] Runs on Raspberry-Pi
- [x] Finds nearby stations
- [x] Discovers stations by genre
- [x] Discovers statations by language
- [ ] I'm feeling lucky ! Play Random stations
- [ ] No external dependencies!

> See my progress [here](https://github.com/deep5050/radio-active/projects/1)


### External Dependency

It needs [FFmpeg](https://ffmpeg.org/download.html) to be installed on your
system in order to play the audio

on Ubuntu based system >= 20.04 Run

```
sudo apt update
sudo apt install ffmpeg
```

For other systems including windows see the above link

#### Installing FFmpeg

FFmpeg is required for this program to work correctly. Install FFmpeg by following these steps :-

- On Linux - <https://www.tecmint.com/install-ffmpeg-in-linux/>
- On Windows - <https://www.wikihow.com/Install-FFmpeg-on-Windows>


### Install

Just run: `pip3 install --upgrade radio-active`

I encourage you to install with pipx: `pipx install radio-active`

### Run

Run with `radioactive --station [STATION_NAME]` or as simply `radio -U [UUID] ` :zap:


<!-- ### Note !!

This uses [sentry](https://sentry.io) to collect un-handled exceptions only (As it is under heavy development). Next mojor release will remove this.
Make sure you are okay with this ⚠️ -->

### Demo


<a align=center href="https://asciinema.org/a/412285" target="_blank"><img src="https://asciinema.org/a/412285.svg" /></a>



### Options


| Argument                     | Note                                 | Description                                  | Default |
| ---------------------------- | ------------------------------------ | -------------------------------------------- | ------- |
| `--station`, `-S`            | Required ( Optional from second run) | Station name                                 | None    |
| `--uuid`, `-U`               | Optional                             | ID of the station                            | None    |
| `--log-level`, `-L`          | Optional                             | Log level of the program                     | info    |
| `--add-station` , `-A`       | Optional                             | Add an entry to fav list                     | False   |
| `--show-favourite-list`,`-W` | Optional                             | Show fav list                                | False   |
| `--add-to-favourite`,`-F`    | Optional                             | Add current station to fav list              | False   |
| `--flush`                    | Optional                             | Remove all the entries from fav list         | False   |
| `--discover-by-country`,`-D` | Optional                             | Discover stations by country code            | false   |
| `--discover-by-state`        | Optioanl                             | Discover stations by country state           | false   |
| `--discover-by-tag`          | Optional                             | Discover stations by tags/genre              | fasle   |
| `--discover-by-language`     | optional                             | Discover stations by                         | false   |
| `--limit`                    | Optional                             | Limit the # of results in the discover table | 100     |


<hr>


> `--station`, `-S` : Expects a station name to be played (if not provided it
> will try to get the last played station). Example: "pehla nasha" ,
> pehla_nasha, bbc_radio

> `--uuid`,`-U` : When station names are too long or confusing (or multiple
> results for the same name) use the station's uuid to play . --uuid gets the
> greater priority than --station. Example: 96444e20-0601-11e8-ae97-52543be04c81

> `--log-level`, `-L` : don't need to specify unless you are developing it. `info` , `warning` , `error` , `debug` 

> `-F` : Add current station to your favorite list. Example: `-F my_fav_1`

> `-A`: Add any stations to your list. You can add stations that are not currently available on our API. When adding a new station enter a name and direct URL to the audio stream. 


### Changes

see [CHANGELOG](./CHANGELOG.md)

### Community

Share you favorite list with our community 🌐 ➡️ [Here](https://github.com/deep5050/radio-active/discussions/10)

> Your favorite list `.radio-active-alias` is under your home directory as a hidden file :)

### Extra

If you ever face a situation where radio-active quits but the audio (ffplay) runs in the background. Kill the process ID (PID) of ffplay. Run `ps -al` get the PID of ffplay and `kill [PID]`. I know you Know that :)


### Support
<p align=center><a href="https://www.buymeacoffee.com/deep5050" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 117px !important;" ></a></p>

### Acknowledgements

<div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>

<div align=center>
<img src=images/footer.png>
<p align=center> Happy Listening </p>
<img src=https://forthebadge.com/images/badges/built-with-love.svg>

<p align=center ><img align=center src=https://static.pepy.tech/personalized-badge/radio-active?period=total&units=international_system&left_color=black&right_color=green&left_text=TotalInstalls></p>
  
</div>

