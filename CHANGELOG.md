# Change Log
All notable changes to this project will be documented in this file.

## 0.1.9 - 2017-08-18

### Refactored
- all bots now in `bots` module

## 0.1.8 - 2017-06-08

### Added
- lang option in Github.get_starred_repos
- sample scripts to printout github daily trends
- color output in Github daily trends

### Fixed
- dmca error handling in GithubApi

## 0.1.7 - 2017-05-23

### Added
- imdb list data scraper

### Fixed
- minor improvements in ita industries data scraper

## 0.1.6 - 2017-05-19

### Refactored
- ita industries data scraper

### Added
- ita industries data scraper: utils
- rotten tomatoes in README

## 0.1.5 - 2017-05-16

### Added
- Tour de France scraper

## 0.1.4 - 2017-05-12

### Added
- GoogleSearchBot in ita industries project
- Pagine Gialle Bot in ita industries project

## 0.1.3 - 2017-04-27

### Added
- statistik races list downloader (async via tor)
- statistik races details downloader (async via tor)
- statistik runners details downloader (async via tor)
- statistik runners mongodb database downloader (async via tor)

### Fixed
- statistik races list downloader pages url
- statistik races details downloader folders path

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
- async details downloader can take note of urls too
- get_time_eta as hh:mm:ss format
- london marathon bot: take note of url errors too

## 0.0 - 2017-04-25

### Released
- repo

### Added
- list of current bots in README
