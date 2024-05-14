import requests
from datetime import datetime
import logging
import os
import sys
from yaml import load, FullLoader
from argparse import ArgumentParser
from mobility.db_runner import run_sql, get_once

current_path = os.getcwd()

logging.basicConfig(
    filename=os.path.join(current_path, 'logs/shared_mobility.log'),
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    filemode='w'
)

def get_providers_stations(base_station_url, certificate, payload, station_info_url, bbox, tablename, servers):

    r = requests.get(base_station_url, verify=certificate, params=payload)

    if r.status_code != 200:
        sys.exit()

    logging.info('Status code of shared mobility, get systems: %s' % r.status_code)

    system_list = r.json()['systems']
    # Update station list
    station_ids = []
    provider_ids = []
    station_sql_list = []

    for system in system_list:

        r = requests.get(base_station_url+'/'+system['id']+'/'+station_info_url, verify=certificate, params=payload)
        stations = r.json()['data']['stations']

        station_sql = """
        INSERT INTO %s (idobj, "name", provider_id, geom, store_uri_android, store_uri_ios) VALUES ('%s', '%s', '%s', %s, '%s', '%s')
        ON CONFLICT (idobj) DO UPDATE SET
        "name" = EXCLUDED."name",
        store_uri_android = EXCLUDED.store_uri_android,
        store_uri_ios = EXCLUDED.store_uri_ios
        """

        for station in stations:

            if station['lon'] >= bbox['xmin'] and station['lon'] <= bbox['xmax'] \
                    and station['lat'] >= bbox['ymin'] and station['lat'] <= bbox['ymax']:

                station_ids.append(station['station_id'])
                station_sql_list.append(station_sql % (
                    tablename,
                    station['station_id'],
                    station['name'].replace("'", "''"),
                    system['id'],
                    "ST_Transform(ST_GeomFromText('POINT(" + str(station['lon']) + " " + str(station['lat']) + ")', 4326), 2056)",
                    station['rental_uris']['android'] if 'rental_uris' in station else None,
                    station['rental_uris']['ios'] if 'rental_uris' in station else None,
                ))
                if system['id'] not in provider_ids:
                    provider_ids.append(system['id'])

    run_sql(servers, station_sql_list)
    logging.info('Updated station list for each provider having stations inside the bbox')

    # Delete all station which are not listed in station_ids
    delete_sql = ["DELETE FROM %s WHERE idobj not in ('%s')" % (
        tablename,
        "','".join(station_ids)
    )]
    run_sql(servers, delete_sql )
    logging.info('Deleted all stations which are not anymore referenced')


def get_data(args):

    config_file = args.filename

    certificate = True
    if args.certificate_verification == 'off':
        certificate = False

    station_only = False
    if args.station_only == 'yes':
        station_only = True

    with open(config_file) as file:
        params = load(file, Loader=FullLoader)

    # User parameters
    bbox = params['bbox']
    base_station_url = params['base_station_url']
    station_info_url = params['station_info_url']
    station_status_url = params['station_status_url']
    payload = {'authorization': params['authorization_email']}
    tablename = params['shared_station_tablename']
    servers = params['servers']

    if station_only is False:
        get_providers_stations(base_station_url, certificate, payload, station_info_url, bbox, tablename, servers)

    updated_stations = []

    # Get all providers
    sql = "SELECT provider_id FROM %s GROUP BY provider_id" % tablename
    rows = get_once(servers[0], sql)

    # Get all stations
    sql = "SELECT idobj FROM %s" % tablename
    stations = get_once(servers[0], sql)
    stations_ids = []
    for station in stations:
        stations_ids.append(station[0])

    station_sql = """
    UPDATE %s SET
        is_installed = %s,
        is_renting = %s,
        is_returning = %s,
        last_reported = '%s',
        num_bikes_available = %s,
        num_docks_available = %s,
        update_time = '%s'
    WHERE
        idobj = '%s'
    """

    now = datetime.now().isoformat()
    station_sql_list = []

    for row in rows:

        r = requests.get(base_station_url+"/"+row[0]+"/"+station_status_url, verify=certificate, params=payload)

        logging.info('Status code of shared mobility, get provider info: %s' % r.status_code)

        if r.status_code != 200:
            sys.exit()

        stations = r.json()['data']['stations']
        for station in stations:
            if station['station_id'] in stations_ids:
                stations_ids.remove(station['station_id'])

                station_sql_list.append(station_sql % (
                    tablename,
                    str(station['is_installed']),
                    str(station['is_renting']),
                    str(station['is_returning']),
                    datetime.fromtimestamp(station['last_reported']).isoformat(),
                    str(station['num_bikes_available']),
                    str(station['num_docks_available']) if 'num_docks_available' in station else 'null',
                    now,
                    station['station_id'],
                ))

    run_sql(servers, station_sql_list)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        '-f',
        '--filename',
        help='filename of the config file (optional, default would be config.yml)',
        default='config.yml',
        action='store'
    )
    parser.add_argument(
        '-c',
        '--certificate_verification',
        help='Turns off the HTTPS certificate verification (default is "on")',
        default='on',
        action='store'
    )
    parser.add_argument(
        '-s',
        '--station_only',
        help='If set to "yes", then the script only updates the station information and does not check for new station or providers (default is "no")',
        default='no',
        action='store'
    )

    args = parser.parse_args()

    get_data(args)
