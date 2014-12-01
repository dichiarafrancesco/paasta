#!/usr/bin/env python
"""
Contains methods used by the paasta client to check whether Yelp service
passes all the markers required to be considered paasta ready.
"""
import os

from service_deployment_tools.paasta_cli.utils import \
    is_file_in_dir, check_mark, x_mark


def add_subparser(subparsers):
    check_parser = subparsers.add_parser(
        'check',
        description="Execute 'paasta check' from service repo root",
        help="Determine whether service in pwd is paasta ready")
    check_parser.set_defaults(command=paasta_check)


def file_exists_check(filename, path):
    """
    Print whether filename exists within pwd or one of its children
    """
    if is_file_in_dir(filename, path):
        print "%s Found %s" % (check_mark(), filename)
    else:
        print "%s Missing %s" % (x_mark(), filename)


def deploy_check():
    """
    Check whether deploy.yaml exists in service directory
    """
    service_name = os.path.basename(os.getcwd())
    service_path = os.path.join('/nail/etc/services', service_name)
    file_exists_check('deploy.yaml', service_path)


def docker_check():
    """
    Check whether Dockerfile exists in service directory
    """
    file_exists_check('Dockerfile', os.getcwd())


def sensu_check():
    """
    Check whether monitoring.yaml exists in service directory
    """
    service_name = os.path.basename(os.getcwd())
    service_path = os.path.join('/nail/etc/services', service_name)
    file_exists_check('monitoring.yaml', service_path)


def smartstack_check():
    """
    Check whether smartstack.yaml exists in service directory
    """
    service_name = os.path.basename(os.getcwd())
    service_path = os.path.join('/nail/etc/services', service_name)
    file_exists_check('smartstack.yaml', service_path)


def paasta_check(args):
    """
    Analyze the service in the PWD to determine if it is paasta ready
    """
    deploy_check()
    docker_check()
    sensu_check()
    smartstack_check()