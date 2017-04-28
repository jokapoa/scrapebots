# Change Log
All notable changes to this project will be documented in this file.

## 0.1.3 - 2017-04-27

### Added
- statistik races list fetcher (async via tor)
- statistik races details fetcher (async via tor)

### Fixed
- statistik races list fetcher pages url
- statistik races details fetcher folders path

### Removed
- time profiling utils

## 0.1.2 - 2017-04-27

### Tested
- conne marathon bot (it works)

### Added
- conne marathon bot (raw version => -0.1)
- time utils

## 0.1.1 - 2017-04-26

### Added
- nyc marathon bot

### Tested
- nyc marathon bot (it works)

### Fixed
- nyc marathon bot: go_to_next_page_of_archive

## 0.1 - 2017-04-25

### Tested
- async workers for london marathon

### Refactored
- utils for london marathon

### Added
- FSG media downloader
- london marathon bot: AthletePerformance.to_csv() includes url field
- london marathon bot utils: percentage in ETA time

### Fixed
- london marathon bot: parse event id
- async details fetcher can take note of urls too
- get_time_eta as hh:mm:ss format
- london marathon bot: take note of url errors too

## 0.0 - 2017-04-25

### Released
- repo

### Added
- list of current bots in README
