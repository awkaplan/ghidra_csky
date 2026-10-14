# Changelog

Changes in this fork relative to upstream leommxj/ghidra_csky at
[`b4871e7`](https://github.com/leommxj/ghidra_csky/commit/b4871e7f1c3b2e39f73b44dc4316f9a3bb3b0ba6).

## Unreleased

### Fixed

- `andn` (16- and 32-bit) computed NAND `~(x & y)` instead of AND-NOT. Now `rz = rx & ~ry`
  (32-bit, `32b_data.sinc`) and `rz = rz & ~rx` (16-bit, `16b_data.sinc`). The 32-bit body also
  had a stray `=-` (`i32_r_rz =- zext(...)`), which parsed as assignment then unary minus.
- `zext`/`sext rz, rx, msb, lsb` (`32b_data.sinc`): the field mask used `msb` as the width instead
  of `msb - lsb + 1`. `sext()` on a same-size varnode is a plain copy in Sleigh, so `sext` behaved
  as `zext`. Both are now explicit arithmetic.
- `movih` (`32b_data.sinc`): `zext(imm:2 << 16)` shifted inside the 2-byte operand, so every
  `movih` loaded 0 and `movih`-based peripheral accesses decompiled as low-address ghosts
  (`uRam000000NN`). Now `zext(imm:2) << 16`.
- Build failure on Ghidra 12.1.3: two unused imports in `CSKY_ElfRelocationHandler.java`
  referenced classes no longer on the classpath. Removed.
- Release workflow: the third-party unzip action it used no longer exists. Replaced with `unzip`,
  and Ghidra 11.0 / Java 17 / Gradle 8.5 updated to 12.1.3 / Java 21 / Gradle 9.7.1.

### Added

- Privileged instructions in `32b_priv.sinc` (upstream's reserved include for this class) and
  `sync` in `32b_special.sinc`. Previously all of these decoded as bad data and truncated control
  flow in the decompiler.
  - `mfcr rz, cr<rx,0>` / `mtcr rx, cr<rz,0>` read and write the named control register
    (`mfcr r0,PSR`, `mtcr r1,PSR`); index order follows binutils `csky_ctrl_regs`. Only bank 0
    decodes.
  - `psrclr` / `psrset` display flag names (`psrclr ie`) and update the architectural PSR bits
    af=1, fe=4, ie=6, ee=8.
  - `rte` restores PSR from EPSR and returns to EPC; `rfi` restores PSR from FPSR and returns to FPC.
  - `stop`, `wait`, `doze`, `sync` are opaque p-code ops (`cpu_stop`, `cpu_wait`, `cpu_doze`,
    `sync_barrier`).
- 19 control-register slots (`SS0`..`SS4`, `DCSR`, `CWR`, `CFR`, `CR18`, `CR22`..`CR31`) at new
  register offsets from `0x240`, so `mfcr`/`mtcr` can name every `cr<0..31, 0>`. Existing register
  offsets are unchanged.
- Regression suite `tests/` (`run_tests.py`, `cases.toml`): decodes each case with the extension and
  checks register results with Ghidra's p-code emulator. Encodings come from the vendor assembler;
  expected values from the ISA semantics, not from this module.
- CI builds the extension and runs the tests on every push and pull request, and attaches the zip
  to releases. The Sleigh spec is compiled explicitly, so the zip ships a precompiled `csky_v2.sla`.
- `CONTRIBUTING.md`, `AGENTS.md` (`CLAUDE.md` links to it), `LICENSE.md`.

### Changed

- `Instructions.md` moved to `docs/instruction-coverage.md` and regenerated from the Sleigh
  constructors (17 entries were implemented but unchecked).
- README rewritten: status and known limitations, build, test, layout, credits and licensing.
- `extension.properties` description; `.gitignore` drops the upstream author's personal scripts.
