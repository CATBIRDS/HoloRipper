# HoloRipper

Holoripper is a Python script for scraping YouTube's pages for data about specific channels' streams.

For a given channel, HoloRipper will grab its live streaming status, as well as a list of any upcoming streams, including a standardized UTC timestamp of their listed start time. These streams will be organized and stored into a generated .json file. It can also download profile images for channels.

Holoripper can be seen in use [here](https://catbird.club/holotracker), where it serves as the server-side script to generate up-to-date tracking data. 

## Installation

This repository mostly serves as a "snapshot" display of the script, in the interests of keeping my projects open-source and publicly available. It's not necessarily the most up-to-date version, nor is it necessarily designed with ease-of-use for external purposes in mind. It may randomly break if your usage case and style doesn't overlap with mine. However, if you'd like to use HoloRipper yourself anyway, you can do so after installing some prerequisites.

HoloRipper runs on Python 3, and makes use of [requests](https://pypi.org/project/requests/), [pytz](https://pypi.org/project/pytz/), [argparse](https://pypi.org/project/argparse/), and [datetime](https://pypi.org/project/DateTime/):

```bash
pip install requests pytz argparse datetime
```
## Customization

By default, HoloRipper will generate profile images to ```assets/profile/```, and will output the final .json file to ```data/``` - These paths are located on ```line 46``` and ```line 172``` respectively, if you choose to change them. Additionally, it will grab its channel data from ```data/``` - located on ```line 29```

HoloRipper will grab channel data from a single ```Master.json``` file. An example of this master file has been included in this repo for you to inspect, appropriately named. This Master file is nothing but a list of IDs paired with a human-readable name pairing of the channel, filed under ```nameEN```. The channel ID is mandatory for HoloRipper to function, but the corresponding human-readable text can be whatever you'd like.

It's worth mentioning again here that this script is not exactly built for external usage, and is made public mostly for purposes of transparency. You may notice that the Master.json file has lots of additional information beyond these listed attributes - they are used by the [HoloTracker](https://catbird.club/holotracker) site, in the interests of consolidating all key information into a single location. For the purposes of HoloRipper exclusively, these elements can be entirely ignored, or replaced with whatever you want if you so desire.

## Usage

Normal operation: Just run it.

```bash
python3 HoloRipper 
```

Note that HoloRipper will NOT download profile images by default.

To download profile images as well, run HoloRipper with the ```-profiles True``` argument.

HoloRipper will display the current running mode (profiles enabled/disabled) and give status displays for each channel it is told to scrape as it runs.

### NOTE:
HoloRipper is kind of a mess. It's a work in progress. Contributions are welcome.
