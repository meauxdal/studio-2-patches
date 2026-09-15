# Colors Stars and Trek investigation

## Status — 2026-09-15

Software/provenance investigation only. Trek's use of an additional display
RAM page is the leading explanation for its broken picture. The required
historical Studio III configuration and custom display timing remain unknown.
No RTL change is justified by the evidence collected so far.

## Exact input

`software/RCA-Studio-II-Fullset/2 Prototypes and Betas/Colors Stars and Trek [AUD_2464_09_B41_ID09_02].bin`

- Length: 1,024 bytes.
- SHA-256: `ca6e04260fdf71a30096b492944f637c1738628e3e340b8616c54cdc4aaafdba`.
- Prior investigation reports CRC16-CCITT `F498` and identical Hagley/Emma
  ST2 payloads, explicitly mapped to pages `04 05 06 07`.
- Reported ST2 SHA-256:
  `8c95a7f749cb0e46ee82b3c2018d8bb671023f90adc2d6976544506a3f4ffbbf`.

The raw cartridge length and SHA-256 were independently rechecked when this
note was created. ST2 identity and CRC above are carried forward from the
prior investigation, not newly verified here. Do not invent missing pages.

## Findings carried forward

- A1 selects Stars, which works and retains the resident interrupt routine.
  A2 selects Trek, which is visibly broken.
- Selection dispatch: `0400=6A01`, `0402=D10A`, `0404=D208`,
  `0408=16E7`, `040A=220B`, `040C=1600`.
- Trek calls native `0610` at `0656`. That routine begins with IDL, sets
  `R1=062A`, and returns with `D4`.
- The custom ISR at `062A` sets `R0=0900`. Its loop at `063A` is
  `80 E2 E2 20 A0 3C 3A`. A 64-row NTSC target remains a timing hypothesis.
- Trek sets `A=0700` at `05EA`, jumps to `065E`, and calls native `0618`.
  That routine sets `RC=0A00` and copies 256 bytes from `[RA++]` to `[RC++]`
  until the low byte of RC wraps. The destination is `0A00–0AFF`.
- Cartridge `0700–07FF` decodes as a coherent 64×32 spacecraft bitmap.
  The observed large blocks are not that artwork.
- With this cartridge, current RTL does not provide RAM at `0A00`:
  writes are ignored and unmapped reads return `FF`. The saved standard Emma
  PAL and NTSC configurations also omit this RAM page.
- Resident routine `02F2` fills using `GHI R1`; after Trek installs its ISR,
  that value is `06`, not zero. The manual's clear shorthand is insufficient.

The `0610–0640` cartridge bytes were rechecked against the above account.
The RTL RAM select excludes addresses with bit 9 set, and the read mux
defaults to `FF`; cartridge mappings must still be considered for each input.

## Prior observations and their limits

User-supplied simulation results: Stars matches a simplified reference at
frames 120/240/480/600; Trek differs. At Trek frame 120, the first display
page (`0900–09FF`) and 64 color cells match exactly. The reference renders
only 32 logical rows and cannot validate Trek's custom DMA extent. Several
resident firmware variants produce the same broken PAL result.

The previous session ran Emma 02 v2.00 with standard Studio III NTSC,
the exact ST2, and keyboard `2`. It showed upper graphics followed by large
colored blocks. Standard PAL A2 capture was not completed.

These observations support investigating the missing second display page
and a possible PAL display-length mismatch. They do not establish an RTL
defect or prove historical expanded-memory hardware.

## Preserved scratch evidence

Under `tmp/trek-investigation-20260915/` (local scratch, not a build dependency):

- `embedded-0700-bitmap.png`: decoded cartridge artwork.
- `emma-standard-ntsc-a2.png`: previous session's emulator capture.
- `standard-ntsc.xml`, `standard-pal.xml`: saved upstream configurations.
- `experiment-ntsc-extra-a00-ram.xml`: **prepared, never run**. Its only
  differences from the saved NTSC configuration are the descriptive label
  and one RAM region, `0A00–0AFF`; this diff was rechecked.
- `emma-current-pixie.cpp`: saved upstream source, reported revision
  `6cef5f299a32206d939afaaabb56d4c5efc6c4fa`.
- `hagley.html`: saved accession metadata.
- `hagley-current-download.bin`: 45,889,866-byte RIFF/WAVE recording,
  despite its extension. It is not a newly verified ROM.

Prior metadata source: [Hagley accession AUD_2464_09_B41_ID09_02](https://digital.hagley.org/AUD_2464_09_B41_ID09_02),
reported as “Color Stars and Trek (82-Q1),” approximately 1977, cassette
Side 02, without specific hardware requirements. Local primary manual:
`untracked_docs/Programming_Manual_for_STUDIO_III_Sep77.pdf`.

## User-run NTSC experiment: successful RAM copy

The user replaced the installed NTSC XML with the experimental file; matching
SHA-1 hashes confirmed the replacement. However, the experimental label did
not appear and Emma's Memory Type view showed page A as undefined. Thus the
XML attempt did not establish an active RAM mapping.

The user then changed page A to RAM (`.`) through Memory Type and restarted
the program. The NTSC screenshot now shows the recognizable spacecraft
instead of solid blocks. Some visual effects remain unexplained.

The supplied `memorydump.bin` is a full 65,536-byte CPU memory dump. Direct
comparison found zero differences between dump `0A00–0AFF` and cartridge
`0700–07FF`, and zero differences between dump `0400–07FF` and the entire
1,024-byte cartridge. This establishes a successful copy in the experimental
NTSC run, not a historical hardware configuration.

## Display-loop analysis

```text
063A 80     GLO R0       ; capture low byte of DMA pointer
063B E2     SEX R2
063C E2     SEX R2
063D 20     DEC R0
063E A0     PLO R0       ; restore captured low byte
063F 3C 3A  BN1 063A
```

These are six two-machine-cycle instructions, totaling 12 CPU cycles per
iteration (RCA MPM-201A instruction summary). In the saved Emma
`Pixie::cyclePixie()` code, an eight-byte-wide line takes 14 machine cycles,
eight used for DMA. Two lines therefore leave 12 CPU cycles. This supports
a two-scanline repetition interpretation and a 64-logical-row NTSC display.
It does not establish the initial phase or the last lines' DMA addresses.

Do not simplify `DEC R0; PLO R0` to an unconditional full-pointer restore:
PLO restores only the low byte, while DEC can change the high byte at a page
boundary. DMA also advances R0 between instructions. A trace is needed to
check the actual sequence, including the `09FF/0A00` transition and final
EF-controlled loop exit. Correct bitmap storage alone cannot resolve this.

## Full NTSC trace result

User-supplied `trace.log`, preserved locally as
`tmp/trek-investigation-20260915/user-ntsc-trace-20260915.log`, contains
4,969 lines and two complete display DMA intervals. Each contains 1,024 DMA
bytes (128 eight-byte scanlines). Both have the same address sequence:

- Rows starting at `0900` through `0AF0`, in steps of eight, appear twice.
- The `09F8` pair and transition to the `0A00` pair are correct.
- `0AF8–0AFF` appears once; the final scanline reads `0B00–0B07`.

All 1,016 preceding DMA addresses match the expected doubled-row sequence;
only the final eight differ, in both intervals. After the second `0AF0` row,
`063F: BN1 3A` falls through to `0641`. The CPU begins timer maintenance
while two DMA bursts remain, so R0 advances without another row rewind.
This establishes a bottom-edge overrun in this Emma NTSC run and offers a
specific explanation for the thin line under the ship. It does not explain
all perceived glitches or establish that real hardware behaves identically.

## Studio II alternate comparison

The user observed similar bottom lines with both Fullset alternate BIOSes.
Byte comparison of the Studio II standard and alternate files found exactly
one difference: `003E` is `34` (B1) in standard and `38` (SKP/NBR) in the
alternate. The following operand is `3C`. This disables the conditional
branch back to the final `DEC R0; PLO R0` loop. The Studio III NTSC alternate
also differs in its display ISR; its trace result follows below.

The user's Studio II alternate trace is preserved as
`tmp/trek-investigation-20260915/user-s2-alt-trace.log`. It contains the tail
of a display interval, without an interrupt marker. After two visible
`09F8–09FF` bursts, `003E: NBR` falls through into timer maintenance.
Two remaining scanlines read `0A00–0A07` and `0A08–0A0F`.

This confirms the same failure class as Trek in Emma: row rewinding ends
before display DMA, so the final scanlines read beyond the intended bitmap.
The details differ: Studio II alternate overruns its `0900–09FF` page for
two scanlines; Trek overruns `0900–0AFF` for one. DMA address logs do not
include pixel values. The alternate firmware's origin and intended timing
remain unknown; this is not evidence that Emma itself is wrong.

The subsequent Studio III alternate trace, preserved as
`tmp/trek-investigation-20260915/user-s3-alt-trace.log`, contains one display
tail followed by part of the next display interval. At the captured tail,
`003A: B1 41` branches into timer maintenance. DMA still reads `09F0–09F7`,
then `09F8–09FF`, then `0A00–0A07`. Thus this alternate also overruns its
bitmap, for one final scanline. Unlike the Studio II alternate's unconditional
fall-through, this exit is EF-controlled, making it a closer comparison to
Trek's EF-controlled exit. It does not distinguish a historical firmware
assumption from an emulator timing discrepancy.

## Upper-score corruption: resident R1 dependency

The supplied memory dump was preserved as `user-memorydump.bin` in the same
scratch directory. Its resident code exposes a second consequence of Trek
moving R1 to `06xx`, beyond the known `02F2` fill behavior:

- `0135: GHI R1; STR R6` is the pattern-erasure loop. It writes `06`
  instead of zero when Trek's ISR is installed.
- Decimal conversion at `0273: GHI R1; PHI RE` constructs a table pointer
  whose low byte is set to `BC`. Standard R1 selects `00BC`, containing
  `64 0A 01` (100, 10, 1). Trek instead selects `06BC`, containing
  `6C 06 E1`, which is cartridge code, not the decimal table.
- `027A: GHI R1; STR RC` also initializes decimal digits with `06`
  instead of zero.
- The dump has scores `0880=00`, `0881=0A`, but decimal scratch bytes
  `0882–0884=06 07 06`. These are inconsistent with proper conversion
  of either score (000 or 010).

Cartridge `05E0` calls resident score code (`23A9`, `2368`), and the resident
`0368` path invokes decimal conversion (`9XY8` at `0370`), then erases and
builds a score pattern. This provides a concrete software mechanism for
upper-screen corruption even with correct display DMA and added RAM.
An execution trace through this score path is still needed to tie each
corrupted output to the captured screen. Do not replace all GHI R1 uses:
some post-install fills may intentionally depend on `06` for color.

## Handwritten planning/source witness: MSS_246409_0874_21_01

The user supplied an eight-page reconstructed PDF from Hagley scans, titled
`MSS_246409_0874_21_01 FRED games 'Trek' graphing computer game planning-compressed.pdf`.
The user quotes Hagley's folder note: "From a partially scanned folder
containing diagrams, instructions, and notes about FRED games."
That is collection context, not an explicit machine identification for every
sheet. All eight PDF pages were visually inspected; ambiguous handwriting
was not treated as an exact transcription. Page numbers below refer to the
user's PDF, often containing two original sheets side by side.

- Page 1: Enterprise screen plan with color annotations and both `09xx` and
  `0Axx` display addressing. Page 2: another screen plan and shared selector
  listing at `0400`, including the Stars entry and corrected Trek destination.
- Page 3: `0610` installs R1=`062A`; `0618` is explicitly described as moving
  Enterprise into TV "(PAGE A)" and sets RC=`0A00`. The `063A` loop is
  `80 E2 E2 20 A0 3C 3A`, exactly as in the cartridge. The right sheet labels
  the saucer, photon, fire flag, and a key-0 fire path. The listing includes
  revisions rather than a single clean final program.
- Page 4: saucer/photon movement and hit processing; `61 0A; 23 8F` at
  `06D6` awards ten to the score. The score-display call and its later
  relocation are annotated. This directly supports investigating resident
  score routines in this program.
- Page 5: saucer/photon patterns and Enterprise bytes at `0700`.
- Page 6: color initialization and explicit corrections. Cartridge matches
  checked corrections `070B=10`, `072E=1F02`, `07B2=38`, `07C2=38`, plus
  saucer bytes `06F9=30 78 FC FC 78 30`.
- Page 7: another color sketch and a typed "SHOOTING STARS" listing whose
  header says it uses the built-in interpreter. This sheet's annotations
  must not automatically be applied to Trek.
- Page 8: a separate-looking special memory-dump routine with a display area
  `0180–01FF`. Its relationship to Trek is not established.

The exact matching addresses, code, shared selector, and incorporated
corrections establish a close relationship to the surviving cartridge.
Extra display RAM was explicitly planned, not merely an accidental write.
The source still installs R1 high=`06` and calls resident score routines;
it does not by itself resolve that interpreter incompatibility. No inspected
sheet establishes VIP hardware, authorship, a working final build, or a
specific resident firmware image. The other cassette titles supplied by the
user are research leads, not evidence that they share one runtime.

## Next bounded experiment

1. Compare the final EF transition and ISR exit with primary CDP1861 timing
   before proposing any software or emulator timing experiment.
2. Investigate upper-screen content separately; the trace does not show a
   row-address fault there. Do not label unfamiliar symbols as corrupt solely
   from appearance.
3. PAL comparison remains pending. Emulator success supports a software
   dependency, not historical hardware.

The user performed the Emma runs; agent native app control is disabled.
No Quartus, Verilator build, hardware regression, release change, or RTL edit
was performed.
