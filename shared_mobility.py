import requests
from datetime import datetime
import psycopg2
import sys
from yaml import load, FullLoader
from argparse import ArgumentParser
from mobility.db_runner import run_sql, get_once


def get_data(args):

    config_file = args.filename

    certificate = True
    if args.certificate_verification == 'off':
        certificate = False

    with open(config_file) as file:
        params = load(file, Loader=FullLoader)

    bbox = params['bbox']
    providers_info_url = params['providers_info_url']
    station_info_url = params['station_info_url']
    station_status_url = params['station_status_url']
    tablename = params['shared_station_tablename']

    servers = params['servers']

    # Get Stations
    r = requests.get(station_info_url, verify=certificate)

    if r.status_code != 200:
        sys.exit(1)

    stations = r.json()['data']['stations']

    station_ids = []

    station_sql = """
    INSERT INTO %s (idobj, "name", provider_id, geom) VALUES ('%s', '%s', '%s', %s) ON CONFLICT DO NOTHING
    """

    station_sql_list = []

    for station in stations:
        if station['lon'] >= bbox['xmin'] and station['lon'] <= bbox['xmax'] \
            and station['lat'] >= bbox['ymin'] and station ['lat'] <= bbox['ymax']:
                station_ids.append(station['station_id'])
                station_sql_list.append(station_sql % (
                    tablename,
                    station['station_id'], 
                    station['name'].replace("'", "''"), 
                    station['provider_id'],
                    "ST_Transform(ST_GeomFromText('POINT("+ str(station['lon']) + " " + str(station['lat']) +")', 4326), 2056)"
                ))

    run_sql(servers, station_sql_list)

    # Check uris (we use the first server to do so, as they all should contain the same data)
    url_sql = """
    SELECT provider_id FROM %s WHERE provider_url is null
    """
    records = get_once(servers[0], (url_sql % tablename))

    update_urls_sql = """
    UPDATE %s SET 
        provider_url = '%s',  
        store_uri_android = '%s',
        store_uri_ios = '%s'
    WHERE
        provider_id = '%s'
    """

    if len(records) > 0:
        r = requests.get(providers_info_url, verify=certificate)

        if r.status_code != 200:
            sys.exit(1)

        providers = r.json()['data']['providers']
        done = []
        
        provider_sql_list = []

        for record in records:
            
            if record[0] not in done:
                provider = list(filter(lambda x:x["provider_id"]==record[0], providers))
                if len(provider) == 0:
                    continue
                provider = provider[0]
                provider_sql_list.append(update_urls_sql % (
                    tablename,
                    provider['url'] if 'url' in provider else '-9999',
                    provider['rental_apps']['android']['store_uri'] if 'rental_apps' in provider else '-9999',
                    provider['rental_apps']['ios']['store_uri'] if 'rental_apps' in provider else '-9999',
                    record[0], 
                ))
                
                done.append(record[0])
        
        run_sql(servers, provider_sql_list)

    # Check vehicle availability
    r = requests.get(station_status_url, verify=certificate)

    if r.status_code != 200:
        sys.exit(1)

    stations = r.json()['data']['stations']

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
    
    for station_id in station_ids:
        station = list(filter(lambda x:x["station_id"]==station_id,stations))
        
        if len(station) == 0:
            continue
        
        station = station[0]
        
        station_sql_list.append(station_sql % (
            tablename,
            str(station['is_installed']), 
            str(station['is_renting']),
            str(station['is_returning']),
            datetime.fromtimestamp(station['last_reported']).isoformat(),
            str(station['num_bikes_available']),
            str(station['num_docks_available']),
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
    args = parser.parse_args()

    get_data(args)
