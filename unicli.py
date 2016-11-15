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
@click.option('--host', prompt='Host',
              default='127.0.0.1',
              help='The hostname of the Unifi controller.')
@click.option('--port', prompt='Port',
              default=8443,
              help='The port of the Unifi controller.')
@click.option('--verify/--no-verify', prompt='Verify SSL',
              default=True,
              help='Verify SSL certificate.')
@click.option('--site', prompt='Site ID',
              default='default',
              help='The site ID used by the Unifi controller.')
@click.option('--user', prompt='User', default='ubnt',
              help='The user account used to authenticate.')
@click.option('--password', prompt='Password', hide_input=True,
              help='The password used to authenticate.')
@click.pass_context
def cli(ctx, host, port, verify, site, user, password):
    ctx.obj = {}
    ctx.obj['HOST'] = host
    ctx.obj['PORT'] = str(port)
    ctx.obj['URL'] = 'https://' + host + ':' + str(port) + '/api/s/' + site + '/'
    ctx.obj['VERIFY'] = verify
    ctx.obj['USER'] = user
    ctx.obj['PASSWORD'] = password

    payload = {'username': ctx.obj['USER'], 'password': ctx.obj['PASSWORD']}
    click.echo('Logging in...')
    r = requests.post('https://' + host + ':' + str(port) + '/api/login',
                     data=json.dumps(payload),
                     verify=ctx.obj['VERIFY'])
    ctx.obj['COOKIES'] = r.cookies


@cli.command()
@click.pass_context
def list(ctx):
    """List clients."""
    click.echo('Listing the clients...')
    r = requests.get(ctx.obj['URL'] + 'stat/sta', verify=ctx.obj['VERIFY'],
                     cookies=ctx.obj['COOKIES'])
    for mac in [value['mac'] for value in json.loads(r.text)['data']]:
        click.echo(mac)


@cli.command()
@click.argument('mac')
@click.pass_context
def unblock(ctx, mac):
    """Unblock a client using its MAC address."""
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
    click.echo('Blocking %s...' % mac)
    payload = {'cmd': 'block-sta', 'mac': mac}
    r = requests.post(ctx.obj['URL'] + 'cmd/stamgr', verify=ctx.obj['VERIFY'],
                     cookies=ctx.obj['COOKIES'], data=json.dumps(payload))
    click.echo(r.text)
