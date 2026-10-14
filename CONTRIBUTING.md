# Contributing

This file is for people and AI coding agents working on the C-SKY v2 Sleigh spec.

## Prerequisites

- Ghidra 12.1.3 (PUBLIC build); set `GHIDRA_INSTALL_DIR` to its directory
- JDK 21 and Gradle 9.7.1 (full build only)
- Python 3.11+ with `pyghidra` (3.1.0 verified), for the tests
- For new test encodings: the C-SKY GNU toolchain (`csky-elfabiv2-as`, `csky-elfabiv2-objdump`)

## Fast loop

For a change to the Sleigh spec, without a full Gradle build:

1. Edit a `.sinc` file under `CSKY/data/languages/`.
2. Compile the spec: `$GHIDRA_INSTALL_DIR/support/sleigh CSKY/data/languages/csky_v2.slaspec`
   (`ERROR` lines mean failure; pre-existing WARN lines are expected).
3. Copy the language files into the installed extension:
   `cp CSKY/data/languages/* $GHIDRA_INSTALL_DIR/Ghidra/Extensions/CSKY/data/languages/`
4. Run the tests: `GHIDRA_INSTALL_DIR=... python tests/run_tests.py`

Run a full Gradle build before opening a pull request (see README.md, Build).

## Where things live

- `csky_v2.sinc`: register definitions, bit ranges (`psr_cf`), macros. Included by `csky_v2.slaspec`.
- `csky_v2.slaspec`: top-level spec. Includes `csky_v2.sinc`, `16b.sinc`, `32b.sinc`. Keeps
  `float.sinc` commented out.
- `16b.sinc`: 16-bit token and include hub. `16b_data.sinc`, `16b_branch.sinc`, `16b_memory.sinc`.
- `32b.sinc`: 32-bit token (`ins32`), field definitions, operand attachments, and the include hub.
- `32b_data.sinc`: arithmetic, logic, shifts, `zext`/`sext`, `movi`/`movih`, and so on.
- `32b_branch.sinc`: `b*`, `jsr`, `rts`, `bsr`, and jumps.
- `32b_memory.sinc`: immediate-offset, register-offset, vector and multi-register loads and stores.
- `32b_priv.sinc`: `mfcr`, `mtcr`, `psrclr`, `psrset`, `rte`, `rfi`, `stop`, `wait`, `doze`.
- `32b_special.sinc`: `trap` and `sync`.
- `float.sinc` is not built.
- `CSKY/src/main/java/.../CSKY_ElfRelocationHandler.java` and `CSKY_ElfRelocationConstants.java`:
  ELF relocations. These are the only Java sources in the repository.

## Conventions

- **Token bit numbering.** In `32b.sinc` a 32-bit instruction is two little-endian halfwords stored
  high halfword first, so the token field positions are halfword-swapped. Each field has a trailing
  comment with the real ISA bit range, for example `i32_r_rx = (0,4) #(16,20)`. Reason in the
  commented (real) numbering, and cite the real bits when you write a new field.
- **Encodings** come from the vendor assembler (`csky-elfabiv2-as -mcpu=ck803`, then `objdump -d`).
  Do not infer an encoding from this module's own output.
- **Semantics** come from the ISA manual or from T-Head's QEMU `target/csky`. Do not derive them
  from this module.
- **Every semantic fix gets a test case** in `tests/cases.toml`. Its expected values must be
  independent of this module, and the case must fail before the fix.
- **Sleigh `sext()` and `zext()` change varnode size only.** To extend a bit field inside a value of
  the same size, use explicit arithmetic (see the `zext`/`sext` rules in `32b_data.sinc`). Shift
  after widening: `zext(imm:2) << 16`, not `zext(imm:2 << 16)`.
- **Comments** are short and describe semantics or encoding. History goes in CHANGELOG.md and in
  commit messages.
- **Indentation** is 4 spaces in new code. Do not reformat existing upstream lines; this keeps the
  diff against upstream small.
- **Register offsets** in `csky_v2.sinc` must not move. Saved Ghidra programs depend on them. Add new
  registers at new offsets.

## Adding a test case

Each case in `tests/cases.toml` is one instruction word, as `objdump -d` prints it:

```toml
[[case]]
hex = "c4a42043"   # andn r3, r4, r5
asm = "andn r3,r4,r5"          # optional: expected disassembly text
in  = { r4 = 0xF0F0FFFF, r5 = 0x0000FF00 }   # optional: register inputs
out = { r3 = 0xF0F000FF }      # optional: expected registers after one step; "pc" = next PC
```

- `hex` is 4 hex digits (16-bit) or 8 hex digits (32-bit).
- Put the encoding's origin in the comment, and the `csky-elfabiv2-as` source line if you can.
- Use the header comment at the top of `tests/cases.toml` as the field reference.
