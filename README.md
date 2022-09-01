# Hubstaff user activity stats CLI

A tool generating HTML activity reports from Hubstaff API.

## Installation
In order to build a CLI, you need to run
``` sh
make
```

On successful build step, `make` will output
a `./build/hubstats` self-contained executable (a python ZipApp archive).

To run a command you need a python of at least `3.7` version installed.

## Configuration
The tool heavily relies on INI config file.
The config can be specified with `--config` CLI param, with fallback to `~/.hubstats.cfg`.
To make sure it successfully run multiple times, the config should have a write permission (to store a refresh token).


**Minimal config example:**

``` ini
[DEFAULT]
organization_id = <org_id>
personal_token = <personal_api_token>
```
Organization ID can be extracted from your Hubstaff dashboard (e.g. https://app.hubstaff.com/dashboard/000001/ <- *000001* is an org ID)

You can obtain a personal token at [Hubstaff Develper portal](https://developer.hubstaff.com/personal_access_tokens/)


**A full list of CLI arguments:**
```
  --config PATH, -c PATH
                        Path to configuration INI file
                        (default: ~/.hubstats.cfg)

  --date YYYY-MM-DD, -d YYYY-MM-DD
                        Date to pull the activities
                        (default: yesterday)

  --output PATH, -o PATH
                        Output file (default: STDOUT)
```
