from yaml import load, FullLoader
from argparse import ArgumentParser
from mobility.db_runner import run_sql


def truncate(args):

    config_file = args.filename

    table = args.type + '_tablename'

    with open(config_file) as file:
        params = load(file, Loader=FullLoader)

    tablename = params[table]
    servers = params['servers']

    sql = 'TRUNCATE TABLE %s' % tablename

    run_sql(servers, [sql])


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

    truncate(args)
