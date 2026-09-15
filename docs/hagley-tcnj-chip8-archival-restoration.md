# Hagley / TCNJ CHIP-8 archival restoration map

## Purpose and scope

This document records two related but distinct parts of the CHIP-8 collection
work:

1. byte-preserving extraction of CHIP-8 programs from Hagley audio-tape
   derivatives that also contain the COSMAC VIP interpreter; and
2. later, explicitly labelled repairs that make selected archival programs
   usable on portable CHIP-8 interpreters.

The distinction is important. An **extracted** image contains unchanged source
bytes from a known address range. A **portable fix** is a derivative whose
changed bytes and rationale are documented in the
[portable CHIP-8 patches repository](https://github.com/meauxdal/chip-8-patches).
A reconstruction is never presented as recovered archival data.

This is the CHIP-8 companion to the
[Studio II/III binary provenance map](hagley-studio-ii-iii-binary-provenance.md).

## The recovered COSMAC VIP interpreter

Hagley accession `AUD_2464_09_B41_ID21_01`, labelled `VIP Lang @0000 CHIP 8`,
is a 512-byte CDP1802 program:

- load address: `$0000-$01FF`
- SHA-1: `8aa634c239004ff041c9adbf9144bd315ab5fc77`
- SHA-256: `699ad707fd9756c10a31c7abbd03b95e28ae04112bd097ab72a62493d358271b`

Its bytes match the two-page CHIP-8 interpreter published at `$0000-$01FF` in
Appendix C of the
[RCA COSMAC VIP Instruction Manual](https://www.bitsavers.org/components/rca/cosmac/COSMAC_VIP_Instruction_Manual_1978.pdf),
including the listing's two printed corrections. It is therefore an
independent archival copy of Joseph Weisbecker's standard COSMAC VIP
interpreter, not evidence of a previously unknown interpreter variant.

The same 512 bytes are the exact prefix of four other Hagley downloads. Those
downloads are complete VIP memory transfers rather than ordinary `.ch8`
payloads:

```text
Hagley Extracted Binary                    COSMAC VIP memory

file $0000  +---------------------------+  $0000
            | standard VIP interpreter  |
file $01FF  +---------------------------+  $01FF

file $0200  +---------------------------+  $0200
            | CHIP-8 program payload    |
            | and captured tail bytes   |
file end    +---------------------------+
```

Removing the common `$0000-$01FF` prefix restores the conventional CHIP-8
file form loaded at `$0200`. `VIP Lang` itself ends at `$01FF` and has no
payload to extract.

## Hagley composite-image extractions

The original files remain unchanged in archival holding. Every extracted file
starts at source offset `$0200`, retains every remaining byte, and was compared
byte-for-byte with the common interpreter before the split.

| Accession and Hagley title | Source | Extracted `$0200` payload | Result |
| --- | ---: | ---: | --- |
| `AUD_2464_09_B41_ID19_01` — Videodraw Chip 8 | 768 bytes; SHA-256 `4412af904170cd2b1496fb5f5f98e339cf71e06813b9c81ff540fd32f10b20bc` | 256 bytes; SHA-256 `c3d5e465fdba6c275ab02fbef114fa4f69f9cac26edddc10d05326e195d8a9be` | exact archival payload retained; source for the portable Videodraw fix |
| `AUD_2464_09_B41_ID19_02` — VIP Kaleidoscope Chip 8 | 768 bytes; SHA-256 `84b2c0ebb32d2bdfac28a5ed06ecf82ddf5d5a9449486eeff0a5fc0be2ebb374` | 256 bytes; SHA-256 `2a8e816793e4de296453cb2e16f3948d6caf24ad708b341c5c23facba4622a1e` | promoted as the labelled Hagley extraction |
| `AUD_2464_09_B41_ID23_01` — Tic-Tac-Toe (CHIP 8) 4 Pages @0000 | 1024 bytes; SHA-256 `642210831052150fed87c30538811cc84b55f1e4350bb62bd89fcb977d265186` | 512 bytes; SHA-256 `22d6c108415ff9ed86c7c7fcdcf29563e923f954e06ac938a171d593964072d6` | preserved capture; its first 470 bytes match the manual-sized Tick-Tack-Toe source used for the portable fix |
| `AUD_2464_09_B41_ID23_02` — Private Eye Target Practice (CHIP 8) 4 Pages | 1024 bytes; SHA-256 `c9cb2a320f511da6cbd808645cf7ca428c26ef1eb74b2d31d66c0d8d3aae1a7e` | 512 bytes; SHA-256 `7961dd3164f74368e6ec8bcf8862ac383ca303eacb4172d2b90fe9917e03bb96` | exact match for the existing Private Eye Target Practice payload; labelled extraction also retained |

The full 256-byte Kaleidoscope payload is retained because that is what the
tape derivative preserves. Its first 122 bytes exactly match the shorter
Joseph Weisbecker Kaleidoscope image in the collection; the remaining captured
bytes are not discarded or silently treated as part of that shorter image.
Likewise, the 512-byte Tic-Tac-Toe capture is preserved even though only its
first 470 bytes match the manual-sized program used by the patch project.

The extraction log, source images, and byte-preserving payloads should be kept
together in an accession-oriented preservation tree. Playable extractions must
remain explicitly labelled as derivatives.

## Additional 512-byte-boundary extractions

Two later-reviewed captures also divide at file offset `$0200`, but their
resident interpreter regions are variants rather than byte-identical copies of
the standard interpreter above. Their payload boundary is independently
supported by the program comparisons.

| Accession | Source layout | Result |
| --- | --- | --- |
| `AUD_2464_09_B41_ID20_01` — VIP Pinball | 1792-byte capture; first 512 bytes are a CHIP-8 interpreter variant differing at three offsets from the common image; payload begins at `$0200` | retain all 1280 post-interpreter bytes as `VIP Pinball (Andrew Modla, Hagley Capture)`; the program body agrees with the established Andrew Modla image while Hagley's captured tail is deliberately retained |
| `AUD_2464_09_B41_ID32_01_2` — Snoopy COSMAC picture | 2048-byte capture; first 512 bytes are the resident interpreter region | the 1536 bytes at file `$0200-$07FF` exactly match the established `Snoopy COSMAC Picture` hybrid |

These are page-aligned extractions, not claims that every byte before `$0200`
matches one canonical interpreter revision.

## Portable restoration ledger

Some early programs use COSMAC VIP behavior that a platform-neutral CHIP-8
interpreter cannot reproduce: `0NNN` calls into CDP1802 code, direct access to
VIP display RAM, original shift semantics, or assumptions about uninitialised
memory. The patch project preserves the accepted original beside a guarded
builder, a validator, and a technical note. The resulting files are named
`portable fix` so they cannot be mistaken for primary-source images.
The hashes below identify the canonical outputs of those guarded builders.

| Title | Source and restoration class | Result |
| --- | --- | --- |
| Bingo | TCNJ `S.572.2, 3`; replaces six classes of native VIP service while retaining game state and display behavior in CHIP-8 code | 1536-byte portable fix; SHA-256 `d261441ae0e9241cf43cf33f6947e55ec7e9c9c038eb46ebff0668aa0433f5fb` |
| Clock Program | common 280-byte image; replaces a native timing loop with a 60-tick CHIP-8 delay-timer interval | 280-byte portable fix; SHA-256 `bf2d6d3bdcaefa4997ac81d40790adccb58be5c264b917b8f6a3c355123d98a7` |
| Craps | common 192-byte image; reconstructs a missing seven-byte frame sprite whose address and geometry are fixed by the program | 247-byte reconstruction; SHA-256 `2dee82081ef51e77187ff83d931288f2ec3c732b382f7c43ed068b4809ae735a` |
| Keypad Test | common 114-byte image; makes four shifts explicit so VIP and modern shift conventions agree | 114-byte portable fix; SHA-256 `4132032f1d3874c8b6ad7728b1e402ba1b6330db1f775a5e858ae3f9599a6a23` |
| Tick-Tack-Toe | 470-byte manual-sized image, corroborated by the first 470 bytes of Hagley `ID23_01`; replaces a native board-clear service | 490-byte portable fix; SHA-256 `b54cd3243b58499ad747f7b1e46e377d38d3f9470e1a50c74c18034dcfb3fcad` |
| Videodraw | exact 256-byte Hagley `ID19_01` extraction; removes one native display-page call and makes coordinate wrapping explicit | 256-byte portable fix; SHA-256 `2e2f85723f85786b668f37e7989b743f4f7f75dae89e098b714c9f8ba51ba1be` |
| Wipe Off | common 206-byte image; restores the manual's documented 20-ball constant, corroborated by the intact portion of TCNJ `S.572.2` | 206-byte preservation fix; SHA-256 `3e5e87255c96369e41a16499b47229b973cfdfc2972d371f4a4f725e52c50412` |
| Pinball | two identical 1536-byte images matching Andrew Modla's VIP manual listing; native display services were investigated but not translated | no derivative produced; source SHA-256 `b69111849cf95731d18dfc0b56cb9543ea835105516bb7e348afa1910d0e6af1` |

The detailed evidence is maintained with the builders:

- [Bingo](https://github.com/meauxdal/chip-8-patches/blob/main/docs/bingo.md)
- [Clock Program](https://github.com/meauxdal/chip-8-patches/blob/main/docs/clock-program.md)
- [Craps](https://github.com/meauxdal/chip-8-patches/blob/main/docs/craps.md)
- [Keypad Test](https://github.com/meauxdal/chip-8-patches/blob/main/docs/keypad-test.md)
- [Tick-Tack-Toe](https://github.com/meauxdal/chip-8-patches/blob/main/docs/tick-tack-toe.md)
- [Videodraw](https://github.com/meauxdal/chip-8-patches/blob/main/docs/videodraw.md)
- [Wipe Off](https://github.com/meauxdal/chip-8-patches/blob/main/docs/wipe-off.md)
- [Pinball investigation](https://github.com/meauxdal/chip-8-patches/blob/main/docs/pinball.md)

## Preservation and verification rules

- Hagley and TCNJ source captures remain unchanged.
- The four Hagley composite splits remove exactly the verified interpreter
  prefix; the interpreter-only `ID21_01` object produces no payload.
- Extracted payloads retain their complete post-`$01FF` byte range, including
  capture tails whose purpose is not established.
- Hashes identify exact files. A title or visual resemblance is not used as a
  substitute for byte equality.
- Portable fixes are derived files. Builders guard the accepted source hash
  and each intended byte replacement; validators target the repaired failure
  class.
- The Craps frame is explicitly a reconstruction from program geometry, not a
  recovered byte sequence.
- Pinball remains an investigated original because no proportionate portable
  translation was completed.
- Passing a validator establishes the documented software transformation; it
  is not a claim of complete COSMAC VIP hardware validation.
