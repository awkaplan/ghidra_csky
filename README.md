# Ghidra Processor Module for C-SKY v2

A Ghidra processor module (Sleigh spec plus a small ELF relocation handler) for the C-SKY v2 ISA,
used by CK8xx cores such as the CK803S. Language id: `CSKY_V2:LE:32:default`.

This repository is a fork of [leommxj/ghidra_csky](https://github.com/leommxj/ghidra_csky). It adds
correctness fixes, privileged-instruction support, and a regression test suite. The fixes were
found while reverse-engineering Baofeng DM-32UV radio firmware (CK803S core). The fork's changes
are listed in [CHANGELOG.md](CHANGELOG.md).

## Status

- Targets Ghidra 12.1.3 on Java 21. Other Ghidra versions are untested.
- The integer ISA is partially implemented. See [docs/instruction-coverage.md](docs/instruction-coverage.md).
- Floating point is not built. `float.sinc` is excluded: its `@include` is commented out in
  `csky_v2.slaspec`.
- `mfcr`/`mtcr` decode only control-register bank 0 (`cr<n,0>`). Other banks (sel != 0) do not
  decode.
- The carry flag `psr_cf` is modelled at PSR bit 31. Architecturally it is bit 0; see the comment in
  `CSKY/data/languages/csky_v2.sinc`. A whole-PSR value read with `mfcr` shows C in the S position.
- `trap`, `stop`, `wait`, `doze` and `sync` are opaque p-code operations (`trap_exception`,
  `cpu_stop`, `cpu_wait`, `cpu_doze`, `sync_barrier`).
- The ELF relocation handler extends a constructor that Ghidra 12 marks deprecated for removal; it
  builds on 12.1.3 but will need porting to `AbstractElfRelocationHandler` for a later Ghidra.

## Install

The fork has no GitHub release yet. Either build from source (below), or download the `extension`
artifact from a successful run on the Actions tab. Then install it into Ghidra:

1. Start Ghidra and open `File -> Install Extensions...`.
2. Press `+` and select `ghidra_12.1.3_PUBLIC_<YYYYMMDD>_CSKY.zip`.
3. Press `OK` and restart Ghidra.

## Build

Prerequisites:

- Ghidra 12.1.3 (PUBLIC build), with `GHIDRA_INSTALL_DIR` pointing at it
- JDK 21
- Gradle 9.7.1

```sh
cd CSKY
gradle -PGHIDRA_INSTALL_DIR=/path/to/ghidra_12.1.3_PUBLIC
```

The extension is written to `CSKY/dist/ghidra_12.1.3_PUBLIC_<YYYYMMDD>_CSKY.zip`.

For a fast check of the Sleigh spec alone, without Gradle:

```sh
$GHIDRA_INSTALL_DIR/support/sleigh CSKY/data/languages/csky_v2.slaspec
```

This writes `csky_v2.sla`. Pre-existing WARN lines are expected; an `ERROR` line means failure.

## Test

`tests/run_tests.py` runs each case in `tests/cases.toml`. Each case is one instruction word, as
`objdump -d` prints it. The runner checks Ghidra's disassembly text and, where a case gives expected
registers, emulates one step with Ghidra's p-code emulator and checks the resulting register values.

It needs the extension installed in Ghidra (see Install) and the `pyghidra` package (3.1.0 verified):

```sh
pip install pyghidra
GHIDRA_INSTALL_DIR=/path/to/ghidra_12.1.3_PUBLIC python tests/run_tests.py
```

23 of 23 cases pass on this fork; 22 of 23 fail against the unmodified upstream spec. See
[CONTRIBUTING.md](CONTRIBUTING.md) for how to add cases.

## Repository layout

```
README.md                    this file
CHANGELOG.md                 changes in this fork relative to upstream
CONTRIBUTING.md              development loop and conventions (people and AI agents)
AGENTS.md                    short entry point for AI coding agents (CLAUDE.md links here)
LICENSE.md                   licence for this fork's own changes; upstream is not licensed
docs/instruction-coverage.md implemented and unimplemented instruction checklist
tests/run_tests.py           pyghidra regression runner
tests/cases.toml             instruction test cases
.github/workflows/build.yml  CI: build + test on push and pull request; attaches the zip to releases
CSKY/                        the Ghidra extension: Module.manifest, build.gradle,
                             extension.properties, data/languages/*.sinc and *.slaspec,
                             src/main/java relocation handler
```

## Credits and licensing

This repository is a fork of **[leommxj/ghidra_csky](https://github.com/leommxj/ghidra_csky)**,
based on upstream commit
[`b4871e7f1c3b2e39f73b44dc4316f9a3bb3b0ba6`](https://github.com/leommxj/ghidra_csky/commit/b4871e7f1c3b2e39f73b44dc4316f9a3bb3b0ba6)
("Change goto to call for jsri", 2026-07-08). Nearly all of the processor module is upstream work.

**Upstream authors** (from the upstream git history):

- **leommxj** (Leopold) — original author and maintainer of the module
- **"1234"** — the November 2024 series of Sleigh fixes and new instructions (INS32, ABS32,
  size hints, ZEXT/SEXT refactor, push/pop order, ...), merged via upstream PR #4
- **deniska-iriska** — CMPLTI typo fix, upstream PR #4
- **DUO-1337** — `declt`/`lrs.x`, the `i32_imm18_imm` fix, and the `R_CSKY_RELATIVE`/`GLOB_DAT`/
  `JUMP_SLOT` relocations, upstream PR #6

`CSKY/build.gradle` is Ghidra's standard extension build script and carries Ghidra's own
Apache-2.0 header (NSA / Ghidra project); `CSKY/extension.properties` keeps `author=leommxj`.

**Licensing status.** The upstream repository carries **no license file**, and none of its source
files carries a license header (other than the Ghidra build script above). This fork therefore
grants **no license for the upstream code** — publishing this fork does not change the upstream
authors' rights in their work. This fork's own changes, listed in [CHANGELOG.md](CHANGELOG.md),
are licensed under the
[PolyForm Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0).
The full terms and the scope of the licence are in [LICENSE.md](LICENSE.md). The required notice is:

    Required Notice: Copyright 2026 Alex Kaplan (https://github.com/awkaplan/ghidra_csky)

That licence covers only the fork's own changes. It cannot grant rights in the upstream code they
modify.
