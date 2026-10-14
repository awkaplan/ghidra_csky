# AGENTS.md

This repository is a Ghidra processor module (Sleigh spec plus one Java relocation handler) for the
C-SKY v2 ISA, used by CK8xx cores such as the CK803S. It is a fork of leommxj/ghidra_csky.

Read [CONTRIBUTING.md](CONTRIBUTING.md) first. It has the development loop, the file layout and the
conventions.

## Rules most likely to be violated

1. **Bit numbering.** `32b.sinc` stores 32-bit instructions as halfword-swapped tokens. Reason in the
   real ISA bit numbers in the trailing comments, not in the token's own field positions.
2. **Source independence.** Encodings come from `csky-elfabiv2-as -mcpu=ck803` and `objdump -d`.
   Semantics come from the ISA manual or T-Head QEMU `target/csky`. Never derive an expected value
   from this module's own output.
3. **One test per fix.** Every semantic fix needs a case in `tests/cases.toml` that fails before the
   fix.
4. **No reformatting of upstream lines.** Keep the diff against upstream small. New code uses 4-space
   indentation.
5. **Do not move register offsets** in `CSKY/data/languages/csky_v2.sinc`. Add new registers at new
   offsets.

## Commands

```sh
# Sleigh-only compile check (no Gradle)
$GHIDRA_INSTALL_DIR/support/sleigh CSKY/data/languages/csky_v2.slaspec

# Full extension build (Ghidra 12.1.3, JDK 21, Gradle 9.7.1)
cd CSKY && gradle -PGHIDRA_INSTALL_DIR=$GHIDRA_INSTALL_DIR

# Regression tests (extension must be installed in Ghidra; needs pyghidra)
GHIDRA_INSTALL_DIR=$GHIDRA_INSTALL_DIR python tests/run_tests.py
```

## Where things are

- Instruction tests: `tests/cases.toml` (format in its header comment), runner `tests/run_tests.py`.
- Instruction coverage checklist: `docs/instruction-coverage.md`.
- Change history: `CHANGELOG.md`.
