# Project 2 (FINAL) : BigData Analysis Project - Weather

**Due**: April 24 2017 @ 11:55pm

This project will have you perform Data Analysis and processing using
MapReduce / Apache Spark. The project will use the weather dataset from
<https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/>. This project will
use only 16 years of data (2000 - 2016) for all the stations starting with US
and elements TMAX, TMIN. 

## Creation of datasets

For the Global Historical Climatology Network (GHCN) [weather data][ghcn]:

```bash
mkdir data  # if it doesn't exist
cd data
for i in `seq 2000 2016`; do
    wget https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/${i}.csv.gz
    gzip -cd ${i}.csv.gz  | grep -e TMIN -e TMAX | grep ^US > ${i}.csv
done
```

For the GHCN station metadata (latitude and longitude):

```bash
cd data
wget ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt
awk 'OFS="," {print $1, $2, $3}' ghcnd-stations.txt > ghcnd-stations.csv
```

The Google Maps geocoding API is used to get the actual city and state name
for each weather station; see the function `getcity()` in
[`weatherstats.py`](weatherstats.py) for details.

## Weather measurement metadata

The following information serves as a definition of each field in one line of
data covering one station-day. Each field described below is separated by a
comma ( , ) and follows the order presented in this document.

    ID = 11 character station identification code
    YEAR/MONTH/DAY = 8 character date in YYYYMMDD format (e.g. 19860529 = May 29, 1986)
    ELEMENT = 4 character indicator of element type
    DATA VALUE = 5 character data value for ELEMENT
    M-FLAG = 1 character Measurement Flag
    Q-FLAG = 1 character Quality Flag
    S-FLAG = 1 character Source Flag
    OBS-TIME = 4-character time of observation in hour-minute format (i.e. 0700 =7:00 am)

See section III of the GHCN-Daily
<ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt> file for an explanation
of ELEMENT codes and their units as well as the M-FLAG, Q-FLAGS and S-FLAGS.

The OBS-TIME field is populated with the observation times contained in
NOAA/NCDC’s Multinetwork Metadata System (MMS).

## Requirements

Build a Hadoop map/reduce or Apache Spark analysis that yields the following:

* Average TMIN, TMAX for each year excluding abnormalities or missing data
* Maximum TMAX, Minimum TMIN for each year excluding abnormalities or missing
  data
* 5 hottest, 5 coldest weather stations for each year excluding abnormalities
  or missing data
* Hottest and coldest day and corresponding weather stations in the entire
  dataset

## Usage

On [OSC][]'s [Owens cluster][owens] cluster:

```bash
# request a cluster node
qsub -I -l nodes=1:ppn=12 -l walltime=04:00:00
module load spark

# change into the directory where this repo was cloned
cd /dir/where/you/cloned/this/repo

pyspark --executor-memory 18G --driver-memory 18G
```

Then at the PySpark prompt:

```python
>>> from weatherstats import run, run_whole_dataset

>>> run()

2000
====

Avg min temp = 4.4 deg C
Avg max temp = 17.6 deg C

Hottest station #1: USC00416892 (Pecos, TX 79772) - 37.4 deg C
Hottest station #2: USC00411013 (Brackettville, TX 78832) - 36.9 deg C
Hottest station #3: USC00045502 (Mecca, CA 92254) - 36.8 deg C
Hottest station #4: USC00024761 (Lake Havasu City, AZ 86403) - 35.0 deg C
Hottest station #5: USC00021026 (Buckeye, AZ 85326) - 34.0 deg C

[...]

>>> run_whole_dataset()

Entire dataset (2000-2016)
==========================

  * Loading all datasets into a single DataFrame...
  * Computing coldest station for entire dataset...

Coldest station was USC00501684 (Chicken, AK 99732) on 07 Feb 2008: -57.8 deg C

  * Computing hottest station for entire dataset...

Hottest station was USR0000HKAU (Kula, HI 96790) on 13 Feb 2015: 55.6 deg C
```


[ghcn]: ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/
[osc]: https://www.osc.edu/
[owens]: https://www.osc.edu/resources/technical_support/supercomputers/owens
