## 2.5.1

1. Fixed RuntimeError with empty selection menu on no options provided to radio.
2. Display the current station name as a panel while starting the radio with `--uuid`
3. Minor typos were fixed in the help message.
4. Station names do not contain any unnecessary spaces now
5. Do not play any stations while `--flush` is given. Just delete the list and exit.

## 2.5.0

1. Added a selection menu while no station information is provided. This will include the last played station and the favorite list.
2. Added `--volume` option to the player. Now you can pass the volume level to the player.
3. `ffplay` initialization errors handled. Better logic to stop the PID of `ffplay`
4. Some unhandled errors are now handled
5. Minor typos fixed
6. `sentry-sdk` added to gater errors (will be removed on next major release)
7. About section updated to show donation link
8. The upgrade message will now point to this changelog file
9. Updated documentation

## 2.4.0

1. Crashes on Windows fixed
Fixed setup-related issues (development purpose)

## 2.3.0

1. Discover stations by country 
2. Discover stations by state
3. Discover stations by genre/tags
4. Discover stations by language
5. More info on multiple results for a station name
6. Shows currently playing radio info as box
7. sentry-SDK removed
8. Help table improved
9. Other minor bugs fixed

## 2.2.0

1. Pretty Print welcome message using Rich
2. More user-friendly and gorgeous
3. Added several new options `-F`,`-W`,`-A`,`--flush`
4. Fixed unhandled Exception when trying to quit within 3 seconds
5. Supports User-Added stations
6. Alias file now supports both UUID and URL entry
7. Fixed bugs in playing last station (which is actually an alias under fav list)
8. New Table formatted help message
9. Notification for new app version
10. Several typos fixed
11. Asciinema demo added
12. README formatted
13. Pylint the codebase
14. Added support section
15. python imports Sorted
16. Alias pattern updated from `=` to `==`
17. Many more

## 2.1.3

1. Fixed bugs in the last station
2. Typos fixed
3. Formatted codebase
4. Logging issued fixed
5. Sentry Added to collect unhandled Exceptions logs only


## 2.1.2

1. Updated README and project details
2. Fixed minor bugs

## 2.1.1

1. Minor bugs fixed
2. Station aliasing support

## 2.1.0

1. Minor bugs quashed

## 2.0.4

1. Initial release
