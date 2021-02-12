import requests
from datetime import datetime
import psycopg2
import sys
from yaml import load, FullLoader
from argparse import ArgumentParser

def get_data(args):

    config_file = args.filename

    with open(config_file) as file:
        params = load(file, Loader=FullLoader)

    bbox = params['bbox']
    electric_station_url = params['electric_station_url']
    connection_params = params['connection_params']

    tablename = params['electric_station_tablename']

    connection = psycopg2.connect(
        host = connection_params['host'],
        database = connection_params['db'],
        user = connection_params['user'],
        password = connection_params['password']
    )

    cursor= connection.cursor()

    # Get everything...
    r = requests.get(electric_station_url, verify=False)

    if r.status_code != 200:
        sys.exit(1)
    
    features = r.json()['features']
    
    locations = []

    location_sql = """
    INSERT INTO %s (idobj, geom) VALUES ('%s', %s) ON CONFLICT DO NOTHING
    """

    for feature in features:
        lon = feature['geometry']['coordinates'][0]
        lat = feature['geometry']['coordinates'][1]

        if lon >= bbox['xmin'] and lon <= bbox['xmax'] \
            and lat >= bbox['ymin'] and lat <= bbox['ymax']:
            locations.append(feature)
            cursor.execute(location_sql % (
                tablename,
                feature['id'], 
                "ST_Transform(ST_GeomFromText('POINT("+ str(lon) + " " + str(lat) +")', 4326), 2056)"
            ))

    connection.commit()

    update_urls_sql = """
    UPDATE %s SET 
        description = '%s',
        availability = '%s'
    WHERE
        idobj = '%s'
    """

    for location in locations:
        description = location['properties']['description'].split('\n')
        description = ''.join(list(map(lambda x: x.strip(), description)))

        cursor.execute(update_urls_sql % (
            tablename,
            description, 
            location['properties']['Availability'], 
            location['id'], 
        ))

    connection.commit()

    cursor.close()
    connection.close()

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
