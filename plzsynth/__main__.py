#!/usr/bin/env python
#
# Copyright (C) 2022 Peter Volgyesi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Main entry point for plzsynth"""

import sys
from time import sleep, time
import random

import click

from . import PLZPLLADF, DeviceType, gain_map


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--port",
    "-p",
    help="Serial port  [default: first found]",
    metavar="SERIAL_DEVICE",
)
@click.option(
    "--device",
    "-d",
    type=click.Choice([t.name for t in DeviceType], case_sensitive=False),
    default=DeviceType.ADF4351.name,
    show_default=True,
    help="ADF device type",
)
@click.option(
    "--ref-clk",
    "-r",
    type=click.FloatRange(10.0, 250.0),
    default=25.0,
    show_default=True,
    help="Reference clock (MHz)",
)
@click.option(
    "--gain",
    "-g",
    type=click.IntRange(0, len(gain_map) - 1, clamp=True),
    default=3,
    show_default=True,
    help="Gain",
)
@click.pass_context
def cli(ctx, port, device, ref_clk, gain):
    """PLZ-PLL-ADF command line tool"""
    ctx.ensure_object(dict)
    ctx.obj["port"] = port
    ctx.obj["device"] = device
    ctx.obj["ref_clk"] = ref_clk
    ctx.obj["gain"] = gain


@cli.command()
@click.option(
    "--freq",
    "-f",
    type=click.FloatRange(35.0, 4400.0),
    required=True,
    help="Frequency in MHz",
)
@click.pass_context
def tone(ctx, freq):
    """Emit a single frequency tone"""
    gain = ctx.obj["gain"]
    device = PLZPLLADF(
        serial_port=ctx.obj["port"],
        device=DeviceType[ctx.obj["device"]],
        ref_clk=ctx.obj["ref_clk"] * 1e6,
    )
    print(f"Using {device}")
    device.start_tone(freq * 1e6, gain)
    print(f"Tone {freq} MHz, gain {gain_map[gain]} dBm")
    print("Press Ctrl-C to stop")
    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        pass
    device.stop()

@cli.command()
@click.option(
    "--start",
    "-s",
    type=click.FloatRange(35.0, 4400.0),
    required=True,
    help="Start frequency in MHz",
)
@click.option(
    "--end",
    "-e",
    type=click.FloatRange(35.0, 4400.0),
    required=True,
    help="End frequency in MHz",
)
@click.option(
    "--step",
    "-d",
    type=click.FloatRange(1.0, 10000.0),
    required=True,
    help="Step frequency in kHz",
)
@click.pass_context
def sweep(ctx, start, end, step):
    """Sweeping between start and end frequencies"""
    gain = ctx.obj["gain"]
    device = PLZPLLADF(
        serial_port=ctx.obj["port"],
        device=DeviceType[ctx.obj["device"]],
        ref_clk=ctx.obj["ref_clk"] * 1e6,
    )
    print(f"Using {device}")
    device.start_sweep(start * 1e6, end * 1e6, step * 1e3, gain)
    print(f"Sweep from {start} to {end} MHz with {step} kHz steps, "
          f"gain {gain_map[gain]} dBm")
    print("Press Ctrl-C to stop")
    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        pass
    device.stop()


@cli.command()
@click.option(
    "--start",
    "-s",
    type=click.FloatRange(35.0, 4400.0),
    required=True,
    help="Start frequency in MHz",
)
@click.option(
    "--end",
    "-e",
    type=click.FloatRange(35.0, 4400.0),
    required=True,
    help="End frequency in MHz",
)
@click.option(
    "--step",
    "-d",
    type=click.FloatRange(1.0, 10000.0),
    required=True,
    help="Step frequency in kHz",
)
@click.option(
    "--dwell-time",
    "-t",
    type=float,
    required=True,
    help="Dwell time im milliseconds",
)

@click.pass_context
def hop(ctx, start, end, step, dwell_time):
    """Random frequency hopping between start and end freqs"""
    gain = ctx.obj["gain"]
    device = PLZPLLADF(
        serial_port=ctx.obj["port"],
        device=DeviceType[ctx.obj["device"]],
        ref_clk=ctx.obj["ref_clk"] * 1e6,
    )
    print(f"Using {device}")
    print(f"Random hopping from {start} to {end} MHz with {step} kHz steps, "
          f"dwell time {dwell_time} ms, gain {gain_map[gain]} dBm")
    print("Press Ctrl-C to stop")
    t_wait = dwell_time / 1000.0
    try:
        while True:
            freq = random.uniform(1e6 * start, 1e6 * end)
            freq -= freq % int(step * 1000) #TODO: small random bias
            device.start_tone(freq, gain)
            #print(f"Freq: {freq} MHz")
            sleep(t_wait)
            device.stop()
            # TODO: calibrate t_wait

    except KeyboardInterrupt:
        pass
    device.stop()


if __name__ == "__main__":
    sys.exit(cli(prog_name="plzsynth"))
