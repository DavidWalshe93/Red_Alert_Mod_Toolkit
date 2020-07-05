"""
Author:     David Walshe
Date:       03 July 2020
"""

import os
import logging

from configparser import ConfigParser

from src.db_driver.helpers.db_helper import DBHelper
from src.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class IniWriter:

    NURPLE_POSTFIX = "_nurple_mod.mpr"

    def __init__(self):
        self.model = DBHelper()
        self.writer = ConfigParser(allow_no_value=True)
        self.writer.optionxform = str

    def build(self):
        self.link()
        self.compile()

    def link(self):
        self.add(self.model.infantry)
        self.add(self.model.buildings)
        self.add(self.model.vehicles)
        self.add(self.model.aircraft)
        self.add(self.model.ships)

    def add(self, data: list):
        for item in data:
            section = item.pop("Tag").replace("[", "").replace("]", "")
            comment = item.pop("Name")

            self.writer.add_section(section)
            self.writer.set(section, f"; {comment}")
            for key, value in item.items():
                try:
                    self.writer.set(section, key, str(value))
                except Exception as err:
                    print(err)

    def compile(self):
        for mpr_file in self.mpr_files:
            out_file = mpr_file.replace(".mpr", "")

            with open(mpr_file, "r") as fh:
                mpr_content = fh.read()

            with open(f"{out_file}{self.NURPLE_POSTFIX}", "w") as fh:
                fh.write(f"; {'=' * 100}\n")
                fh.write(f"; Mod specific content below - Content generated by Mod Builder Application\n")
                fh.write(f"; {'=' * 100}\n")
                self.writer.write(fh)

                fh.write(f"; {'=' * 100}\n")
                fh.write(f"; Map specific content below - Content generated by Map Builder Application\n")
                fh.write(f"; {'=' * 100}\n")
                fh.write(mpr_content)

                logger.info(f"Created modded mpr file @ {mpr_file}")

    @property
    def mpr_files(self):
        try:
            map_dir = ConfigManager().map_directory
            mpr_files = os.listdir(map_dir)
            mpr_files = [os.path.join(map_dir, file) for file in mpr_files if file.endswith(".mpr")]
            mpr_files = [file for file in mpr_files if file.find(self.NURPLE_POSTFIX) == -1]

            return mpr_files
        except OSError as err:
            logger.error(f"Could not get map directory contents.\n\t"
                         f"User config: {ConfigManager().config}\n\t"
                         f"{err}")

            return []


