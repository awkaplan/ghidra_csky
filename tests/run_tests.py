#!/usr/bin/env python3
"""Regression tests for the C-SKY Sleigh spec.

Each case in cases.toml is one instruction, given as the word `objdump -d` prints for it. The
runner decodes it with the installed CSKY extension, checks the disassembly text, and optionally
runs it through Ghidra's p-code emulator to check register values.

Requires the pyghidra package and GHIDRA_INSTALL_DIR pointing at a Ghidra install that has this
extension installed. Usage:

    python tests/run_tests.py [path/to/cases.toml]

Exits non-zero if any case fails.
"""

import sys
import tomllib
from pathlib import Path

import pyghidra

LANGUAGE_ID = "CSKY_V2:LE:32:default"
LOAD_ADDRESS = 0x1000
DEFAULT_CASES = Path(__file__).with_name("cases.toml")


def encode(word_hex: str) -> bytes:
    """Turn an objdump instruction word into memory bytes.

    32-bit instructions are stored as two little-endian halfwords, high halfword first.
    """
    word = int(word_hex, 16)
    if len(word_hex) == 4:
        return word.to_bytes(2, "little")
    if len(word_hex) == 8:
        return (word >> 16).to_bytes(2, "little") + (word & 0xFFFF).to_bytes(2, "little")
    raise ValueError(f"expected 4 or 8 hex digits, got {word_hex!r}")


class Harness:
    """Decodes and emulates single instructions in a throwaway in-memory program."""

    def __init__(self):
        pyghidra.start()
        # Ghidra classes are importable only after the JVM is up.
        from java.lang import Object
        from ghidra.app.cmd.disassemble import DisassembleCommand
        from ghidra.app.emulator import EmulatorHelper
        from ghidra.program.database import ProgramDB
        from ghidra.program.model.address import AddressSet
        from ghidra.program.model.lang import LanguageID
        from ghidra.program.util import DefaultLanguageService
        from ghidra.util.task import TaskMonitor

        self.Object = Object
        self.DisassembleCommand = DisassembleCommand
        self.EmulatorHelper = EmulatorHelper
        self.ProgramDB = ProgramDB
        self.AddressSet = AddressSet
        self.monitor = TaskMonitor.DUMMY
        self.language = DefaultLanguageService.getLanguageService().getLanguage(
            LanguageID(LANGUAGE_ID))

    def run(self, case):
        """Return (disassembly text or None, list of failure messages)."""
        consumer = self.Object()
        program = self.ProgramDB(
            "test", self.language, self.language.getDefaultCompilerSpec(), consumer)
        try:
            instruction = self._load(program, encode(case["hex"]))
            if instruction is None:
                return None, ["does not decode"]

            text = str(instruction)
            errors = []
            if "asm" in case and text != case["asm"]:
                errors.append(f"asm: got {text!r}, expected {case['asm']!r}")
            if "out" in case:
                errors += self._emulate(program, case.get("in", {}), case["out"])
            return text, errors
        finally:
            program.release(consumer)

    def _load(self, program, data):
        tx = program.startTransaction("load")
        try:
            addr = program.getAddressFactory().getDefaultAddressSpace().getAddress(LOAD_ADDRESS)
            memory = program.getMemory()
            memory.createInitializedBlock("code", addr, len(data), 0, self.monitor, False)
            memory.setBytes(addr, data)
            self.DisassembleCommand(addr, self.AddressSet(addr), False).applyTo(
                program, self.monitor)
        finally:
            program.endTransaction(tx, True)
        return program.getListing().getInstructionAt(addr)

    def _emulate(self, program, inputs, expected):
        emu = self.EmulatorHelper(program)
        try:
            for reg, value in inputs.items():
                emu.writeRegister(reg, value)
            emu.writeRegister(emu.getPCRegister(), LOAD_ADDRESS)

            errors = []
            if not emu.step(self.monitor):
                errors.append(f"emulation failed: {emu.getLastError()}")
            for reg, want in expected.items():
                if reg == "pc":
                    got = emu.getExecutionAddress().getOffset()
                else:
                    got = emu.readRegister(reg).longValue() & 0xFFFFFFFF
                if got != want:
                    errors.append(f"{reg}: got {got:#x}, expected {want:#x}")
            return errors
        finally:
            emu.dispose()


def main(argv):
    cases_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_CASES
    cases = tomllib.loads(cases_path.read_text())["case"]
    harness = Harness()

    failures = 0
    for case in cases:
        try:
            text, errors = harness.run(case)
        except Exception as exc:  # a Java exception in one case should not stop the run
            text, errors = None, [f"exception: {exc}"]
        print(f"{'FAIL' if errors else 'ok  '} {case['hex']:<8} {text or ''}")
        for error in errors:
            print(f"       {error}")
        failures += bool(errors)

    print(f"\n{len(cases) - failures}/{len(cases)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
