from datetime import datetime
import psycopg2
import sys
from yaml import load, FullLoader
from argparse import ArgumentParser


def check_timeout(args):

    config_file = args.filename

    table = args.type + '_tablename'

    with open(config_file) as file:
        params = load(file, Loader=FullLoader)

    tablename = params[table]
    servers = params['servers']
    timedelta = float(params['update_timeout']) * 3600

    error = []

    sql = 'SELECT max(update_time) FROM %s' % tablename

    now = datetime.now()

    for server in servers:
        connection = psycopg2.connect(
            host=server['host'],
            database=server['db'],
            user=server['user'],
            password=server['password']
        )
        cursor = connection.cursor()
        cursor.execute(sql)
        then = cursor.fetchone()[0]
        tdelta = now - then
        seconds = tdelta.total_seconds()

        if seconds > timedelta:
            error.append('Timeout for server: %s' % server['host'])

        cursor.close()
        connection.close()

    if len(error) > 0:
        sys.exit('\n'.join(error))


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
        '-t',
        '--type',
        help='Defines which services have to be analyzed (default to shared_station)',
        default='shared_station',
        action='store'
    )
    args = parser.parse_args()

    check_timeout(args)
