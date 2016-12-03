# -*- coding: utf-8 -*-
"""
    unicli.py
    ~~~~~~~~~
    Command line utility to interact with the Unifi API
    :copyright: (c) 2016 by Nicolas Untz.
    :license: BSD, see LICENSE for more details.
"""

import click
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


@click.group()
@click.option('--host',
              default='127.0.0.1',
              help='The hostname of the Unifi controller.')
@click.option('--port',
              default=8443,
              help='The port of the Unifi controller.')
@click.option('--verify/--no-verify',
              default=True,
              help='Verify SSL certificate.')
@click.option('--site',
              default='default',
              help='The site ID used by the Unifi controller.')
@click.option('--user', default='ubnt',
              help='The user account used to authenticate.')
@click.option('--password', prompt='Password', hide_input=True,
              envvar='PASSWORD', help='The password used to authenticate.')
@click.option('-v', '--verbose', count=True)
@click.option('-v', '--verbose', is_flag=True,
              help='Enables verbose mode.')
@click.pass_context
def cli(ctx, host, port, verify, site, user, password, verbose):
    ctx.obj = {}
    ctx.obj['HOST'] = host
    ctx.obj['PORT'] = str(port)
    ctx.obj['URL'] = 'https://' + host + ':' + str(port) + '/api/s/' + site + '/'
    ctx.obj['VERIFY'] = verify
    ctx.obj['USER'] = user
    ctx.obj['PASSWORD'] = password
    ctx.obj['VERBOSE'] = verbose

    payload = {'username': ctx.obj['USER'], 'password': ctx.obj['PASSWORD']}
    if ctx.obj['VERBOSE']:
        click.echo('Logging in...')
    r = requests.post('https://' + host + ':' + str(port) + '/api/login',
                     data=json.dumps(payload),
                     verify=ctx.obj['VERIFY'])
    ctx.obj['COOKIES'] = r.cookies


@cli.command()
@click.pass_context
def events(ctx):
    """Display recent events."""
    if ctx.obj['VERBOSE']:
        click.echo('Downloading recent events...')
    r = requests.get(ctx.obj['URL'] + 'stat/event', verify=ctx.obj['VERIFY'],
                     cookies=ctx.obj['COOKIES'])

    for (datetime, msg) in [(value['datetime'], value['msg']) for value in
                            json.loads(r.text)['data']]:
        click.echo('{0}\t{1}'.format(datetime, msg))


@cli.command()
@click.pass_context
def devices(ctx):
    """List devices (AP)."""
    if ctx.obj['VERBOSE']:
        click.echo('Getting devices data...')
    r = requests.get(ctx.obj['URL'] + 'stat/device', verify=ctx.obj['VERIFY'],
                     cookies=ctx.obj['COOKIES'])

    for (name, adopt_ip, num_sta, guest_num_sta) in [(value['name'],
          value['adopt_ip'], value['num_sta'], value['guest-num_sta'])
          for value in json.loads(r.text)['data']]:

        click.echo('{0} {1} ({2} users, {3} guests)'.format(name,
                                  adopt_ip, num_sta, guest_num_sta))


@cli.command()
@click.pass_context
def clients(ctx):
    """List active clients."""
    if ctx.obj['VERBOSE']:
        click.echo('Listing the active clients...')
    r = requests.get(ctx.obj['URL'] + 'stat/sta', verify=ctx.obj['VERIFY'],
                     cookies=ctx.obj['COOKIES'])

    def get_hostname(value):
        if 'hostname' in value:
            return value['hostname']
        else:
            return 'No hostname'

    for (mac, hostname) in [(value['mac'], get_hostname(value)) for value in
                            json.loads(r.text)['data']]:
        click.echo('{0}\t{1}'.format(mac, hostname))


@cli.command()
@click.argument('mac')
@click.pass_context
def unblock(ctx, mac):
    """Unblock a client using its MAC address."""
    if ctx.obj['VERBOSE']:
        click.echo('Unblocking %s...' % mac)
    payload = {'cmd': 'unblock-sta', 'mac': mac}
    r = requests.post(ctx.obj['URL'] + 'cmd/stamgr', verify=ctx.obj['VERIFY'],
                     cookies=ctx.obj['COOKIES'], data=json.dumps(payload))
    click.echo(r.text)


@cli.command()
@click.argument('mac')
@click.pass_context
def block(ctx, mac):
    """Block a client using its MAC address."""
    if ctx.obj['VERBOSE']:
        click.echo('Blocking %s...' % mac)
    payload = {'cmd': 'block-sta', 'mac': mac}
    r = requests.post(ctx.obj['URL'] + 'cmd/stamgr', verify=ctx.obj['VERIFY'],
                     cookies=ctx.obj['COOKIES'], data=json.dumps(payload))
    click.echo(r.text)
