import argparse


__version__ = '0.0.2.1'


def run():
    global args
    parser = argparse.ArgumentParser(description='Simple start with async rabbitmq consumers!')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("file", type=str, help="Select entrypoint of your consumer", nargs='?')
    group.add_argument("-s", "--start", metavar="DIRNAME", type=str, help="Input project name to create", nargs='?')
    parser.add_argument("-W", "--workers", metavar="10", default=10, type=int,  help="Select number of workers")
    parser.add_argument("-C", "--config", metavar="CONFIG_FILE.yml", default="config.yml", type=str, help="Select conf file of your consumer")
    parser.add_argument('-R', '--reload', dest='reload', action='store_true')
    args = parser.parse_args()

    if (dirname := args.start):
        from propan.startproject import create
        create(dirname)
    else:
        if args.reload:
            from propan.supervisors.watchgodreloader import WatchGodReload
            WatchGodReload(target=_run).run()
        else:
            _run()

def _run():
    import sys
    import uvloop
    import importlib

    from propan.config.configuration import init_settings

    uvloop.install()
    config = init_settings(args.config, **{
        "MAX_CONSUMERS": args.workers
    })
    sys.path.append(config.BASE_DIR)

    try:
        f, func = args.file.split(":", 2)
        mod = importlib.import_module(f)
        app = getattr(mod, func)
    except ValueError as e:
        from loguru import logger
        logger.error(e)
        logger.error('Please, input module like python_file:propan_app_name')
    else:
        app.run()