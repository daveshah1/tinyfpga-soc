#!/usr/bin/env python3

import argparse
import importlib
import os.path
import struct

from litex.gen import *
# from migen.genlib.io import CRG
from litex.boards.platforms import tinyfpga_b
from litex.build.generic_platform import *

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *


class BaseSoC(SoCCore):
    def __init__(self, platform, **kwargs):
        SoCCore.__init__(self, platform,
            clk_freq=int((1/(platform.default_clk_period))*1000000000),
            integrated_rom_size=0x400,
            integrated_sram_size=0x2800,
            integrated_main_ram_size=0,
            **kwargs)
        self.submodules.crg = CRG(platform.request(platform.default_clk_name))


# BIOS + RAM + Block RAM used for design is too much. Customize instead.
# Also, `builder = Builder(soc, **builder_argdict(args))
# builder._initialize_rom = _initialize_rom_tinyfpga`
# Doesn't work... why?
class TinyFpgaBuilder(Builder):
    def __init__(self, soc, output_dir=None,
                 compile_software=True, compile_gateware=True,
                 gateware_toolchain_path=None,
                 csr_csv=None):
        Builder.__init__(self, soc, output_dir, compile_software,
            compile_gateware, gateware_toolchain_path, csr_csv)
        self.software_packages = []
        self.add_software_package("loader",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "loader")))

    def _initialize_rom(self):
        bios_file = os.path.join(self.output_dir, "software", "loader",
                                 "loader.bin")
        if self.soc.integrated_rom_size:
            with open(bios_file, "rb") as boot_file:
                boot_data = []
                while True:
                    w = boot_file.read(4)
                    if not w:
                        break
                    boot_data.append(struct.unpack(">I", w)[0])
            self.soc.initialize_rom(boot_data)


def main():
    parser = argparse.ArgumentParser(description="TinyFPGA MiSoC port")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    platform = tinyfpga_b.Platform()
    # platform.add_extension(tinyfpga_b.serial)
    soc = BaseSoC(platform, **soc_core_argdict(args))

    # We want a custom lm32_config.v. Since there's no clean way to really
    # remove include paths, let's go ahead and manually modify it.
    lm32_config_paths = list(platform.verilog_include_paths)
    platform.verilog_include_paths.remove(lm32_config_paths[0])
    platform.add_verilog_include_path(".")

    builder = TinyFpgaBuilder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
