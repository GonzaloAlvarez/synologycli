#!/bin/sh
''':'
[ -f '.venv/bin/python' ] && exec .venv/bin/python "$0" "$@"
for name in python3 python; do
    if type "$name" > /dev/null 2>&1; then
        "$name" -m venv .venv
        .venv/bin/python -m pip install --upgrade pip setuptools click loguru click_loguru synology_api
        exec .venv/bin/python "$0" "$@"
    fi
done
echo >&2 "Please install python"
exit 1
':'''
# -*- coding: utf-8 -*-
# Copyright: (c) 2018, Gonzalo Alvarez

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import sys
import click
import configparser
import getpass
from loguru import logger  # noqa: E402
from click_loguru import ClickLoguru  # # noqa: E402
from synology_api import filestation

__program__ = 'Uploader'
__version__ = '0.0.1'

click_loguru = ClickLoguru(__program__, __version__)


@click.group(invoke_without_command=True)
@click_loguru.logging_options
@click_loguru.stash_subcommand()
@click_loguru.init_logger(logfile=False)
@click.version_option(prog_name=__program__, version=__version__)
@click.pass_context
def cli(ctx, **kwargs):
    pass


class SynologyConfig(configparser.ConfigParser):
    def __init__(self):
        super(SynologyConfig, self).__init__()
        self.config_file = os.path.join(os.getcwd(), 'synology.conf')
        if not os.path.isfile(self.config_file):
            self['synology'] = {}
            self['synology']['host'] = input('Enter synology host name [raidnas.lan]: ') or 'raidnas.lan'
            self['synology']['port'] = input('Enter port number [5000]: ') or '5000'
            self['synology']['username'] = input('Enter username [admin]: ') or 'admin'
            self['synology']['password'] = getpass.getpass('Enter password [admin]: ') or 'admin'
            self['synology']['path'] = input('Enter remote folder [/share]: ') or '/share'
            with open(self.config_file, 'w') as cfile:
                self.write(cfile)
        else:
            self.read(self.config_file)


class Synology:
    def __init__(self, config):
        self.config = config
        self.host = config.get('synology', 'host')
        self.port = config.get('synology', 'port')
        self.username = config.get('synology', 'username')
        self.password = config.get('synology', 'password')
        self.remote_path = config.get('synology', 'path')
        logger.info(f'Logging in to synology on [{self.host}]')
        self.fl = filestation.FileStation(self.host, self.port, self.username, self.password, secure=False, cert_verify=False, dsm_version=7, debug=False, otp_code=None)
        logger.info(f'Logged in')

    def upload(self, filename, dest=None):
        logger.info(f'Uploading file [{filename}]')
        dest_path = self.remote_path
        if dest:
            dest_path = os.path.join(self.remote_path, dest)
        self.fl.upload_file(dest_path, filename)
        logger.info(f'File uploaded')

    def download(self, filename):
        logger.info(f'Downloading file [{filename}]')
        file_path = os.path.join(self.remote_path, filename)
        self.fl.get_file(path=file_path, mode='download')
        logger.info('File downloaded')

    def list(self):
        logger.info(f'Showing folder [{self.remote_path}]')
        result = self.fl.get_file_list(self.remote_path)['data']
        folders = [fdr['name'] for fdr in result['files'] if fdr['isdir']]
        return (folders, None)

    def mkdir(self, name):
        logger.info(f'Creating folder [{name}]')
        self.fl.create_folder(self.remote_path, name)


@cli.command(name='up', help='Upload file')
@click.argument('filename')
@click.pass_context
def file_upload(ctx, filename):
    cfg = SynologyConfig()
    sy = Synology(cfg)
    if os.path.isdir(filename):
        for root, dirs, files in os.walk(filename):
            parent = os.path.join(os.path.basename(filename), os.path.relpath(root, filename))
            for file in files:
                sy.upload(os.path.join(root, file), os.path.join(parent, file))
    else:
        sy.upload(filename)


@cli.command(name='dw', help='Download file')
@click.argument('filename')
@click.pass_context
def file_download(ctx, filename):
    cfg = SynologyConfig()
    sy = Synology(cfg)
    sy.download(filename)


@cli.command(name='ls', help='List Files')
@click.pass_context
def list(ctx):
    cfg = SynologyConfig()
    sy = Synology(cfg)
    dirs, files = sy.list()
    for dir in dirs or []:
        print(f'[{dir}]')
    for fl in files or []:
        print(fl)


@cli.command(name='mkdir', help='Create Folder')
@click.argument('foldername')
@click.pass_context
def mkdir(ctx, foldername):
    cfg = SynologyConfig()
    sy = Synology(cfg)
    sy.mkdir(foldername)


@cli.command(name='push', help='Upload and delete file')
@click.argument('filename')
@click.pass_context
def file_push(ctx, filename):
    cfg = SynologyConfig()
    sy = Synology(cfg)
    sy.upload(filename)
    os.remove(filename)


if __name__ == '__main__':
    sys.exit(cli(obj={}))
