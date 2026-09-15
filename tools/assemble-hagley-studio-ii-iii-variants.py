#!/usr/bin/env python3
"""Assemble testable Hagley Game Pack and 180 XL-1 variants and split parts."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOLDING = ROOT / "software" / "s2-holding"
HAGLEY = HOLDING / "Hagley Digital Archives"
FULLSET = ROOT / "software" / "RCA-Studio-II-Fullset"
PROTOTYPES = FULLSET / "2 Prototypes and Betas"
ALTERNATES = PROTOTYPES / "Alternates"
COMPONENTS = ROOT / "software" / "hagley-holding" / "Split components"
ARCHIVAL_COMPOSITES = HOLDING / "6 Alternates - Review" / "Archival composites"
HEADER_DEFECTS = HOLDING / "6 Alternates - Review" / "Header defects"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_read(path: Path, expected_sha256: str) -> bytes:
    data = path.read_bytes()
    actual = sha256(data)
    if actual != expected_sha256:
        raise ValueError(f"unexpected SHA-256 for {path}: {actual}")
    return data


def st2_payload(data: bytes, pages: tuple[int, ...]) -> bytes:
    if data[:4] != b"RCA2":
        raise ValueError("source is not an ST2 container")
    if data[4] != len(pages) + 1 or tuple(data[64 : 64 + len(pages)]) != pages:
        raise ValueError("unexpected ST2 block count or page table")
    payload = data[256:]
    if len(payload) != len(pages) * 256:
        raise ValueError("unexpected ST2 payload length")
    return payload


def make_st2(payload: bytes, pages: tuple[int, ...], title: str) -> bytes:
    if len(payload) != len(pages) * 256:
        raise ValueError("payload size does not match page table")
    title_bytes = title.encode("ascii")
    if len(title_bytes) > 32:
        raise ValueError("ST2 title exceeds 32 bytes")
    header = bytearray(256)
    header[:4] = b"RCA2"
    header[4] = len(pages) + 1
    header[5] = 1
    header[8:12] = b"JWMT"
    header[32 : 32 + len(title_bytes)] = title_bytes
    header[64 : 64 + len(pages)] = bytes(pages)
    return bytes(header) + payload


def write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == data:
        state = "unchanged"
    else:
        path.write_bytes(data)
        state = "wrote"
    print(f"{state:9} {len(data):4} bytes  {sha256(data)}  {path.relative_to(ROOT)}")


def preserve(path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / path.name
    data = path.read_bytes()
    if target.exists() and target.read_bytes() != data:
        raise ValueError(f"preservation target differs: {target}")
    if not target.exists():
        shutil.copy2(path, target)
    if target.read_bytes() != data:
        raise ValueError(f"preservation copy failed: {target}")
    path.unlink()
    print(f"preserved           {path.relative_to(ROOT)} -> {target.relative_to(ROOT)}")


def preserve_stem_if_hash(
    directory: Path,
    stem: str,
    marker_extension: str,
    expected_sha256: str,
    destination: Path,
) -> None:
    marker = directory / f"{stem}{marker_extension}"
    if not marker.exists() or sha256(marker.read_bytes()) != expected_sha256:
        return
    for path in sorted(
        path for path in directory.iterdir() if path.is_file() and path.stem == stem
    ):
        preserve(path, destination)


def preserve_copy(path: Path, destination: Path, target_name: str | None = None) -> None:
    target = destination / (target_name or path.name)
    destination.mkdir(parents=True, exist_ok=True)
    data = path.read_bytes()
    if target.exists() and target.read_bytes() != data:
        raise ValueError(f"preservation target differs: {target}")
    if not target.exists():
        shutil.copy2(path, target)
        print(f"preserved copy      {path.relative_to(ROOT)} -> {target.relative_to(ROOT)}")


def main() -> None:
    preserve_stem_if_hash(
        PROTOTYPES,
        "Quiz [AUD_2464_09_B41_ID04_02]",
        ".bin",
        "f99591c280e9f29ff98889e87d23306bfa980e730d367e2307dc0a55fcee4110",
        ARCHIVAL_COMPOSITES / "Quiz ID04_02",
    )
    preserve_stem_if_hash(
        PROTOTYPES,
        "Tag-Race (Joyce) [AUD_2464_09_B41_ID17_01]",
        ".bin",
        "2c09bd0b585c3c52ad727e52f11b676ef267335860608dd5ebcbb55e8fac74c6",
        ARCHIVAL_COMPOSITES / "Tag-Race ID17_01",
    )
    preserve_stem_if_hash(
        PROTOTYPES,
        "Numbers [AUD_2464_09_B41_ID12_01]",
        ".bin",
        "2287da62bd0ee845683f9873b06d3d7c813ea95102ab2025ec74c9c99a7fb08b",
        ARCHIVAL_COMPOSITES / "Numbers ID12_01",
    )
    numbers_archive = ARCHIVAL_COMPOSITES / "Numbers ID12_01"
    preserve_copy(
        HAGLEY
        / "Numbers (82-F4) 1-2=Bagels, 3=Reverse "
        "[AUD_2464_09_B41_ID12_01].bin",
        numbers_archive,
        "Numbers [AUD_2464_09_B41_ID12_01].bin",
    )
    preserve_copy(
        HAGLEY
        / "Numbers (82-F4) 1-2=Bagels, 3=Reverse "
        "[AUD_2464_09_B41_ID12_01].st2",
        numbers_archive,
        "Numbers [AUD_2464_09_B41_ID12_01].st2",
    )
    archived_numbers_note = numbers_archive / "Numbers [AUD_2464_09_B41_ID12_01].txt"
    if not archived_numbers_note.exists():
        write(
            archived_numbers_note,
            b"Hagley Museum and Library: Sarnoff/RCA Collection -Joseph A. "
            b"Weisbecker's archived manuscripts and materials -Accession 2464 "
            b"-Box Number AVD B41\r\n\r\n1-2=Bagels, 3=Reverse\r\n",
        )
    preserve_stem_if_hash(
        PROTOTYPES,
        "Space War 2 + 3 [AUD_2464_09_B41_ID05_01]",
        ".st2",
        "088d37168dbefe863acb0fabe999c837abd371b92d0a9430bda5ca3672f93051",
        ARCHIVAL_COMPOSITES / "Space War ID05_01",
    )
    space_explorer_bin = PROTOTYPES / "Space Explorer (1978) (Thomas Lenihan).bin"
    if (
        space_explorer_bin.exists()
        and sha256(space_explorer_bin.read_bytes())
        == "a568a6bb40fd5cb172ec1a2c424f6bc9a5e2084adb2a531ea22f409518ed33db"
    ):
        preserve(
            space_explorer_bin,
            ARCHIVAL_COMPOSITES / "Space Explorer block-concatenated BIN",
        )
    preserve_stem_if_hash(
        ALTERNATES,
        "Space War 2 (Alt) [AUD_2464_09_B41_ID05_01]",
        ".st2",
        "08b68e8662d66c77e675ff4142288e63536af0ae35cd0a4d7d916405f49d138b",
        HEADER_DEFECTS / "Space War 2",
    )

    game_pack_st2 = checked_read(
        PROTOTYPES
        / "Game Pack (Doodle, Curling, Pong, Addition, Freeway) "
        "(Joseph Weisbecker).st2",
        "979bbe51a85ee6eb18c8f7ecfa238258ff92764599683f5f96e88a1312461898",
    )
    game_pack = st2_payload(game_pack_st2, (4, 5, 6, 7))
    quiz_st2 = checked_read(
        HAGLEY / "Studio 2 Quiz (B2-F4) [AUD_2464_09_B41_ID04_02].bin",
        "53cd4aba4e2ed136face90cf109c17ab9e695610de40845566b936b9dec4fab2",
    )
    quiz_upper = st2_payload(quiz_st2, (4, 5, 6, 7))[0x200:]
    space_war_st2 = checked_read(
        HAGLEY
        / "180 Space War (S2-A3) 512 Bytes [AUD_2464_09_B41_ID05_01].bin",
        "088d37168dbefe863acb0fabe999c837abd371b92d0a9430bda5ca3672f93051",
    )
    space_war_upper = st2_payload(space_war_st2, (4, 5, 6, 7))[0x200:]

    game_pack_lower = game_pack[:0x200]
    game_pack_upper = game_pack[0x200:]
    game_pack_quiz_variant = game_pack_lower + quiz_upper
    game_pack_space_war_variant = game_pack_lower + space_war_upper

    variant_rows = (
        (
            "Game Pack (Quiz and Tag-Race upper-page variant) "
            "[AUD_2464_09_B41_ID04_02, ID17_01]",
            game_pack_quiz_variant,
            "GAME PACK QUIZ-TAG UPPER",
        ),
        (
            "Game Pack (Space War upper-page variant) "
            "[AUD_2464_09_B41_ID05_01]",
            game_pack_space_war_variant,
            "GAME PACK SPACEWAR UPPER",
        ),
    )
    for name, payload, title in variant_rows:
        write(ALTERNATES / f"{name}.bin", payload)
        write(ALTERNATES / f"{name}.st2", make_st2(payload, (4, 5, 6, 7), title))

    game_pack_variant_note = """Title: {title}

Provenance and status:
* Synthetic test assembly made from Game Pack's exact $0400-$05FF lower pages
  and the {upper_source} $0600-$07FF upper pages.
* This combination was not captured as one archival object and must not be
  described as a documented cartridge dump.
* BIN SHA-256: {digest}

Testing:
* Load the BIN or ST2 as a cartridge and compare selections 1 through 9 with
  the canonical Game Pack. Record any differences by selection.
"""
    write(
        ALTERNATES / f"{variant_rows[0][0]}.txt",
        game_pack_variant_note.format(
            title="Game Pack (Quiz and Tag-Race upper-page variant)",
            upper_source="Quiz ID04_02 / Tag-Race ID17_01",
            digest=sha256(game_pack_quiz_variant),
        ).encode(),
    )
    write(
        ALTERNATES / f"{variant_rows[1][0]}.txt",
        game_pack_variant_note.format(
            title="Game Pack (Space War upper-page variant)",
            upper_source="Space War ID05_01",
            digest=sha256(game_pack_space_war_variant),
        ).encode(),
    )

    component_rows = (
        (
            "Game Pack lower pages $0400-$05FF [AUD_2464_09_B41_ID05_02].bin",
            game_pack_lower,
        ),
        (
            "Game Pack upper pages $0600-$07FF [AUD_2464_09_B41_ID05_02].st2",
            make_st2(game_pack_upper, (6, 7), "GAME PACK UPPER ORIGINAL"),
        ),
        (
            "Game Pack upper pages $0600-$07FF (Quiz and Tag-Race variant) "
            "[AUD_2464_09_B41_ID04_02, ID17_01].st2",
            make_st2(quiz_upper, (6, 7), "GAME PACK UPPER QUIZ-TAG"),
        ),
        (
            "Game Pack upper pages $0600-$07FF (Space War variant) "
            "[AUD_2464_09_B41_ID05_01].st2",
            make_st2(space_war_upper, (6, 7), "GAME PACK UPPER SPACEWAR"),
        ),
    )
    for name, payload in component_rows:
        write(COMPONENTS / name, payload)

    pauls_printer_st2 = checked_read(
        HAGLEY
        / "Paul's Printer 8 Pages @0000 180 XL1 [AUD_2464_09_B41_ID13_01].bin",
        "667954da803715a25a8d5559349a4f1a75b8560a8f229b9a994961d43b0a06bb",
    )
    pauls_printer = st2_payload(pauls_printer_st2, tuple(range(8)))
    color_runs = checked_read(
        HAGLEY
        / "180 XL-1 (82-A1) Color Runs (Press 1-2) 8 Pages "
        "[AUD_2464_09_B41_ID16_02].bin",
        "50e4abe8b4449d2f284a15b732509ce7856ea537bd4817dd58ddbd6460a91e15",
    )
    space_explorer_st2 = checked_read(
        PROTOTYPES / "Space Explorer (1978) (Thomas Lenihan).st2",
        "258eaf7637b6524ed363e91982b01cfc08cf970e8e269cce26e262ffe8b4b784",
    )
    space_explorer = st2_payload(
        space_explorer_st2, (4, 5, 6, 7, 0x0C, 0x0D, 0x0E, 0x0F)
    )

    write(
        ALTERNATES
        / "180 XL-1 Resident Interpreter (Paul's Printer extraction) "
        "[AUD_2464_09_B41_ID13_01].rom",
        pauls_printer[:0x400],
    )
    write(
        ALTERNATES
        / "180 XL-1 Resident Interpreter (Paul's Printer extraction) "
        "[AUD_2464_09_B41_ID13_01].txt",
        b"""Title: 180 XL-1 Resident Interpreter (Paul's Printer extraction)
Archive ID: AUD_2464_09_B41_ID13_01

Provenance and status:
* Extracted unchanged from payload bytes $0000-$03FF of the archival Paul's
  Printer ST2 object.
* This is an unverified resident-environment variant, not a production BIOS
  identification.
* ROM SHA-256: 9b9dd1528ba59f0ea0ef7e487cc8bd92488641f7d9d47dfef85f2a6905558a9c
* It differs from the Color Runs extraction only at $0178 and $0183, where
  this copy contains $55 instead of $53.

Testing:
* Load through Machine ROM in Studio III mode, first bare and then with the
  matching Paul's Printer program-page BIN from the split-components holding
  folder.
""",
    )
    write(
        COMPONENTS / "Paul's Printer program pages $0400-$07FF [AUD_2464_09_B41_ID13_01].bin",
        pauls_printer[0x400:],
    )
    write(
        COMPONENTS / "Color Runs program pages $0400-$07FF [AUD_2464_09_B41_ID16_02].bin",
        color_runs[0x400:],
    )
    write(
        COMPONENTS / "Space Explorer region $0400-$07FF (Thomas Lenihan).bin",
        space_explorer[:0x400],
    )
    write(
        COMPONENTS / "Space Explorer region $0C00-$0FFF (Thomas Lenihan).st2",
        make_st2(space_explorer[0x400:], (0x0C, 0x0D, 0x0E, 0x0F), "SPACE EXPLORER HIGH REGION"),
    )

    numbers_st2 = checked_read(
        HAGLEY
        / "Numbers (82-F4) 1-2=Bagels, 3=Reverse "
        "[AUD_2464_09_B41_ID12_01].st2",
        "73833f33891d5af1e6f5090b28350451a549d88be8f66ff006e4c4c73981ca52",
    )
    numbers_payload = st2_payload(numbers_st2, (4, 5, 6, 7))[:0x200]
    numbers_header = bytearray(numbers_st2[:256])
    numbers_header[4] = 3
    numbers_header[66:128] = b"\0" * 62
    numbers_culled_st2 = bytes(numbers_header) + numbers_payload
    numbers_name = "Numbers [AUD_2464_09_B41_ID12_01]"
    write(PROTOTYPES / f"{numbers_name}.bin", numbers_payload)
    write(PROTOTYPES / f"{numbers_name}.st2", numbers_culled_st2)
    write(
        PROTOTYPES / f"{numbers_name}.txt",
        f"""Title: Numbers
Archive ID: AUD_2464_09_B41_ID12_01
Archive label: Numbers (82-F4) 1-2=Bagels, 3=Reverse

Provenance and format:
* The archival four-page object contains this program at $0400-$05FF followed
  by an exact copy of Game Pack's $0600-$07FF upper pages.
* This canonical entry contains only the two Numbers pages. The unchanged
  four-page composite is preserved under s2-holding/6 Alternates - Review/
  Archival composites/Numbers ID12_01.
* BIN SHA-256: {sha256(numbers_payload)}
* ST2 SHA-256: {sha256(numbers_culled_st2)}

Controls:
* 1-2: Bagels
* 3: Reverse
""".encode(),
    )

    space_war_payload = st2_payload(space_war_st2, (4, 5, 6, 7))[:0x200]
    space_war_name = "Space War 2 [AUD_2464_09_B41_ID05_01]"
    space_war_culled_st2 = make_st2(
        space_war_payload, (4, 5), "SPACE WAR 2 HAGLEY ID05_01"
    )
    write(PROTOTYPES / f"{space_war_name}.bin", space_war_payload)
    write(PROTOTYPES / f"{space_war_name}.st2", space_war_culled_st2)
    write(
        PROTOTYPES / f"{space_war_name}.txt",
        f"""Title: Space War 2
Archive ID: AUD_2464_09_B41_ID05_01

Provenance and format:
* Exact $0400-$05FF first region of the archival four-page 180 Space War
  object. Its unrelated $0600-$07FF region is a Game Pack upper-page variant.
* The unchanged four-page composite is preserved under s2-holding/6
  Alternates - Review/Archival composites/Space War ID05_01.
* BIN SHA-256: {sha256(space_war_payload)}
* ST2 SHA-256: {sha256(space_war_culled_st2)}

Known startup:
* A1 launches the horizontal-intercept screen.
* A2 launches the two-player/vertical-intercept screen.
* Play controls have not been independently reverified.
""".encode(),
    )

    repaired_space_war_alt = (
        HOLDING / "Space War 2 [AUD_2464_09_B41_ID05_01].st2"
    ).read_bytes()
    write(
        ALTERNATES / "Space War 2 (Alt) [AUD_2464_09_B41_ID05_01].st2",
        repaired_space_war_alt,
    )
    write(
        ALTERNATES / "Space War 2 (Alt) [AUD_2464_09_B41_ID05_01].txt",
        b"""Title: Space War 2 (TCNJ header alternate)
Archive ID: AUD_2464_09_B41_ID05_01

Provenance and format:
* The two payload pages exactly match the canonical Hagley Space War 2 entry.
* This alternate retains the TCNJ/Sarnoff title field.
* The inherited copy incorrectly declared four data pages while containing
  two. This retained copy corrects header byte $0004 from $05 to $03 without
  changing its payload; the defective container is preserved under holding.
""",
    )

    write(
        ALTERNATES
        / "Basic Videomate 3 Game Package (Alt) [AUD_2464_09_B41_ID05_02].txt",
        b"""Title: Basic Videomate 3 Game Package (Game Pack header alternate)
Archive ID: AUD_2464_09_B41_ID05_02

Provenance and format:
* Exact Hagley ST2 object. Its four-page payload is byte-for-byte identical to
  the canonical Game Pack; only the 32-byte title field differs from the TCNJ
  Game Pack container.
* This is a provenance-header alternate, not another program version.
""",
    )

    write(
        PROTOTYPES / "Space Explorer (1978) (Thomas Lenihan).txt",
        b"""Title: Space Explorer
Platform: RCA Studio II family
Year: 1978
Author: Thomas Lenihan

Format:
* The ST2 is the canonical runnable form. It maps four pages at $0400-$07FF
  and four more at $0C00-$0FFF.
* The former 2048-byte BIN merely concatenated those two regions and therefore
  mapped its second half incorrectly when loaded as a flat cartridge. It is
  preserved under s2-holding/6 Alternates - Review/Archival composites/
  Space Explorer block-concatenated BIN.
* Both address regions are also retained separately under
  software/hagley-holding/Split components; the high-region ST2 keeps its
  $0C00-$0FFF page map.

Controls:
* Keypad B direction keys: move the center cursor toward a target dot.
* B5: lock on target.
* A0: fire at the target.

Objective:
* Eliminate all nine dots before the timer expires. Hitting a target eventually
  reduces the score; the objective is a low score.

Source:
* Andrew Modla collection notes for space_explorer.
""",
    )
    write(
        ARCHIVAL_COMPOSITES
        / "Space Explorer block-concatenated BIN"
        / "Space Explorer (1978) (Thomas Lenihan).txt",
        b"""Title: Space Explorer block-concatenated BIN (preservation copy)

Status:
* This 2048-byte file is the exact payload-block order of the canonical ST2.
* It concatenates the ST2 regions for $0400-$07FF and $0C00-$0FFF. A flat BIN
  loader places the second region incorrectly, so this form is retained in
  holding and is not a playable fullset entry.
* BIN SHA-256: a568a6bb40fd5cb172ec1a2c424f6bc9a5e2084adb2a531ea22f409518ed33db
""",
    )
    write(
        HEADER_DEFECTS
        / "Space War 2"
        / "Space War 2 (Alt) [AUD_2464_09_B41_ID05_01].txt",
        b"""Title: Space War 2 alternate with defective block count

Status:
* Preserved inherited ST2 container. Header byte $0004 declares four payload
  blocks, but only two blocks are physically present at pages $04 and $05.
* The fullset alternate repairs only byte $0004 from $05 to $03.
* Defective ST2 SHA-256: 08b68e8662d66c77e675ff4142288e63536af0ae35cd0a4d7d916405f49d138b
""",
    )
    write(
        COMPONENTS / "Split components.txt",
        b"""Hagley / prototype split components

These files retain each evidenced address region separately. They are source
components, not all standalone programs:

* Game Pack lower pages are a flat BIN for $0400-$05FF.
* The three Game Pack upper variants are ST2s so they retain $0600-$07FF.
* The Paul's Printer and Color Runs program BINs map at $0400-$07FF and require
  their matching 180 XL-1 resident ROM.
* Space Explorer's low BIN maps at $0400-$07FF. Its high ST2 retains the sparse
  $0C00-$0FFF mapping. The complete Space Explorer ST2 remains the playable
  fullset form.

Use tools/assemble-hagley-studio-ii-iii-variants.py to reproduce every file and
tools/verify-hagley-studio-ii-iii-provenance.py to verify the joins and splits.
""",
    )


if __name__ == "__main__":
    main()
