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
@click.option(
    "--host", default="127.0.0.1", help="The hostname of the Unifi controller."
)
@click.option("--port", default=8443, help="The port of the Unifi controller.")
@click.option("--verify/--no-verify", default=True, help="Verify SSL certificate.")
@click.option(
    "--site", default="default", help="The site ID used by the Unifi controller."
)
@click.option("--user", default="ubnt", help="The user account used to authenticate.")
@click.option(
    "--password",
    prompt="Password",
    hide_input=True,
    envvar="PASSWORD",
    help="The password used to authenticate.",
)
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@click.pass_context
def cli(ctx, host, port, verify, site, user, password, verbose):
    ctx.obj = {}
    ctx.obj["HOST"] = host
    ctx.obj["PORT"] = str(port)
    ctx.obj["URL"] = "https://" + host + ":" + str(port) + "/api/s/" + site + "/"
    ctx.obj["VERIFY"] = verify
    ctx.obj["USER"] = user
    ctx.obj["PASSWORD"] = password
    ctx.obj["VERBOSE"] = verbose

    payload = {"username": ctx.obj["USER"], "password": ctx.obj["PASSWORD"]}
    if ctx.obj["VERBOSE"]:
        click.echo("Logging in...")
    r = requests.post(
        "https://" + host + ":" + str(port) + "/api/login",
        data=json.dumps(payload),
        verify=ctx.obj["VERIFY"],
    )
    ctx.obj["COOKIES"] = r.cookies


@cli.command()
@click.pass_context
def events(ctx):
    """Display recent events."""
    if ctx.obj["VERBOSE"]:
        click.echo("Downloading recent events...")
    payload = {"_limit": 200, "_start": 0, "within": 1}
    r = requests.get(
        ctx.obj["URL"] + "stat/event",
        verify=ctx.obj["VERIFY"],
        cookies=ctx.obj["COOKIES"],
        data=json.dumps(payload),
    )
    event_response = json.loads(r.text)

    for (datetime, msg) in [
        (value["datetime"], value["msg"]) for value in event_response["data"]
    ]:
        click.echo("{0}\t{1}".format(datetime, msg))


def get_device_response(ctx):
    """Return the deserialized JSON response for /stat/device (devices)"""
    r = requests.get(
        ctx.obj["URL"] + "stat/device",
        verify=ctx.obj["VERIFY"],
        cookies=ctx.obj["COOKIES"],
    )
    return json.loads(r.text)


def get_device_hostnames(device_response):
    """Return a dictionary that maps device mac addresses to hostnames."""
    return dict(
        zip(
            [value["mac"] for value in device_response["data"]],
            [value["hostname"] for value in device_response["data"]],
        )
    )


@cli.command()
@click.pass_context
def devices(ctx):
    """List devices (AP)."""
    if ctx.obj["VERBOSE"]:
        click.echo("Getting devices data...")
    device_response = get_device_response(ctx)

    for (name, adopt_ip, num_sta, guest_num_sta) in [
        (value["name"], value["adopt_ip"], value["num_sta"], value["guest-num_sta"])
        for value in device_response["data"]
    ]:

        click.echo(
            "{0} {1} ({2} users, {3} guests)".format(
                name, adopt_ip, num_sta, guest_num_sta
            )
        )


@cli.command()
@click.pass_context
def clients(ctx):
    """List active clients."""
    if ctx.obj["VERBOSE"]:
        click.echo("Listing the active clients...")
    device_response = get_device_response(ctx)
    device_hostnames = get_device_hostnames(device_response)
    r = requests.get(
        ctx.obj["URL"] + "stat/sta",
        verify=ctx.obj["VERIFY"],
        cookies=ctx.obj["COOKIES"],
    )
    sta_response = json.loads(r.text)

    def get_client_hostname(value):
        if "hostname" in value:
            return value["hostname"]
        elif "name" in value:
            return value["name"]
        else:
            return "No hostname"

    def is_guest(value):
        if value["is_guest"]:
            return "guest"
        else:
            return ""

    for (mac, hostname, oui, ap, channel, signal, is_guest) in [
        (
            value["mac"],
            get_client_hostname(value),
            value["oui"],
            device_hostnames[value["ap_mac"]],
            value["channel"],
            value["signal"],
            is_guest(value),
        )
        for value in sta_response["data"]
    ]:
        click.echo(
            "{1} ({0} {2}) AP: {3}, CH: {4}, SG: {5}dBm {6}".format(
                mac, hostname, oui, ap, channel, signal, is_guest
            )
        )


@cli.command()
@click.argument("mac")
@click.pass_context
def unblock(ctx, mac):
    """Unblock a client using its MAC address."""
    if ctx.obj["VERBOSE"]:
        click.echo("Unblocking %s..." % mac)
    payload = {"cmd": "unblock-sta", "mac": mac}
    r = requests.post(
        ctx.obj["URL"] + "cmd/stamgr",
        verify=ctx.obj["VERIFY"],
        cookies=ctx.obj["COOKIES"],
        data=json.dumps(payload),
    )
    click.echo(r.text)


@cli.command()
@click.argument("mac")
@click.pass_context
def block(ctx, mac):
    """Block a client using its MAC address."""
    if ctx.obj["VERBOSE"]:
        click.echo("Blocking %s..." % mac)
    payload = {"cmd": "block-sta", "mac": mac}
    r = requests.post(
        ctx.obj["URL"] + "cmd/stamgr",
        verify=ctx.obj["VERIFY"],
        cookies=ctx.obj["COOKIES"],
        data=json.dumps(payload),
    )
    click.echo(r.text)


@cli.command()
@click.argument("mac")
@click.pass_context
def reconnect(ctx, mac):
    """Reconnect a client using its MAC address."""
    if ctx.obj["VERBOSE"]:
        click.echo("Reconnecting %s..." % mac)
    payload = {"cmd": "kick-sta", "mac": mac}
    r = requests.post(
        ctx.obj["URL"] + "cmd/stamgr",
        verify=ctx.obj["VERIFY"],
        cookies=ctx.obj["COOKIES"],
        data=json.dumps(payload),
    )
    click.echo(r.text)
