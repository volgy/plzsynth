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


"""Top-level package for plzsynth"""

from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

from enum import Enum

import serial
from serial.tools.list_ports import comports

__author__ = """Peter Volgyesi"""
__email__ = "peter.volgyesi@gmail.com"


class DeviceType(Enum):
    """ADF chip type"""

    ADF4350 = 1
    ADF4351 = 2


# gain index to dBm
gain_map = [-4.0, -1.0, 2.0, 5.0]


class PLZPLLADF:
    """
    PLZ-PLL-ADF synthesizer interface class
    """

    START_SYMBOL = b"\xAD"

    def __init__(
        self, serial_port=None, device=DeviceType.ADF4351, ref_clk=25e6,
    ):
        """
        Initialize PLZ-PLL-ADF synthesizer interface
        """
        if serial_port is None:
            for pinfo in comports():
                if pinfo.vid is not None:
                    serial_port = pinfo.device
                    break

        if serial_port is None:
            raise RuntimeError("No PLZ-PLL-ADF synthesizer found")

        self.ref_clk = ref_clk
        self.device = device
        self.serial_port = serial_port
        self.conn = serial.Serial(
            self.serial_port, baudrate=115200, timeout=1.0
        )
        self.stop(False)

    @staticmethod
    def _chksum(msg):
        """Calculate and return checksum for a message"""
        return sum(msg) & 0xFF

    def _send(self, msg, ack=True):
        """Send message with checkshum and wait for response"""
        msg += self._chksum(msg).to_bytes(1, "big")
        #self.conn.reset_input_buffer()
        self.conn.write(msg)
        recv = self.conn.read(3)
        if recv != self.START_SYMBOL + b"\x66\x13":
            raise RuntimeError("PLZ-PLL-ADF error")


    def start_tone(self, frequency, gain=3):
        """Start a single frequency tone"""
        msg = (
            self.START_SYMBOL
            + self.device.value.to_bytes(1, "big")
            + b"\x01"
            + int(4 - gain).to_bytes(1, "big")
            + int(self.ref_clk / 100).to_bytes(3, "big")
            + int(frequency / 1000).to_bytes(3, "big")
        )

        self._send(msg)

    def start_sweep(self, start, end, step, gain=3):
        """Start a single frequency tone"""
        msg = (
            self.START_SYMBOL
            + self.device.value.to_bytes(1, "big")
            + b"\x02"
            + int(4 - gain).to_bytes(1, "big")
            + int(self.ref_clk / 100).to_bytes(3, "big")
            + int(start / 1000).to_bytes(3, "big")
            + int(end / 1000).to_bytes(3, "big")
            + int(step).to_bytes(3, "big")
            + b"\x01"
        )

        self._send(msg)

    def stop(self, ack=True):
        """Stop signal generation"""
        msg = self.START_SYMBOL + b"\xFF"
        self._send(msg, ack)

    def __repr__(self):
        return (
            f"PLZ-PLL-ADF on {self.serial_port}, "
            f"{self.device.name}, "
            f"ref_clk: {self.ref_clk / 1e6:.3f} MHz"
        )
