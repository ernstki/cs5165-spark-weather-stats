#!/usr/bin/env python
from pyspark import SparkContext
from pyspark.sql import SQLContext, Row


sc = SparkContext.getOrCreate() #appName='weatherStats')
sqlc = SQLContext(sc)


def mkdf(filename):
    """
    Read filename (or glob; things like '20??.csv' will work) and return a
    handle to a PySpark DataFrame
    """
    raw = sc.textFile(filename)
    data = raw.map(lambda x: x.split(','))
    table = data.map(lambda r: Row(sta=r[0], date=r[1], meas=r[2],
                                   degc=int(r[3]), m=r[4], q=r[5], s=r[6],
                                   time=r[7]))
    df = sqlc.createDataFrame(table)
    return df.filter(df.q=='')  # prune measurements w/ quality problems


def mkstations(filename):
    """
    Read in comma-separated data with station identifiers and return a PySpark
    DataFrame

    Source: https://mesonet.agron.iastate.edu/sites/networks.php?network=_ALL_&format=csv&nohtml=on

    Headers: stid,station_name,lat,lon,elev,begints,iem_network
    """
    raw = sc.textFile(filename)
    data = raw.map(lambda x: x.split(','))
    table = data.map(lambda r: Row(stid=r[0], station_name=r[1], lat=r[2],
                                   lon=r[3], elev=r[4], begints=r[5],
                                   iem_network=r[6]))
    return sqlc.createDataFrame(table)


def getcity(stations, sta):
    """
    Given 'stations' DataFrame (generated by mkstations), look up city and
    state from Google Maps API for given station ID 'sta'.
    """
    import json 
    from urllib import urlopen
    baseurl = 'https://maps.googleapis.com/maps/api/geocode/json?sensor=false'

    r = stations.filter(stations.stid==sta).collect()
    if r:
        (lat, lon) = (r[0].lat, r[0].lon)
    else:
        raise RuntimeError("Station '%s' not found" % sta)

    response = urlopen('%s&latlng=%s,%s' % (baseurl, lat, lon))
    raw = response.read()
    json = json.loads(raw)
    return json['results'][1]['formatted_address']


def run():
    """
    Run analyses
    """

    stations = mkstations('data/stations.csv')

    for col in ['begints', 'elev', 'iem_network']: # station_name, stid
        stations = stations.drop(col)

    for year in range(2000,2001): #17):
        df = mkdf('data/%s.csv' % str(year))

        print("\n%s\n====\n" % year)

        # join with 'stations' table (adds lat, lon, station_name, stid)
        df = df.join(stations, df.sta==stations.stid)

        # Average minimum temperature
        avgmin = df.filter(df.meas=='TMIN').groupBy().mean('degc').collect()[0]

        # Average maximum temperature
        avgmax = df.filter(df.meas=='TMAX').groupBy().mean('degc').collect()[0]


if __name__ == '__main__':
    run()
