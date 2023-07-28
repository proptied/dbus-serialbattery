# -*- coding: utf-8 -*-
from struct import unpack_from
from typing import Optional
from utils import logger
from bms.lltjbd import LltJbdProtection, LltJbd, readCmd

REG_MFGNAME = 0xA0
REG_BARCODE = 0xA2


class LltJbd_Sfk(LltJbd):
    BATTERYTYPE = "LltJbd_Sfk"

    def __init__(self, port: Optional[str], baud: Optional[int], address: Optional[str]):
        super(LltJbd_Sfk, self).__init__(port, baud, address)

        self.protection = LltJbdProtection()
        self.type = self.BATTERYTYPE

        self.mfg_name: str = ""
        self.barcode: str = ""

        logger.info("Init of LltJbd_Sfk")

    def test_connection(self):
        # call a function that will connect to the battery, send a command and retrieve the result.
        # The result or call should be unique to this BMS. Battery name or version, etc.
        # Return True if success, False for failure
        result = False
        logger.info("Starting test of LltJbd_Sfk")
        try:
            result = super().test_connection()
            result = result and self.test_sfk_settings()
        except Exception as err:
            logger.error(f"Unexpected {err=}, {type(err)=}")
            result = False

        return result

    def test_sfk_settings(self):
        if self.get_sfk_settings() and self.mfg_name == "SUN FUN KITS":
            return True

        return False

    def get_sfk_settings(self):
        try:
            with self.eeprom(writable=False):
                mfg_name = self.read_serial_data_llt(readCmd(REG_MFGNAME))
                if mfg_name:
                    self.mfg_name = str(unpack_from(">x12s", mfg_name)[0].decode("utf-8"))
        except Exception as err:
            logger.error(f"Unexpected {err=}, {type(err)=}")

        return True

    def unique_identifier(self) -> str:
        """
        Used to identify a BMS when multiple BMS are connected
        """
        barcode = self.read_serial_data_llt(readCmd(REG_BARCODE))
        if barcode:
            self.barcode = str(unpack_from(">x6s", barcode)[0].decode("utf-8"))

        if self.barcode != "":
            return self.barcode.replace(" ", "_")
        else:
            return self.barcode

    def custom_name(self) -> str:
        return "SFK" + self.barcode[:3] + "-" + self.barcode[-3:]
