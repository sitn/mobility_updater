import requests
from datetime import datetime
import sys
from yaml import load, FullLoader
from argparse import ArgumentParser
from mobility.db_runner import run_sql

def get_data(args):

    config_file = args.filename

    with open(config_file) as file:
        params = load(file, Loader=FullLoader)

    bbox = params['bbox']
    electric_station_url = params['electric_station_url']

    tablename = params['electric_station_tablename']

    servers = params['servers']

    # Get everything...
    r = requests.get(electric_station_url, verify=False)

    if r.status_code != 200:
        sys.exit(1)
    
    features = r.json()['features']
    
    locations = []

    location_sql = "INSERT INTO %s (idobj, geom) VALUES ('%s', %s) ON CONFLICT DO NOTHING"

    location_sql_list = []

    for feature in features:
        lon = feature['geometry']['coordinates'][0]
        lat = feature['geometry']['coordinates'][1]

        if lon >= bbox['xmin'] and lon <= bbox['xmax'] \
            and lat >= bbox['ymin'] and lat <= bbox['ymax']:
            locations.append(feature)
            location_sql_list.append(location_sql % (
                tablename,
                feature['id'], 
                "ST_Transform(ST_GeomFromText('POINT("+ str(lon) + " " + str(lat) +")', 4326), 2056)"
            ))

    run_sql(servers, location_sql_list)

    update_urls_sql = """
    UPDATE %s SET 
        description = '%s',
        availability = '%s',
        update_time = '%s'
    WHERE
        idobj = '%s'
    """
    
    location_sql_list = []
    now = datetime.now().isoformat()

    for location in locations:
        description = location['properties']['description'].split('\n')
        description = ''.join(list(map(lambda x: x.strip(), description)))

        location_sql_list.append(update_urls_sql % (
            tablename,
            description, 
            location['properties']['Availability'],
            now,
            location['id'], 
        ))

    run_sql(servers, location_sql_list)

if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        '-f',
        '--filename',
        help='filename of the config file (optional, default would be config.yml)',
        default='config.yml',
        action='store'
    )
    args = parser.parse_args()

    get_data(args)