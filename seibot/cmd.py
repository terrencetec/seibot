"""Command line usage"""
import argparse
import configparser

import seibot.config
import seibot.seibot


def parser():
    """Parser"""
    parser = argparse.ArgumentParser(description="seibot")
    parser.add_argument("--get-seibot-config", action="store_true")
    parser.add_argument("--get-filter-config", action="store_true")
    parser.add_argument("--get-model-parameters", action="store_true")
    parser.add_argument("-c", "--config")
    parser.add_argument("-p", "--path")
    return parser


def main(args=None):
    """seibot"""
    options = parser().parse_args(args)

    if options.get_seibot_config:
        path = options.path
        if path is None:
            raise ValueError("Please specify path using the -p or --path."
                             "flag.")
        seibot.config.get_seibot_config(options.path)
        return 
    elif options.get_filter_config:
        path = options.path
        if path is None:
            raise ValueError("Please specify path using the -p or --path."
                             "flag.")
        seibot.config.get_filter_config(options.path)
        return

    if options.config is None:
        raise ValueError("Configuration file is not specified. "
                         "Use the -c or --config flag to specify the "
                         "path of the configuration file.")
    if options.path is None:
        raise ValueError("Please specify path of the output configuration "
                         "file using the -p or --path flag")
    
    bot = seibot.seibot.Seibot(options.config)
    bot.export_best_filters(options.path)
