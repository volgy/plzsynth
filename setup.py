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

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = ["click", "pyserial"]


setup(
    author="Peter Volgyesi",
    author_email="peter.volgyesi@gmail.com",
    python_requires=">=3.6",
    description="Library and tools for PLZ-PLL-ADF boards",
    entry_points={"console_scripts": ["plzsynth=plzsynth.__main__:cli",],},
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme,
    keywords="PLZ-PLL-ADF, RF, synthesizer",
    name="plzsynth",
    packages=find_packages(include=["plzsynth", "plzsynth.*"]),
    url="https://github.com/volgy/plzsynth",
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    zip_safe=False,
)
