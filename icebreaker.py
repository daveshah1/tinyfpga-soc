#!/usr/bin/env python3

import argparse
import importlib
import os.path
import struct

from litex.gen import *
# from migen.genlib.io import CRG
from migen import *
from litex.boards.platforms import icebreaker
from litex.build.generic_platform import *

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.spi_flash import SpiFlashSingle


class BaseSoC(SoCCore):
    def __init__(self, platform, **kwargs):
        SoCCore.__init__(self, platform,
            clk_freq=int((1/(platform.default_clk_period))*1000000000),
            cpu_reset_address=0x100000,
            # cpu_reset_address=0x30000,
            integrated_rom_size=0,
            integrated_sram_size=0x2800,
            integrated_main_ram_size=0,
            **kwargs)

        # No user-reset signal, but wait a few cycles before accessing
        # SPI flash.
        reset_timer = Signal(max=1 << 8, reset=(1 << 8) - 1)
        self.sync.por += If(reset_timer != 0, reset_timer.eq(reset_timer - 1))

        self.submodules.crg = CRG(platform.request(platform.default_clk_name), reset_timer > 0)
        self.submodules.spiflash = SpiFlashSingle(platform.request("spiflash"))
        self.register_rom(self.spiflash.bus)

        self.comb += [platform.request("trigger").eq(0)]


def main():
    parser = argparse.ArgumentParser(description="TinyFPGA MiSoC port")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    # Dummy signal for debugging SPI flash usage w/ Logic Analyzer.
    trigger = [
        ("trigger", 0, Pins("PMOD1A:0"))
    ]

    platform = icebreaker.Platform()
    platform.add_extension(trigger)
    # platform.add_extension(tinyfpga_b.serial)
    soc = BaseSoC(platform, **soc_core_argdict(args))
    platform.toolchain.build_template[3] = "icepack -s {build_name}.txt {build_name}.bin"

    # We want a custom lm32_config.v. Since there's no clean way to really
    # remove include paths, let's go ahead and manually modify it.
    lm32_config_paths = list(platform.verilog_include_paths)
    platform.verilog_include_paths.remove(lm32_config_paths[0])
    platform.add_verilog_include_path(".")

    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
