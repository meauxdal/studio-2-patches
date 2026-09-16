# Canonical-download conversion process

## Preservation model

By default, `build.py` scans files beside the script. If a `hagley/`
subdirectory is present beside it, that directory is scanned too. This lets a
standalone copy of the script operate directly beside downloaded files without
a repository checkout, while retaining the repository's convenient layout.
`--source-dir PATH` replaces those defaults with one explicit input directory.

There is one file per archival object, apart from separately preserved
original tape data. Each file retains its canonical Hagley filename and bytes.
Only files directly inside the selected directories are considered;
subdirectories other than the default `hagley/` directory are not traversed.

The pipeline follows four rules:

1. An accession name identifies a possible recipe; it does not prove the
   format.
2. The complete input SHA-256 must match a recorded source identity before any
   conversion occurs.
3. Every split is expressed as an exact file-offset-to-address mapping. Source
   bytes are not discarded merely because a region is not yet understood.
4. Every generated binary has a recorded expected SHA-256. A changed source or
   changed algorithm stops the build rather than producing a plausible-looking
   file.

Output names express the established identity of the data. Address ranges are
documented as transformation evidence, but generic names such as `Lower pages`
or an unresolved Hagley label are not used as the identity of a deliverable.

Each run also writes `SOURCES.sha256`, identifying every accepted primary
input, and `MANIFEST.sha256`, identifying every generated derivative. These
receipts are themselves checked by `build.py --check`.

## Container and image rules

The `.st2` characters in a Hagley filename are archival naming, not a format
declaration. The builder recognizes an ST2 container only when the bytes have
an `RCA2` signature and a structurally valid 256-byte header, block count, page
table, and payload. Flat cartridge derivatives contain only the mapped payload.
Header repairs change the declared block count without changing payload bytes.

Raw absolute images mapped from `$0000` are emitted as `.rom`. Raw cartridge
images mapped at `$0400` are emitted as `.bin`, with a generated ST2 container
when the page mapping is established. Intel HEX text is checksum-verified,
required to be contiguous from address zero, and decoded to absolute ROM bytes.

## Currently implemented transformations

- `ID03_01` and `ID08_01`: split the canonical 2 KiB memory image into the
  shared `$0000-$03FF` resident environment and the distinct `$0400-$07FF`
  program; wrap the latter as four-page ST2.
- `ID04_02`, `ID05_01`, `ID05_02`, `ID12_01`, and `ID17_01`: parse composite
  ST2 objects and emit the identified TV School House I, Space War, Game Pack,
  Numbers, and Speedway + Tag programs and named Game Pack variants.
- `ID07`, `ID08_02`, `ID09_01`, `ID09_02`, and `ID17_02`: recognize the
  RCA2/ST2 structure from the bytes, then extract the mapped four-page payload
  while preserving the canonical source unchanged.
- `ID13_01` and `ID16_02`: extract absolute 2 KiB images and their resident
  `$0000-$03FF` regions.
- `ID14_01`: retain the two-page payload and construct the corrected two-page
  ST2 container.
- `ID33_01`: correct the ST2 block count and extract its complete four-page
  payload.
- `ID33_02`: restore the five trailing zero bytes established by independently
  preserved tape-block data, yielding the identified FRED 1.5 tape save/load
  fragment as one complete page mapped at `$0100`.
- `ID10` and `ID13_02`: retain the established address-zero images with an
  extension that describes how they are loaded.
- `ID16_01`: decode and checksum-check the Intel HEX text into a contiguous
  2 KiB absolute ROM; the result exactly matches the established Snoopy Snipe
  Shoot binary.

## Additional page-aligned identifications

These transformations were established from 256-byte page structure, with
512-byte interpreter/program boundaries checked where applicable:

| Accession | Evidence | Generated identity |
| --- | --- | --- |
| `ID06_01` | complete 2048-byte image differs at only 22 bytes from the established Coin Bowling image | `Coin Bowling (GPL-4 Variant)`; exact Hagley bytes retained as `.arc` |
| `ID06_02` | first seven pages closely match Computer Bowling; the remaining page plus one byte are all zero | `Computer Bowling (FPL-4 Variant)`; exact meaningful 1792-byte region retained |
| `ID15_01` | executable code is followed by the embedded ELIZA-style dialogue beginning “WHAT IS YOUR NAME?” | `Shrink (Word Language Conversation Program)` |
| `ID20_01` | first two pages are a CHIP-8 interpreter variant; payload begins at file `$0200`; program body matches Andrew Modla's Pinball while the captured tail differs | `VIP Pinball (Andrew Modla, Hagley Capture)`; complete 1280-byte post-interpreter capture retained |
| `ID21_02` | complete byte-for-byte match to the established 4096 Bit Picture image | `4096 Bit Picture` |
| `ID26_01_1` | complete byte-for-byte match to the COSMAC VIP 512-byte monitor ROM | `COSMAC VIP Monitor ROM` |
| `ID26_02_2` | complete byte-for-byte match to the established FPL-4 example | `FPL-4 Race Example` |
| `ID27_01_2` | complete byte-for-byte match to the established FEL-1 example | `FEL-1 Example` |
| `ID32_01_2` | after the 512-byte interpreter region, the remaining 1536 bytes exactly match Snoopy COSMAC Picture | `Snoopy COSMAC Picture` |

### Reviewed page-structure findings not yet emitted by `build.py`

The following archival objects have now been analyzed on the same byte- and
page-structure grounds. They remain preserved as canonical sources, but no new
build recipe is implied merely by documenting a supported internal boundary.

| Accession | Canonical source SHA-256 | Structural finding | Current treatment |
| --- | --- | --- | --- |
| `ID03_02` | `84557d922ba84df950f2ec8b36fedb1ab00bd4930027d071f81e88a11800d452` | one 256-byte COSMAC ELF image; native code occupies file `$0000-$003F`, followed by display data at `$0040-$00FF` including the visible `COSMAC` raster | retain the complete page; code and display data form one program image |
| `ID04_01` | `735674bf9323a1672f63d62d60ae54e8734d222fb4cc31de4ccee792bb8c348f` | complete 2048-byte Bowling image; all eight 256-byte pages are distinct and each contains 242-256 nonzero bytes, with no supported internal split | retain the complete 2 KiB image |
| `ID12_02` | `77d1eac8931609006e6233fc632550aa88020b92f00871c36e88c41477e73bbe` | 256-byte 1K memory-test image; execution deliberately enters the `$0080` region, so the upper half is not generic page padding | retain the complete page |
| `ID15_02` | `5d4a08d65a9854cd1056c9f9539b589c4b15bf6a2242107e1b6f1eec25d4323e` | five-page Subject Color image; the driver selects display pages `$0100`, `$0200`, `$0300`, and `$0400`; the all-zero `$0100` page is therefore intentional | retain all 1280 bytes as one memory image |
| `ID31_02` | `9af19f67d50c301e3448a8fdd14bbfc47b57f1681e5293da63c3717b724943b7` | `$0000-$01FF` is the STK-1 language/core and `$0200-$02FF` is its example program/data | document the `$0200` boundary; keep the archival composite intact |
| `ID31_01` | `cadcfd9e01ea5798aa8332ecab2c2f557e2eb5e8d429987040ca1fe04341b8c4` | `$0000-$01FF` is the closely related STK-2 language/core and `$0200-$04FF` is the A/B/C/D example program; the STK-1 and STK-2 cores differ at only 14 bytes | document the `$0200` boundary; keep the archival composite intact |
| `ID32_01_1` | `74e372e858019aa3d8ffe50d49c99aa16f81922b10ec71a5f55dd651485c0434` | the two terminal loops end with branch operands at file `$006E`; `$006F-$00FF` is 145 zero bytes, giving a well-supported 111-byte program extent inside the 256-byte archival page | retain the canonical page; a future program-only derivative may use `$0000-$006E` if added as a guarded recipe |

Emma 02 carries byte-identical copies of `ID12_02`, both STK objects, and the
VIP 1K Memory Test. Its copy of the latter is labelled
`AUD_2464_09_B41_ID32_02_1`, while the Hagley file reviewed here is
`AUD_2464_09_B41_ID32_01_1`. The bytes establish identity; the accession suffix
disagreement is retained as provenance metadata rather than silently normalized.

`ID14_02` and `ID26_02` are still reported as unmapped. `ID14_02` contains one
page of native code labelled “180-List Utility,” but its execution mapping and
independent identity remain unresolved. `ID26_02` contains C80-LANG/PRINT
material, but its precise execution role and useful standalone form likewise
have not been established well enough to emit a finalized derivative.

Any canonical file without a supported recipe is reported as unmapped.
A documented internal boundary is not, by itself, a build recipe: the source
remains unmapped until an output identity and guarded transformation are both
established. Reporting is not rejection; it marks the boundary between a
preserved source and a transformation whose address or execution model has
been sufficiently understood.

## Direct and newly corrected source mappings

| Accession | Canonical source SHA-256 | Operation | Generated data |
| --- | --- | --- | --- |
| `ID03_01` | `60240a06b9baf54257b61ebd97e40ef74b8a295bbc31311cb188cc3e2a712889` | split the raw 2 KiB image at file `$0400` | 1 KiB New Studio 2-5 Game Set BIN/ST2; resident half remains preserved in the source |
| `ID08_01` | `7c134efa56f2cde8c238e83dc3e50efecc91a8c32f44f9ba3fb18d097291568b` | split the raw 2 KiB image at file `$0400` | 1 KiB Biorhythm BIN/ST2; resident half remains preserved in the source |
| `ID10` | `2bba48ca1e49cd48112a4240ad5c5ccce7e12e8d55b09169b591cb0f59099a47` | retain the raw absolute image; its first 512 bytes match the `ID13_02` environment | 2 KiB ROM |
| `ID13_02` | `55484365a66c56327622b66ed77a31bfde7336f3b2a0b53c6f0ba8226f68e1d0` | retain the raw absolute image; its first 1 KiB matches the resident region extracted from `ID13_01` | 2 KiB ROM |
| `ID16_01` | `44db71ad57ba04c5fcdad739c815c28ab0e50c46b3697c1768ef026ab6a41a2e` | validate all Intel HEX record checksums and decode addresses `$0000-$07FF` | 2 KiB ROM with SHA-256 `712c36ff83a23df3c742b9e6d3aa0480bb52b050fe6d52605f5ecf133c59c9db` |

The shared `ID03_01`/`ID08_01` resident region has SHA-256
`c0991752652951775410afa6c3159cd8574d6cb664bac3600a3e65d8c6a3172b`.
Its equality is byte-for-byte and does not depend on either archival title.
