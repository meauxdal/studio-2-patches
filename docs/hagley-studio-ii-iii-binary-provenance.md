# Hagley / TCNJ Studio II and Studio III binary provenance map

## Purpose and scope

This document shows how the Studio II/III-family audio-tape accessions became
the files in the current RCA Studio II collection:

```text
archival audio tape
        |
        v
Hagley “Extracted Binary” download
        |
        +--> identify its real format
        +--> map file offsets to machine addresses
        +--> split concatenated programs where the bytes support a boundary
        +--> repair container metadata without changing program bytes
        +--> use an extension that describes the resulting file
        |
        v
current BIN / ST2 file, or a clearly labelled non-standalone fragment
```

The scope covers archival material associated with the Studio II and Studio III
family implemented by this core. TCNJ/Sarnoff and Emma 02 copies are included
when they are a source or when their bytes corroborate an identity or split.
Studio IV and coin-arcade accessions remain outside the map. CHIP-8 extraction
and restoration are covered by the companion
[CHIP-8 archival restoration map](hagley-tcnj-chip8-archival-restoration.md).
The item
catalogued as Studio II-TV Tennis Side 02 is retained only to show why binary
analysis reclassified it as FRED software and moved it out of the playable set.

All offsets and identities below are reproducible with
`tools/verify-hagley-studio-ii-iii-provenance.py`.

## Reading the maps

- **Extracted Binary** is Hagley's label for the derivative of the audio tape.
  It is a provenance stage, not a claim that the downloaded file is a flat
  `.bin`; several downloads are actually RCA2/ST2 containers.
- **File offset** is the location inside the downloaded Hagley Extracted
  Binary.
- **Machine address** is where the bytes belong in the machine's address
  space.
- An `RCA2` header is an ST2 container header, even when the downloaded
  filename ends in `.bin`.
- ST2 header byte `$0004` declares the total number of 256-byte blocks,
  including the header itself.
- ST2 header bytes beginning at `$0040` give the destination page for each
  256-byte data block. Page `$04` means address `$0400`, page `$05` means
  `$0500`, and so on.

## Overview

| Hagley accession | Hagley Extracted Binary | What the download really is | Result |
| --- | --- | --- | --- |
| `AUD_2464_09_B41_ID03_01` | New Studio 2-5 Game Set | raw 1024-byte cartridge | one BIN at `$0400`; one ST2 wrapper |
| `AUD_2464_09_B41_ID04_02` | Studio 2 Quiz | complete ST2 misnamed `.bin`; released TV School House I plus unrelated upper pages | move the composite to holding; use the released lower program and Game Pack upper variant separately |
| `AUD_2464_09_B41_ID05_01` | 180 Space War (S2-A3) | complete ST2 misnamed `.bin`; Space War 2 plus unrelated upper pages | move the composite to holding; promote culled Space War 2; retract the unsupported Space War 3 identity |
| `AUD_2464_09_B41_ID05_02` / TCNJ `S.572.33`, `S.572.46` | Basic Videomate / Game Pack | two ST2s with different title fields and one exact payload | retain both provenance headers; extract one canonical BIN |
| `AUD_2464_09_B41_ID07` | Baseball-2K | four-page ST2 | extract one BIN at `$0400` |
| `AUD_2464_09_B41_ID08_01` | Biorhythm | four-page ST2 | extract one BIN at `$0400` |
| `AUD_2464_09_B41_ID08_02` | Secret Number | raw 1024-byte cartridge plus matching ST2 | one BIN at `$0400`; retain ST2 |
| `AUD_2464_09_B41_ID09_01` | Color Demo | raw 1024-byte cartridge plus matching ST2 | one Studio III-family BIN at `$0400`; retain ST2 |
| `AUD_2464_09_B41_ID09_02` | Colors Stars and Trek | raw 1024-byte cartridge plus matching ST2 | one Studio III-family BIN at `$0400`; retain ST2 |
| `AUD_2464_09_B41_ID12_01` | Numbers | raw 1024-byte composite plus matching ST2 | move the composite to holding; promote the culled two-page Numbers program |
| `AUD_2464_09_B41_ID13_01` | Paul's Printer | eight-page ST2 misnamed `.bin` | extract one absolute 2 KiB ROM at `$0000` |
| `AUD_2464_09_B41_ID14_01` | Print Snoopy | raw 512-byte cartridge; companion ST2 count is wrong | retain BIN; repair one ST2 header byte |
| `AUD_2464_09_B41_ID16_02` | Color Runs | absolute 2 KiB image plus matching ST2 | retain complete ROM; additionally extract resident interpreter `$0000-$03FF` |
| `AUD_2464_09_B41_ID17_01` | Tag-Race | four-page ST2; released Speedway + Tag plus unrelated upper pages | move the composite to holding; use the released lower program and Game Pack upper variant separately |
| `AUD_2464_09_B41_ID17_02` | Gunfight | four-page ST2 | extract one BIN at `$0400` |
| `AUD_2464_09_B41_ID33_01` | Studio II-TV Tennis (ANDY) | complete ST2 misnamed `.bin`; header count is wrong | repair one header byte; extract complete 1024-byte BIN |
| `AUD_2464_09_B41_ID33_02` | Studio II-TV Tennis — Unidentified Side 02 | 251 raw bytes; companion ST2 preserves the complete 256-byte page | restore five evidenced trailing zeros; reclassify as a FRED 1.5 fragment |
| TCNJ `S.572.11B` | ST3CTA Tester 3 | sparse twelve-page ST2 | retain ST2 and a block-concatenated BIN; preserve three address regions |

---

## `AUD_2464_09_B41_ID03_01` — New Studio 2-5 Game Set

### Hagley source

`New Studio 2-5 Game Set [AUD_2464_09_B41_ID03_01].bin`

- Download size: `$0400` / 1024 bytes
- SHA-256: `f7d72fa0ef3215aebd517bffebd0ebb3dbde0acfafe816ce55ed80d71da33a85`
- Actual format: raw cartridge bytes
- Address evidence: the matching ST2 has page table `04 05 06 07`

### Address map

```text
Hagley Extracted Binary                         Studio II memory

file $0000  +--------------------------------+  $0400  NEW BINARY START
            |                                |         New Studio 2-5 Game Set
            | complete 1024-byte program     |
            |                                |
file $03FF  +--------------------------------+  $07FF  END
```

### Resulting files

```text
Hagley Extracted Binary, file $0000-$03FF
    |
    +--> New Studio 2-5 Game Set [AUD_2464_09_B41_ID03_01].bin
    |       raw cartridge; load at $0400-$07FF; bytes unchanged
    |
    +--> New Studio 2-5 Game Set [AUD_2464_09_B41_ID03_01].st2
            same bytes, preceded by an RCA2 header mapping pages $04-$07
```

The BIN needs no de-concatenation or byte repair. The ST2 is a container for the
same program, not a second binary version.

---

## `AUD_2464_09_B41_ID04_02` — Studio 2 Quiz

### Hagley source

`Studio 2 Quiz (B2-F4) [AUD_2464_09_B41_ID04_02].bin`

- Download size: `$0500` / 1280 bytes
- SHA-256: `53cd4aba4e2ed136face90cf109c17ab9e695610de40845566b936b9dec4fab2`
- Actual format: a complete ST2 container, despite the `.bin` extension
- Header: valid count `$05`; page table `04 05 06 07`

### Address map

```text
Hagley Extracted Binary                         Studio II memory

file $0000  +--------------------------------+          RCA2/ST2 HEADER
            | 256-byte container header      |          (not program data)
file $00FF  +--------------------------------+

file $0100  +--------------------------------+  $0400  NEW BINARY START
            |                                |         TV School House I
            | exact released 512-byte ROM    |
file $02FF  +--------------------------------+  $05FF  END OF RELEASED ROM

file $0300  +--------------------------------+  $0600  UNRELATED REGION START
            | Game Pack upper-page variant   |         exact same $0600-$07FF
            | also found in Tag-Race dump    |         bytes as Tag-Race
file $04FF  +--------------------------------+  $07FF  END
```

### Resulting files

```text
Hagley file $0000-$04FF
    +--> s2-holding/.../Archival composites/Quiz ID04_02/
            exact archival container and flat composite retained outside the
            playable prototype set

Hagley file $0100-$02FF
    +--> existing released TV School House I cartridge
            exact match; no duplicate prototype entry

Hagley file $0300-$04FF
    +--> Game Pack Quiz/Tag-Race upper-page component and test assembly
```

The first 512 program bytes are exactly the released `TV School House I`
cartridge. The final 512 bytes are preserved as part of the archival object,
but the byte and code evidence below identifies them as a variant of Game
Pack's upper pages, not as Quiz code.

Flat BIN SHA-256:
`f99591c280e9f29ff98889e87d23306bfa980e730d367e2307dc0a55fcee4110`.

---

## `AUD_2464_09_B41_ID05_01` — 180 Space War (S2-A3)

### Hagley source

`180 Space War (S2-A3) 512 Bytes [AUD_2464_09_B41_ID05_01].bin`

- Download size: `$0500` / 1280 bytes
- SHA-256: `088d37168dbefe863acb0fabe999c837abd371b92d0a9430bda5ca3672f93051`
- Actual format: a complete ST2 container, despite the `.bin` extension
- Header: valid count `$05`; page table `04 05 06 07`
- The archival “512 Bytes” label describes only one internal part; the
  Extracted Binary actually contains 1024 program bytes.

### Address map

```text
Hagley Extracted Binary                         Studio II memory

file $0000  +--------------------------------+          RCA2/ST2 HEADER
            | 256-byte container header      |          (not program data)
file $00FF  +--------------------------------+

file $0100  +--------------------------------+  $0400  NEW BINARY START
            |                                |         Space War 2
            | exact 512-byte program         |
file $02FF  +--------------------------------+  $05FF  END SPACE WAR 2

file $0300  +--------------------------------+  $0600  UNRELATED REGION START
            | Game Pack upper-page variant   |         later copied under the
            |                                |         unsupported Space War 3 name
file $04FF  +--------------------------------+  $07FF  END
```

### Resulting files

```text
Hagley file $0000-$04FF
    +--> s2-holding/.../Archival composites/Space War ID05_01/
            legacy-named archival composite; exact source bytes retained

Hagley file $0100-$02FF
    +--> Space War 2 [AUD_2464_09_B41_ID05_01].bin + .st2
            canonical two-page program mapped at $0400-$05FF

Hagley file $0300-$04FF
    +--> legacy `Space War 3` fragment copy
            preservation copy only; the title is not supported by its code
```

The Emma 02 collection carries the same two 512-byte regions under the names
`spacewar-2.st2` and `spacewar-3.st2`. That later filename establishes neither
authorship nor program identity. The first region is an exact Space War 2
program. The second differs at only six offsets from the Quiz/Tag-Race Game
Pack upper-page variant described below and retains its calls into Game Pack's
lower pages. It therefore must not be identified as Space War 3 or presented
as an independent cartridge. The four-page ST2 remains useful only as the
exact archival composite.

The culled Space War 2 BIN has SHA-256
`fd26fa0e1c4a3a611684088175170b5a1f8b3dac5a0c58306ecfc98c407c1703`.
Its generated ST2 has SHA-256
`8bd39731a0c7f64ba4612755ea2def9fda61aa93ca6d2ef65f23a5f8c86cc4be`.

---

## `AUD_2464_09_B41_ID05_02` — Basic Videomate / Game Pack

### Archival sources

- Hagley: `180-V6LI-Basic Videomate 3 Game Package (B2-F4)
  [AUD_2464_09_B41_ID05_02].st2`, SHA-256
  `680c4e032e009864847dbc5e2ac77df0fd467330108313dea11f2ccc3417c9d3`
- TCNJ/Sarnoff `S.572.33`, `S.572.46`: `game_pack.st2`, SHA-256
  `979bbe51a85ee6eb18c8f7ecfa238258ff92764599683f5f96e88a1312461898`

Both are complete 1280-byte ST2 containers. They differ only in the 32-byte
title field at file offsets `$0020-$003F`; their page tables and all 1024
program bytes are exact matches.

### Address map

```text
Hagley or TCNJ ST2                            Studio II/III memory

file $0000  +------------------------------+          RCA2/ST2 HEADER
            | provenance-specific title    |
file $00FF  +------------------------------+

file $0100  +------------------------------+  $0400  NEW BINARY START
            |                              |         Game Pack
            | exact shared 1024-byte data  |
file $04FF  +------------------------------+  $07FF  END
```

### Resulting files

```text
shared data, source file $0100-$04FF
    +--> Game Pack (...).bin
    |       canonical 1024-byte payload, $0400-$07FF
    |
    +--> Game Pack (...).st2
    |       TCNJ/Sarnoff title retained
    |
    +--> Basic Videomate 3 Game Package (Alt) [...].st2
            Hagley title retained; identical payload
```

Shared BIN SHA-256:
`05a941a757db1b5ef0e46f7501eae2cf3c9ed3bba978a96b6713b04c3554727d`.
The local notes identify Doodle, Curling, a Pong variant, Addition, and Freeway;
selections 3, 4, 8, and 9 remain unidentified.

---

## Four-page cartridge extractions

The following accession objects each resolve to one 1024-byte program mapped
at `$0400-$07FF`. No supported internal program boundary was found. Numbers is
excluded because its upper pages are independently identified below. For an
ST2 source, the flat BIN begins at source file offset `$0100`; for a raw source,
it begins at file offset `$0000`.

### Shared map

```text
ST2-form Hagley object                         Machine memory

file $0000  +------------------------------+          RCA2/ST2 HEADER
file $00FF  +------------------------------+
file $0100  +------------------------------+  $0400  NEW BINARY START
            | complete 1024-byte program   |
file $04FF  +------------------------------+  $07FF  END

Raw-form Hagley object                         Machine memory

file $0000  +------------------------------+  $0400  NEW BINARY START
            | complete 1024-byte program   |
file $03FF  +------------------------------+  $07FF  END
```

### Per-accession entries

| Accession | Hagley object and form | Program start | Resulting BIN and SHA-256 | Description |
| --- | --- | --- | --- | --- |
| `ID07` | `Baseball-2K (80) [...].st2`; ST2 | file `$0100` / address `$0400` | `Baseball-2K [...].bin`; `0264f192cbaac2631b69b2e658d2354506b10ba82933eca816c41636eb143a2c` | Baseball-2K prototype; controls unresolved |
| `ID08_01` | `Biorhythm [...].st2`; ST2 | file `$0100` / address `$0400` | `Biorhythm [...].bin`; `b87ef737f560b67a264b22d6ccaab79e462945fd5dafda9e86e6fc80e5e8b51b` | Studio III-era Biorhythm; controls unresolved |
| `ID08_02` | `Secret Number [...].bin`; raw, with matching ST2 | file `$0000` / address `$0400` | `Secret Number [...].bin`; `08b27f303e1e7707096d5950ba1717edccbdf7a8072ed338ff57dad6437b4fb8` | Secret Number prototype |
| `ID09_01` | `Color Demo (82-F4) [...].bin`; raw, with matching ST2 | file `$0000` / address `$0400` | `Color Demo [...].bin`; `1c998ef575fc4c5b10b61f14104c1e64b017f86f00dc5ad5e83fdec23f5ac546` | Studio III-family colour demo; keys 1-9 select demonstrations |
| `ID09_02` | `Colors Stars and Trek (82-Q1) [...].bin`; raw, with matching ST2 | file `$0000` / address `$0400` | `Colors Stars and Trek [...].bin`; `ca6e04260fdf71a30096b492944f637c1738628e3e340b8616c54cdc4aaafdba` | Studio III-family colour program; source notes only suggest key 1 |
| `ID17_02` | `Gunfight- 8 Page (37 [...].st2`; ST2 | file `$0100` / address `$0400` | `Gunfight [...].bin`; `9d5cd31e13d393eb96cfb4b125e1fe58b4bd11379e0ac6f8a73c1804207362ef` | scrolling Gunfight prototype; source notes say game 3 is absent |

The ST2 page table is `04 05 06 07` in every row. The resulting ST2 retains
the archive metadata; the resulting BIN contains only the mapped program
bytes. Emma 02 carries exact ST2 matches for Secret Number, Color Demo, Colors
Stars and Trek, and Gunfight.

---

## `AUD_2464_09_B41_ID13_01` — Paul's Printer

### Hagley source

`Paul's Printer 8 Pages @0000 180 XL1 [AUD_2464_09_B41_ID13_01].bin`

- Download size: `$0900` / 2304 bytes
- SHA-256: `667954da803715a25a8d5559349a4f1a75b8560a8f229b9a994961d43b0a06bb`
- Actual format: complete ST2 container, despite the `.bin` extension
- Header: valid count `$09`; page table `00 01 02 03 04 05 06 07`

### Address map

```text
Hagley Extracted Binary                       Studio III-family memory

file $0000  +------------------------------+          RCA2/ST2 HEADER
file $00FF  +------------------------------+
file $0100  +------------------------------+  $0000  NEW RESIDENT IMAGE START
            | resident interpreter         |
file $04FF  +------------------------------+  $03FF  INTERPRETER END
file $0500  +------------------------------+  $0400  PROGRAM REGION START
            | Paul's Printer program       |
file $08FF  +------------------------------+  $07FF  IMAGE END
```

### Resulting files

```text
Hagley file $0100-$08FF
    +--> Paul's Printer [AUD_2464_09_B41_ID13_01].rom
            exact 2048-byte absolute image, load at $0000-$07FF
```

Result ROM SHA-256:
`47d62cfaa6b0c31d485ef543976a2f732c64c8a95367c1d971a50f0f94371323`.
The inherited 1792-byte BIN begins at Hagley file `$0200` / memory `$0100` and
therefore omits the first 256-byte resident page. It is an incomplete view, not
a different version.

The first 1024 payload bytes are the Paul's Printer copy of the 180 XL-1
resident environment. Its SHA-256 is
`9b9dd1528ba59f0ea0ef7e487cc8bd92488641f7d9d47dfef85f2a6905558a9c`.
Its exact relationship to the Color Runs copy is documented below.

Binary analysis identifies the program as a CDP1864/Studio III-family colour
pattern editor. It must be loaded as a resident ROM rather than as a cartridge.

---

## `AUD_2464_09_B41_ID14_01` — Print Snoopy

### Hagley source

`Print Snoopy (22-A3) [AUD_2464_09_B41_ID14_01].bin`

- Download size: `$0200` / 512 bytes
- SHA-256: `f103f5a39b1ed7fe53f6317ce901b09dba97730c4bad92c8c1b78fab524c4c75`
- Actual format: raw two-page cartridge data
- Address evidence: companion ST2 page table `04 05`
- Companion defect: count `$05` declares four data pages, but only two exist

### Address map and outputs

```text
Hagley Extracted Binary                       Studio II-family memory

file $0000  +------------------------------+  $0400  NEW BINARY START
            | Print Snoopy, 512 bytes      |
file $01FF  +------------------------------+  $05FF  END
                  |                 |
                  |                 +--> Print Snoopy [...].bin (exact bytes)
                  +--> repaired ST2: count $05 -> $03; pages $04-$05
```

Repaired ST2 SHA-256:
`dc5ecd2ae0059952bc8cb5b8842233755c3d61ad9012e8e833db29006cff0baa`.
The program sends run-length-encoded character art through output port 3. The
PNG in the collection is a decoding of that embedded stream, not a ROM dump.

---

## `AUD_2464_09_B41_ID16_02` — Color Runs

### Hagley source

`180 XL-1 (82-A1) Color Runs (Press 1-2) 8 Pages
[AUD_2464_09_B41_ID16_02].bin`

- Download size: `$0800` / 2048 bytes
- SHA-256: `50e4abe8b4449d2f284a15b732509ce7856ea537bd4817dd58ddbd6460a91e15`
- Actual format: raw absolute resident image
- Address evidence: matching ST2 page table `00 01 02 03 04 05 06 07`

### Address map

```text
Hagley Extracted Binary                       Studio III-family memory

file $0000  +------------------------------+  $0000  NEW RESIDENT IMAGE START
            | 180 XL-1 resident interpreter|
file $03FF  +------------------------------+  $03FF  INTERPRETER END
file $0400  +------------------------------+  $0400  COLOR RUNS REGION START
            | Color Runs program           |
file $07FF  +------------------------------+  $07FF  IMAGE END
```

### Resulting files

```text
Hagley file $0000-$07FF
    +--> Color Runs [AUD_2464_09_B41_ID16_02].rom
            exact absolute image, $0000-$07FF

Hagley file $0000-$03FF
    +--> 180 XL-1 Resident Interpreter (Color Runs extraction) [...].rom
            exact additional extraction, $0000-$03FF
```

The complete ROM keeps interpreter and program together. The interpreter-only
ROM has SHA-256
`6765e9ed45f6375b6d1fac21f44653e4bf3d826b81020a64ec21e23e4574d5a6`.
Color Runs is verified on the core in Studio III mode.

### Relationship between the two 180 XL-1 resident copies

The `$0000-$03FF` regions in Paul's Printer and Color Runs are two copies of
the same 180 XL-1 resident environment, not unrelated firmware. Of 1024 bytes,
1022 are identical and in the same positions. Only two branch operands differ:

| Address | Color Runs | Paul's Printer | CDP1802 effect |
| --- | --- | --- | --- |
| `$0178` | `$53` | `$55` | the `BNF` at `$0177` branches to `$0153` or `$0155` |
| `$0183` | `$53` | `$55` | the `BNZ` at `$0182` branches to `$0153` or `$0155` |

At `$0153`, `GHI R4; PLO R7` copies the high byte of `R4` into the low byte of
`R7`; `$0155` is the following `GLO RD`. The Color Runs copy executes that
two-byte register update on both paths, while the Paul's Printer copy skips it.
Changing both references to the same instruction boundary is internally
consistent evidence of two code variants of one environment, rather than a
relocated image. The bytes alone do not establish which variant is later or
canonical, so both remain distinct and neither is silently substituted for
the other.

---

## Reconstructed test variants and split components

`tools/assemble-hagley-studio-ii-iii-variants.py` reproducibly creates the
following files from the checked archival sources. These are analytical test
assemblies and extractions, not additional Hagley objects. They do not replace
the preserved concatenated source files.

### Complete Game Pack variants for testing

Each testable image keeps Game Pack's exact `$0400-$05FF` lower pages and
substitutes one independently captured `$0600-$07FF` upper-page variant:

| Result | Lower pages | Upper pages | BIN SHA-256 |
| --- | --- | --- | --- |
| existing Game Pack | Game Pack / ID05_02 | Game Pack / ID05_02, also Numbers | `05a941a757db1b5ef0e46f7501eae2cf3c9ed3bba978a96b6713b04c3554727d` |
| Game Pack (Quiz and Tag-Race upper-page variant) | Game Pack / ID05_02 | Quiz ID04_02 and Tag-Race ID17_01 | `a5aef0a4faea97fd600a24974ff6e03283f26de1490b3bce8ef6a1627170e5f2` |
| Game Pack (Space War upper-page variant) | Game Pack / ID05_02 | Space War ID05_01 | `7450d2e96129822d00fa122638981604cdba4d9dd27ff62040d8324a9d9301ca` |

The two new variants are written as both 1024-byte BINs and four-page ST2s in
`software/RCA-Studio-II-Fullset/2 Prototypes and Betas/Alternates`. Both forms
map to `$0400-$07FF`. Because the lower and upper copies were not captured
together in these combinations, test results must be reported as behavior of
the reconstructed variant rather than behavior of a documented cartridge.

### Complete 180 XL-1 resident variants for testing

The existing Color Runs extraction and the new Paul's Printer extraction are
the two distinct 1024-byte `$0000-$03FF` resident images:

| Result | Source | ROM SHA-256 |
| --- | --- | --- |
| 180 XL-1 Resident Interpreter (Color Runs extraction) | ID16_02 bytes `$0000-$03FF` | `6765e9ed45f6375b6d1fac21f44653e4bf3d826b81020a64ec21e23e4574d5a6` |
| 180 XL-1 Resident Interpreter (Paul's Printer extraction) | ID13_01 payload bytes `$0000-$03FF` | `9b9dd1528ba59f0ea0ef7e487cc8bd92488641f7d9d47dfef85f2a6905558a9c` |

The Paul's Printer copy is written to `Alternates` as a raw ROM for loading
through the core's Machine ROM action. It differs from the Color Runs copy only
at `$0178` and `$0183`, as described above.

### Individually mapped components

The split parts are written to `software/hagley-holding/Split components`:

| Component | File form | SHA-256 of program bytes |
| --- | --- | --- |
| Game Pack common lower pages `$0400-$05FF` | 512-byte BIN | `a4d4ec3675aa59a5dca3f87509cb0f43c587780872fe0672a07e887aca90f74d` |
| Game Pack original upper pages `$0600-$07FF` | two-page ST2, pages `06 07` | `df3d798dcfd309090dbecd62c379b3ef7562b590344a90b2e0380ebf52c7aa1a` |
| Game Pack Quiz/Tag-Race upper pages `$0600-$07FF` | two-page ST2, pages `06 07` | `11eee1271289c99cbe46f23f3efc7678385d46d4cbc768b1ea81330effa81187` |
| Game Pack Space War upper pages `$0600-$07FF` | two-page ST2, pages `06 07` | `8a9f177ca9e3b2bc2aeb070fbbc0fb3d9b15253fecb07134463e0abf3ba785c6` |
| Paul's Printer program pages `$0400-$07FF` | 1024-byte BIN | `44116c8afcfd12c48b0c004f41688caf82df0a21da352933a2bd3e2be1d70f84` |
| Color Runs program pages `$0400-$07FF` | 1024-byte BIN | `a6b1b9be893eb3cece63c889298afb7e3ec643196fa2a4e561447c808f527918` |
| Space Explorer region `$0400-$07FF` | 1024-byte BIN | `060475138169f1908be11b99ec920b9c5839415326577573feea6479b6a8caa3` |
| Space Explorer region `$0C00-$0FFF` | four-page ST2, pages `0C 0D 0E 0F` | `4a0f9ca5b95e130714d57ca9f777f04c5f446a3d6cf2d31d44d2d04b0c46f477` |

The ST2 wrappers on the three upper-page pieces preserve their actual
`$0600-$07FF` mapping. Those pieces are not standalone programs. The two
program-page BINs naturally load at `$0400`, but they likewise require their
matching 180 XL-1 resident environment. Rejoining each resident ROM with its
matching program BIN exactly reconstructs the corresponding 2048-byte source
payload.

---

## `AUD_2464_09_B41_ID17_01` — Tag-Race (Joyce)

### Hagley source

`Tag Race (82-F4) Joyce 11-76 8 Pages @0000
[AUD_2464_09_B41_ID17_01].st2`

- Download size: `$0500` / 1280 bytes
- SHA-256: `9ae8353fcb4e5d83f455a8acd135b8fddf8c2ea93a02f81f4a367e70bd5d9a22`
- Actual format: complete four-page ST2; page table `04 05 06 07`
- The “8 Pages @0000” label conflicts with the encoded four-page address map

### Address map

```text
Hagley Extracted Binary                       Studio II-family memory

file $0000  +------------------------------+          RCA2/ST2 HEADER
file $00FF  +------------------------------+
file $0100  +------------------------------+  $0400  NEW BINARY START
            | released Speedway + Tag      |
file $02FF  +------------------------------+  $05FF  RELEASED ROM END
file $0300  +------------------------------+  $0600  UNRELATED REGION START
            | Game Pack upper-page variant |
file $04FF  +------------------------------+  $07FF  END
```

### Resulting files

```text
Hagley file $0000-$04FF
    +--> s2-holding/.../Archival composites/Tag-Race ID17_01/
            exact archival container and flat composite retained outside the
            playable prototype set

Hagley file $0100-$02FF
    +--> existing released USA Speedway + Tag cartridge
            exact match; no duplicate prototype entry

Hagley file $0300-$04FF
    +--> Game Pack Quiz/Tag-Race upper-page component and test assembly
```

The first 512 bytes exactly equal the released USA Speedway + Tag cartridge.
The second 512 bytes exactly equal the same Game Pack upper-page variant in the
Quiz accession. It is not Tag-Race code. Flat BIN SHA-256:
`2c09bd0b585c3c52ad727e52f11b676ef267335860608dd5ebcbb55e8fac74c6`.

---

## Shared `$0600-$07FF` Game Pack upper-page variants

The identical upper pages in Quiz and Tag-Race have SHA-256
`11eee1271289c99cbe46f23f3efc7678385d46d4cbc768b1ea81330effa81187`.
They are a three-byte variant of Game Pack's `$0600-$07FF` pages, whose SHA-256
is `df3d798dcfd309090dbecd62c379b3ef7562b590344a90b2e0380ebf52c7aa1a`:

| Address | Quiz / Tag-Race | Game Pack / Numbers | Instruction role |
| --- | --- | --- | --- |
| `$0682` | `$F3` | `$62` | opcode (`F3 04` versus `LDI R2,$04`) |
| `$06A5` | `$F2` | `$A6` | collision-branch target at `$06A4` (`$06F2` versus `$06A6`) |
| `$06F2` | `$93` | `$C6` | subroutine target at `$06F1` (`$0693` versus `$06C6`) |

This relationship is established by code structure, not by concatenation:

- Game Pack's key-selection stubs at `$04F1-$04F8` jump to `$0760`, `$06DD`,
  `$07E2`, and `$07F4` for selections 6 through 9. All four destinations are
  in the disputed upper pages.
- Code reached through those entries calls back into Game Pack's lower pages:
  the `JSR $059A` at `$0741` and `JMP $0457` at `$07F2` occur unchanged in the
  Game Pack, Quiz/Tag-Race, and other upper-page copies.
- A Studio II program begins through its selection code at `$0400`; `$0600`
  begins an internal setup routine and supplies no replacement selection
  dispatcher. The two pages therefore are not a standalone 512-byte program.
- The first halves of the Quiz and Tag-Race objects are exact released
  two-page cartridges, so neither requires or owns these upper pages.

The same provenance pattern occurs elsewhere. The Numbers object consists of
its `$0400-$05FF` program plus an exact copy of Game Pack's upper pages; its
selection code exposes only keys 1 through 3 and does not enter `$0600-$07FF`.
Its preserved four-page BIN has SHA-256
`2287da62bd0ee845683f9873b06d3d7c813ea95102ab2025ec74c9c99a7fb08b`.
That composite is now kept under holding. The playable prototype entry is the
culled 512-byte Numbers program at `$0400-$05FF`, SHA-256
`419ef74835a5d0554f6ec3138402c14080afc0b4c81feca270e0f6c0273c241a`;
its two-page ST2 SHA-256 is
`dfaa54602e15fbecdd5bc9d49ce3faad5123b6caa5e2c8de738e3211f52b91b1`.
The region later labelled `spacewar-3.st2` is another Game Pack upper-page
variant, differing from the Quiz/Tag-Race copy at six offsets. These repeated
upper-page variants support treating the pages as material copied independently
of the two-page titles, but the bytes do not reveal which tape or memory-copy
step first joined them.

The supported identity is therefore **Game Pack upper pages, variant**, not
Quiz, Tag-Race, Numbers, or Space War 3. The complete archival objects remain
preserved as captured composites; no title ownership is inferred from their
adjacency.

---

## `AUD_2464_09_B41_ID33_01` — Studio II-TV Tennis (ANDY)

### Hagley source

`Studio II-TV Tennis (ANDY) 8Pages@0000 [AUD_2464_09_B41_ID33_01].bin`

- Download size: `$0500` / 1280 bytes
- SHA-256: `6953879de16511310f1d165281936de801f826fe3b40e4390bb50587db1bebd4`
- Actual format: an ST2 container, despite the `.bin` extension
- Encoded page table: `04 05 06 07`, mapping the program to `$0400-$07FF`
- Defect: header byte `$0004` says `$03`—two data pages—but four pages are
  physically present
- The archival “8Pages@0000” label conflicts with the encoded four-page map;
  the page table and actual data length are used here

### Address map

```text
Hagley Extracted Binary                         Studio II memory

file $0000  +--------------------------------+          RCA2/ST2 HEADER
            | count says 2 data pages        |          WRONG COUNT
            | page table says $04-$07        |
file $00FF  +--------------------------------+

file $0100  +--------------------------------+  $0400  NEW BINARY START
            |                                |         TV Tennis (ANDY)
            | complete 1024-byte program     |
            |                                |
file $04FF  +--------------------------------+  $07FF  END
```

### Resulting files

```text
Hagley file $0000-$04FF
    |
    +-- change header byte $0004: $03 -> $05
    |       no program byte changes
    |
    +--> TV Tennis (ANDY) [AUD_2464_09_B41_ID33_01].st2
    |       repaired container
    |
    +-- remove header $0000-$00FF
            |
            +--> TV Tennis (ANDY) [AUD_2464_09_B41_ID33_01].bin
                    complete 1024-byte cartridge, $0400-$07FF
```

- Repaired ST2 SHA-256:
  `b08b8256b310197bd65ec3c13e7f50753ef1ce3bfe10f7bba2cc52b5726ea35f`
- Complete BIN SHA-256:
  `14eae0eeb44118a5984d07feffc7d331351e53b57f7c1a88c8b0a5ed7d540c3f`

The older 512-byte BIN is exactly Hagley file `$0100-$02FF`, or mapped memory
`$0400-$05FF`. It is the first half of this program, not a separate version.

---

## `AUD_2464_09_B41_ID33_02` — Studio II-TV Tennis, Unidentified Side 02

### Hagley source

`Studio II-TV Tennis -Unidentified Side 02 [AUD_2464_09_B41_ID33_02].bin`

- Download size: `$00FB` / 251 bytes
- SHA-256: `8d14312c225d12aaf6dd2dd12e5c0a7c54a589345a68fc1d81f00132c5222c4b`
- Actual format: raw program fragment
- Defect: five trailing zero bytes present in the companion ST2's complete
  256-byte tape block are absent from the Hagley Extracted Binary

### Address map

```text
Hagley Extracted Binary                         Companion ST2 mapping

file $0000  +--------------------------------+  $0400  FRAGMENT START
            | 251 downloaded bytes           |         FRED 1.5 tape software
file $00FA  +--------------------------------+  $04FA
            | five evidenced $00 bytes       |  $04FB  restored from complete
file $00FF  +--------------------------------+  $04FF  companion ST2 block
```

### Resulting files and reclassification

```text
Hagley Extracted Binary, 251 bytes
    + companion ST2's five trailing zero bytes
    |
    +--> FRED 1.5 Tape Software [AUD_2464_09_B41_ID33_02].bin
    |       complete 256-byte fragment
    |
    +--> FRED 1.5 Tape Software [AUD_2464_09_B41_ID33_02].st2
            count repaired from $03 to $02; one page mapped at $0400
```

- Complete 256-byte BIN SHA-256:
  `38fbfa3bb6abf2776eefd55941a702d858e74d32cc5fd5b79c1f3140f825abca`
- Repaired ST2 SHA-256:
  `a2e7be797fae204c6e546e8b2dac10a55bf70b4599b7ea36af3b66200e32360a`

Binary analysis identifies this as native CDP1801/1802 FRED 1.5 cassette
save/load software, not a missing TV Tennis page and not a runnable Studio II
cartridge. The Studio II title and `$0400` address remain documented because
they came from the archival wrapper, but the resulting files are kept outside
the playable Studio II set as non-standalone fragments.

---

## TCNJ `S.572.11B` — ST3CTA Tester 3

### TCNJ/Sarnoff source

`ST3CTA Tester 3 Cartridge.st2`

- Source: The Sarnoff Collection at TCNJ, `S.572.11B`
- Binary conversion credited locally to Marcel van Tongeren, 2018-03-05
- Download size: `$0D00` / 3328 bytes
- SHA-256: `877d3f96d6e52afb15534e453c7584034662db718f0782fb7175718b8ef6637d`
- Actual format: complete sparse ST2
- Header: valid count `$0D`; page table
  `00 01 02 03 24 25 26 27 2C 2D 2E 2F`

### Address map

```text
TCNJ/Sarnoff ST2                              Studio III diagnostic memory

file $0000  +------------------------------+          RCA2/ST2 HEADER
file $00FF  +------------------------------+
file $0100  +------------------------------+  $0000  NEW BINARY REGION
            | executable tester code       |
file $04FF  +------------------------------+  $03FF  END

file $0500  +------------------------------+  $2400  NEW BINARY REGION
            | comparison copy for          |
            | machine $0400-$07FF           |
file $08FF  +------------------------------+  $27FF  END

file $0900  +------------------------------+  $2C00  NEW BINARY REGION
            | comparison copy for          |
            | machine $0C00-$0FFF           |
file $0CFF  +------------------------------+  $2FFF  END
```

### Resulting files

```text
TCNJ/Sarnoff file $0000-$0CFF
    +--> ST3CTA Test Cartridge - Tester 3 (...).st2
    |       exact sparse container; page table preserves all destinations
    |
TCNJ/Sarnoff file $0100-$0CFF
    +--> ST3CTA Test Cartridge - Tester 3 (...).bin
            3072 data bytes concatenated in ST2 block order
```

The BIN's offsets `$0000`, `$0400`, and `$0800` are block boundaries, not the
three machine addresses. Without the ST2 page table, the BIN can be mistaken
for a linear `$0000-$0BFF` image. BIN SHA-256:
`12a078076861dfd3511b78cabc868dbcdd02aa6b0aec77905162ec5990805bef`.

This diagnostic addresses pages above the core's deliberately modelled 4 KiB
cartridge space, so preservation and mapping are complete even though current
RTL cannot run the full high-page test.

---

## Prototype and beta fullset hygiene sweep

The final sweep applies these rules to every binary object under
`2 Prototypes and Betas`:

- every ST2's declared block count equals its physical block count;
- every ST2 page destination is unique within that container;
- every BIN, ROM, and ST2 has a same-stem TXT note;
- the known Quiz, Tag-Race, Numbers, and Space War composites do not remain as
  playable overdumps;
- all aligned 512-byte regions were compared with standalone 512-byte payloads
  throughout the software holdings. The only cross-title matches are the
  already documented Game Pack pieces and the released-program halves of Quiz
  and Tag-Race. No supported new split was found in Baseball-2K, Biorhythm,
  Color Demo, Colors Stars and Trek, Gunfight, New Studio 2-5 Game Set, Secret
  Number, or TV Tennis (ANDY).

Space Explorer required a format correction rather than a title split. Its ST2
maps `$0400-$07FF` and `$0C00-$0FFF`; the old 2048-byte BIN concatenated those
regions and loaded the second half at the wrong addresses. The ST2 remains the
canonical playable file, the concatenated BIN is preserved in holding, and the
two mapped regions are retained separately in `Split components`.

The inherited `Space War 2 (Alt)` ST2 also declared four data pages while
physically containing two. Its playable copy now declares two data pages; the
defective original is preserved under `Header defects/Space War 2`.

## Condensed provenance handoff

```text
Hagley / TCNJ audio tape
  |
  +-- ID03_01 “New Studio 2-5 Game Set”
  |     Extracted Binary: raw 1 KiB
  |     $0400 New Studio 2-5 Game Set ----------------> BIN + ST2
  |
  +-- ID04_02 “Studio 2 Quiz”
  |     Extracted Binary: ST2 misnamed BIN
  |     $0400 TV School House I -----------------------> existing released ROM
  |     $0600 Game Pack upper-page variant ------------> component + test assembly
  |     $0400-$07FF captured composite ----------------> archival holding
  |
  +-- ID05_01 “180 Space War (S2-A3)”
  |     Extracted Binary: ST2 misnamed BIN
  |     $0400 Space War 2 -----------------------------> canonical BIN + two-page ST2
  |     $0600 Game Pack upper-page variant ------------> component + test assembly
  |     $0400-$07FF captured composite ----------------> archival holding
  |
  +-- ID05_02 “Basic Videomate 3 Game Package”
  |     Extracted Binary: four-page ST2
  |     $0400 Game Pack, exact TCNJ payload -----------> canonical BIN + ST2
  |                                                     Hagley-header Alt ST2
  |
  +-- ID07 / ID08 / ID09 / ID17_02
  |     Extracted Binary: raw or four-page ST2
  |     $0400 one complete 1 KiB program --------------> BIN + retained ST2
  |
  +-- ID12_01 “Numbers”
  |     Extracted Binary: raw 1 KiB plus matching ST2
  |     $0400 Numbers, keys 1-3 -----------------------> canonical BIN + two-page ST2
  |     $0600 exact Game Pack upper pages -------------> shared component
  |     $0400-$07FF captured composite ----------------> archival holding
  |
  +-- ID13_01 “Paul's Printer”
  |     Extracted Binary: eight-page ST2 misnamed BIN
  |     $0000 resident environment --------------------+
  |     $0400 Paul's Printer program ------------------+-> absolute 2 KiB ROM
  |
  +-- ID14_01 “Print Snoopy”
  |     Extracted Binary: raw 512 bytes
  |     $0400 Print Snoopy ----------------------------> BIN + repaired ST2
  |
  +-- ID16_02 “Color Runs”
  |     Extracted Binary: absolute 2 KiB image
  |     $0000 resident interpreter --------------------> interpreter ROM
  |     $0000-$07FF complete Color Runs image ---------> complete ROM
  |
  +-- ID17_01 “Tag-Race”
  |     Extracted Binary: four-page ST2
  |     $0400 released Speedway + Tag -----------------> existing released ROM
  |     $0600 Game Pack upper-page variant ------------> component + test assembly
  |     $0400-$07FF captured composite ----------------> archival holding
  |
  +-- ID33_01 “Studio II-TV Tennis (ANDY)”
  |     Extracted Binary: ST2 misnamed BIN, wrong count
  |     $0400 TV Tennis, complete 1 KiB ---------------> repaired ST2 + BIN
  |
  +-- ID33_02 “Studio II-TV Tennis, Side 02”
  |     Extracted Binary: 251-byte fragment
  |     $0400 FRED 1.5 tape software ------------------> completed BIN + repaired ST2
  |                                                     reclassified outside Studio II
  |
  +-- TCNJ S.572.11B “ST3CTA Tester 3”
        Extracted Binary: sparse twelve-page ST2
        $0000 tester code -----------------------------+
        $2400 first comparison image ------------------+-> sparse ST2 + block-order BIN
        $2C00 second comparison image -----------------+
```

## Reproducibility and preservation rules

- The Hagley Extracted Binary downloads remain unchanged.
- Splits are made only at exact, byte-supported boundaries.
- A `.bin` containing `RCA2` is preserved as an ST2; the extension is corrected
  rather than treating the header as program data.
- Header repairs change only ST2 byte `$0004` and leave all program bytes
  untouched.
- Missing bytes are not guessed. The five Side 02 zeros are restored only
  because the separately retained companion ST2 block preserves them.
- “Exact match” means full byte-for-byte equality, verified with SHA-256 and the
  repository verifier—not similarity observed during emulation.
- Emma 02 and other collections corroborate provenance; they are not substituted
  for the Hagley source.
