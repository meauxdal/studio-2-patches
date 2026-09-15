#!/usr/bin/env python3
"""Verify the Hagley/TCNJ Studio II and III binary provenance map."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOLDING = ROOT / "software" / "s2-holding"
HAGLEY = HOLDING / "Hagley Digital Archives"
HAGLEY_WORK = ROOT / "software" / "hagley-holding"
FULLSET = ROOT / "software" / "RCA-Studio-II-Fullset"
PROTOTYPES = FULLSET / "2 Prototypes and Betas"
ALTERNATES = PROTOTYPES / "Alternates"
EMMA = HOLDING / "Emma 02" / "St2" / "StudioII-Sarnoff-Collection"
COMPONENTS = HAGLEY_WORK / "Split components"
ARCHIVAL_COMPOSITES = HOLDING / "6 Alternates - Review" / "Archival composites"
HEADER_DEFECTS = HOLDING / "6 Alternates - Review" / "Header defects"


@dataclass(frozen=True)
class St2:
    data: bytes
    declared_total_blocks: int
    pages: tuple[int, ...]
    payload: bytes


def read(path: Path) -> bytes:
    return path.read_bytes()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_st2_bytes(data: bytes, label: str) -> St2:
    assert data[:4] == b"RCA2", f"not an ST2 container: {label}"
    assert len(data) >= 256 and (len(data) - 256) % 256 == 0, label
    payload = data[256:]
    block_count = len(payload) // 256
    return St2(data, data[4], tuple(data[64 : 64 + block_count]), payload)


def parse_st2(path: Path) -> St2:
    return parse_st2_bytes(read(path), str(path))


def assert_hash(data: bytes, expected: str) -> None:
    assert sha256(data) == expected


def assert_only_byte_changed(before: bytes, after: bytes, offset: int) -> None:
    assert len(before) == len(after)
    assert before[:offset] == after[:offset]
    assert before[offset + 1 :] == after[offset + 1 :]
    assert before[offset] != after[offset]


def verify_id03_new_game_set() -> None:
    source = read(
        HAGLEY / "New Studio 2-5 Game Set [AUD_2464_09_B41_ID03_01].bin"
    )
    companion = parse_st2(
        HAGLEY
        / "New Studio 2-5 Game Set (BA) X2 [AUD_2464_09_B41_ID03_01].st2"
    )
    result_bin = read(
        PROTOTYPES / "New Studio 2-5 Game Set [AUD_2464_09_B41_ID03_01].bin"
    )
    assert len(source) == 0x400
    assert_hash(
        source,
        "f7d72fa0ef3215aebd517bffebd0ebb3dbde0acfafe816ce55ed80d71da33a85",
    )
    assert companion.pages == (0x04, 0x05, 0x06, 0x07)
    assert source == companion.payload == result_bin


def verify_id04_quiz() -> None:
    source_path = HAGLEY / "Studio 2 Quiz (B2-F4) [AUD_2464_09_B41_ID04_02].bin"
    source = parse_st2(source_path)
    result_bin = read(
        ARCHIVAL_COMPOSITES
        / "Quiz ID04_02"
        / "Quiz [AUD_2464_09_B41_ID04_02].bin"
    )
    school = read(
        FULLSET
        / "1 Studio II - MPT-02"
        / "TV School House I (USA) (1977) (Joyce Weisbecker).bin"
    )
    tag_race = parse_st2(
        HAGLEY
        / "Tag Race (82-F4) Joyce 11-76 8 Pages @0000 "
        "[AUD_2464_09_B41_ID17_01].st2"
    ).payload
    assert len(source.data) == 0x500
    assert_hash(
        source.data,
        "53cd4aba4e2ed136face90cf109c17ab9e695610de40845566b936b9dec4fab2",
    )
    assert source.declared_total_blocks == 5
    assert source.pages == (0x04, 0x05, 0x06, 0x07)
    assert source.payload == result_bin
    assert source.payload[:0x200] == school
    assert source.payload[0x200:] == tag_race[0x200:]


def verify_id05_space_war() -> None:
    source_path = (
        HAGLEY
        / "180 Space War (S2-A3) 512 Bytes [AUD_2464_09_B41_ID05_01].bin"
    )
    source = parse_st2(source_path)
    result = read(
        ARCHIVAL_COMPOSITES
        / "Space War ID05_01"
        / "Space War 2 + 3 [AUD_2464_09_B41_ID05_01].st2"
    )
    space_war_2 = parse_st2(
        HOLDING / "Space War 2 [AUD_2464_09_B41_ID05_01].st2"
    )
    emma_space_war_3_label = parse_st2(EMMA / "spacewar-3.st2")
    assert len(source.data) == 0x500
    assert_hash(
        source.data,
        "088d37168dbefe863acb0fabe999c837abd371b92d0a9430bda5ca3672f93051",
    )
    assert source.declared_total_blocks == 5
    assert source.pages == (0x04, 0x05, 0x06, 0x07)
    assert source.data == result
    assert source.payload[:0x200] == space_war_2.payload
    assert source.payload[0x200:] == emma_space_war_3_label.payload
    culled = read(PROTOTYPES / "Space War 2 [AUD_2464_09_B41_ID05_01].bin")
    culled_st2 = parse_st2(
        PROTOTYPES / "Space War 2 [AUD_2464_09_B41_ID05_01].st2"
    )
    assert culled == source.payload[:0x200]
    assert culled_st2.declared_total_blocks == 3
    assert culled_st2.pages == (4, 5)
    assert culled_st2.payload == culled


def verify_standard_four_page_items() -> None:
    rows = (
        (
            "Baseball-2K (80) [AUD_2464_09_B41_ID07].st2",
            "Baseball-2K [AUD_2464_09_B41_ID07].bin",
            None,
        ),
        (
            "Biorhythm [AUD_2464_09_B41_ID08_01].st2",
            "Biorhythm [AUD_2464_09_B41_ID08_01].bin",
            None,
        ),
        (
            "Color Demo (82-F4) [AUD_2464_09_B41_ID09_01].st2",
            "Color Demo [AUD_2464_09_B41_ID09_01].bin",
            "Color Demo (82-F4) [AUD_2464_09_B41_ID09_01].bin",
        ),
        (
            "Colors Stars and Trek (82-Q1) [AUD_2464_09_B41_ID09_02].st2",
            "Colors Stars and Trek [AUD_2464_09_B41_ID09_02].bin",
            "Colors Stars and Trek (82-Q1) [AUD_2464_09_B41_ID09_02].bin",
        ),
        (
            "Gunfight- 8 Page (37 [AUD_2464_09_B41_ID17_02].st2",
            "Gunfight [AUD_2464_09_B41_ID17_02].bin",
            None,
        ),
        (
            "Secret Number [AUD_2464_09_B41_ID08_02].st2",
            "Secret Number [AUD_2464_09_B41_ID08_02].bin",
            "Secret Number [AUD_2464_09_B41_ID08_02].bin",
        ),
    )
    for source_name, result_name, raw_name in rows:
        source = parse_st2(HAGLEY / source_name)
        assert source.declared_total_blocks == 5
        assert source.pages == (0x04, 0x05, 0x06, 0x07)
        assert source.payload == read(PROTOTYPES / result_name)
        if raw_name is not None:
            assert source.payload == read(HAGLEY / raw_name)


def verify_id05_02_game_pack() -> None:
    hagley = parse_st2(
        HAGLEY
        / "180-V6LI-Basic Videomate 3 Game Package (B2-F4) "
        "[AUD_2464_09_B41_ID05_02].st2"
    )
    tcnj = parse_st2(EMMA / "game_pack.st2")
    result_st2 = parse_st2(
        PROTOTYPES
        / "Game Pack (Doodle, Curling, Pong, Addition, Freeway) "
        "(Joseph Weisbecker).st2"
    )
    result_bin = read(
        PROTOTYPES
        / "Game Pack (Doodle, Curling, Pong, Addition, Freeway) "
        "(Joseph Weisbecker).bin"
    )
    hagley_alt = read(
        PROTOTYPES
        / "Alternates"
        / "Basic Videomate 3 Game Package (Alt) [AUD_2464_09_B41_ID05_02].st2"
    )
    assert hagley.pages == tcnj.pages == result_st2.pages == (4, 5, 6, 7)
    assert hagley.payload == tcnj.payload == result_st2.payload == result_bin
    assert hagley.data[:32] == tcnj.data[:32]
    assert hagley.data[32:64] != tcnj.data[32:64]
    assert hagley.data[64:] == tcnj.data[64:]
    assert hagley.data == hagley_alt


def verify_id13_pauls_printer() -> None:
    source = parse_st2(
        HAGLEY
        / "Paul's Printer 8 Pages @0000 180 XL1 [AUD_2464_09_B41_ID13_01].bin"
    )
    result = read(PROTOTYPES / "Paul's Printer [AUD_2464_09_B41_ID13_01].rom")
    inherited_partial = read(
        HAGLEY_WORK / "Paul's Printer [AUD_2464_09_B41_ID13_01].bin"
    )
    assert source.declared_total_blocks == 9
    assert source.pages == tuple(range(8))
    assert source.payload == result
    assert inherited_partial == source.payload[0x100:]
    pauls_resident = source.payload[:0x400]
    assert_hash(
        pauls_resident,
        "9b9dd1528ba59f0ea0ef7e487cc8bd92488641f7d9d47dfef85f2a6905558a9c",
    )
    color_runs_resident = read(
        HAGLEY
        / "180 XL-1 (82-A1) Color Runs (Press 1-2) 8 Pages "
        "[AUD_2464_09_B41_ID16_02].bin"
    )[:0x400]
    differences = tuple(
        offset
        for offset, (pauls_byte, color_runs_byte) in enumerate(
            zip(pauls_resident, color_runs_resident)
        )
        if pauls_byte != color_runs_byte
    )
    assert differences == (0x178, 0x183)
    assert color_runs_resident[0x177:0x179] == bytes((0x3B, 0x53))
    assert pauls_resident[0x177:0x179] == bytes((0x3B, 0x55))
    assert color_runs_resident[0x182:0x184] == bytes((0x3A, 0x53))
    assert pauls_resident[0x182:0x184] == bytes((0x3A, 0x55))


def verify_id14_print_snoopy() -> None:
    source_bin = read(
        HAGLEY / "Print Snoopy (22-A3) [AUD_2464_09_B41_ID14_01].bin"
    )
    companion = parse_st2(
        HAGLEY_WORK / "Print Snoopy [AUD_2464_09_B41_ID14_01].st2"
    )
    repaired = parse_st2(
        PROTOTYPES / "Print Snoopy [AUD_2464_09_B41_ID14_01].st2"
    )
    result_bin = read(
        PROTOTYPES / "Print Snoopy [AUD_2464_09_B41_ID14_01].bin"
    )
    assert len(source_bin) == 0x200
    assert companion.declared_total_blocks == 5
    assert repaired.declared_total_blocks == 3
    assert companion.pages == repaired.pages == (4, 5)
    assert source_bin == companion.payload == repaired.payload == result_bin
    assert_only_byte_changed(companion.data, repaired.data, 4)


def verify_id16_color_runs() -> None:
    source_bin = read(
        HAGLEY
        / "180 XL-1 (82-A1) Color Runs (Press 1-2) 8 Pages "
        "[AUD_2464_09_B41_ID16_02].bin"
    )
    companion = parse_st2(
        HAGLEY
        / "180 XL-1 (82-A1) Color Runs (Press 1-2) 8 Pages "
        "[AUD_2464_09_B41_ID16_02].st2"
    )
    result = read(PROTOTYPES / "Color Runs [AUD_2464_09_B41_ID16_02].rom")
    interpreter = read(
        PROTOTYPES
        / "180 XL-1 Resident Interpreter (Color Runs extraction) "
        "[AUD_2464_09_B41_ID16_02].rom"
    )
    assert companion.declared_total_blocks == 9
    assert companion.pages == tuple(range(8))
    assert source_bin == companion.payload == result
    assert interpreter == source_bin[:0x400]


def verify_id17_01_tag_race() -> None:
    source = parse_st2(
        HAGLEY
        / "Tag Race (82-F4) Joyce 11-76 8 Pages @0000 "
        "[AUD_2464_09_B41_ID17_01].st2"
    )
    result = read(
        ARCHIVAL_COMPOSITES
        / "Tag-Race ID17_01"
        / "Tag-Race (Joyce) [AUD_2464_09_B41_ID17_01].bin"
    )
    released = read(
        FULLSET
        / "1 Studio II - MPT-02"
        / "TV Arcade Series - Speedway + Tag (USA) (1977) "
        "(Joyce Weisbecker).bin"
    )
    quiz = parse_st2(
        HAGLEY / "Studio 2 Quiz (B2-F4) [AUD_2464_09_B41_ID04_02].bin"
    ).payload
    assert source.pages == (4, 5, 6, 7)
    assert source.payload == result
    assert source.payload[:0x200] == released
    assert source.payload[0x200:] == quiz[0x200:]


def verify_shared_game_pack_upper_pages() -> None:
    quiz = parse_st2(
        HAGLEY / "Studio 2 Quiz (B2-F4) [AUD_2464_09_B41_ID04_02].bin"
    ).payload
    tag_race = parse_st2(
        HAGLEY
        / "Tag Race (82-F4) Joyce 11-76 8 Pages @0000 "
        "[AUD_2464_09_B41_ID17_01].st2"
    ).payload
    numbers_source = parse_st2(
        HAGLEY
        / "Numbers (82-F4) 1-2=Bagels, 3=Reverse "
        "[AUD_2464_09_B41_ID12_01].st2"
    ).payload
    game_pack = read(
        PROTOTYPES
        / "Game Pack (Doodle, Curling, Pong, Addition, Freeway) "
        "(Joseph Weisbecker).bin"
    )
    space_war = parse_st2(
        HAGLEY
        / "180 Space War (S2-A3) 512 Bytes [AUD_2464_09_B41_ID05_01].bin"
    ).payload

    shared = quiz[0x200:]
    game_pack_upper = game_pack[0x200:]
    assert shared == tag_race[0x200:]
    assert_hash(
        shared,
        "11eee1271289c99cbe46f23f3efc7678385d46d4cbc768b1ea81330effa81187",
    )
    assert numbers_source[0x200:] == game_pack_upper
    assert_hash(
        game_pack_upper,
        "df3d798dcfd309090dbecd62c379b3ef7562b590344a90b2e0380ebf52c7aa1a",
    )
    assert tuple(
        offset
        for offset, pair in enumerate(zip(shared, game_pack_upper))
        if pair[0] != pair[1]
    ) == (0x82, 0xA5, 0xF2)
    assert tuple(
        offset
        for offset, pair in enumerate(zip(shared, space_war[0x200:]))
        if pair[0] != pair[1]
    ) == (0x82, 0xA5, 0xF2, 0x1E5, 0x1EB, 0x1FF)

    # Game Pack's key-selection stubs enter all four upper-page game regions.
    assert game_pack[0xF1:0xF9] == bytes.fromhex("17 60 16 DD 17 E2 17 F4")
    # The upper pages are not standalone: their code calls back into lower pages.
    assert game_pack[0x341:0x343] == shared[0x141:0x143] == bytes.fromhex("25 9A")
    assert game_pack[0x3F2:0x3F4] == shared[0x1F2:0x1F4] == bytes.fromhex("14 57")


def verify_assembled_variants_and_split_components() -> None:
    game_pack = read(
        PROTOTYPES
        / "Game Pack (Doodle, Curling, Pong, Addition, Freeway) "
        "(Joseph Weisbecker).bin"
    )
    quiz = parse_st2(
        HAGLEY / "Studio 2 Quiz (B2-F4) [AUD_2464_09_B41_ID04_02].bin"
    ).payload
    space_war = parse_st2(
        HAGLEY
        / "180 Space War (S2-A3) 512 Bytes [AUD_2464_09_B41_ID05_01].bin"
    ).payload
    quiz_variant_name = (
        "Game Pack (Quiz and Tag-Race upper-page variant) "
        "[AUD_2464_09_B41_ID04_02, ID17_01]"
    )
    space_war_variant_name = (
        "Game Pack (Space War upper-page variant) "
        "[AUD_2464_09_B41_ID05_01]"
    )
    quiz_variant = read(ALTERNATES / f"{quiz_variant_name}.bin")
    quiz_variant_st2 = parse_st2(ALTERNATES / f"{quiz_variant_name}.st2")
    space_war_variant = read(ALTERNATES / f"{space_war_variant_name}.bin")
    space_war_variant_st2 = parse_st2(
        ALTERNATES / f"{space_war_variant_name}.st2"
    )

    assert quiz_variant == game_pack[:0x200] + quiz[0x200:]
    assert space_war_variant == game_pack[:0x200] + space_war[0x200:]
    assert quiz_variant_st2.pages == space_war_variant_st2.pages == (4, 5, 6, 7)
    assert quiz_variant_st2.payload == quiz_variant
    assert space_war_variant_st2.payload == space_war_variant
    assert_hash(
        quiz_variant,
        "a5aef0a4faea97fd600a24974ff6e03283f26de1490b3bce8ef6a1627170e5f2",
    )
    assert_hash(
        space_war_variant,
        "7450d2e96129822d00fa122638981604cdba4d9dd27ff62040d8324a9d9301ca",
    )

    lower = read(
        COMPONENTS
        / "Game Pack lower pages $0400-$05FF [AUD_2464_09_B41_ID05_02].bin"
    )
    original_upper = parse_st2(
        COMPONENTS
        / "Game Pack upper pages $0600-$07FF [AUD_2464_09_B41_ID05_02].st2"
    )
    quiz_upper = parse_st2(
        COMPONENTS
        / "Game Pack upper pages $0600-$07FF (Quiz and Tag-Race variant) "
        "[AUD_2464_09_B41_ID04_02, ID17_01].st2"
    )
    space_war_upper = parse_st2(
        COMPONENTS
        / "Game Pack upper pages $0600-$07FF (Space War variant) "
        "[AUD_2464_09_B41_ID05_01].st2"
    )
    assert lower == game_pack[:0x200]
    assert original_upper.pages == quiz_upper.pages == space_war_upper.pages == (6, 7)
    assert lower + original_upper.payload == game_pack
    assert lower + quiz_upper.payload == quiz_variant
    assert lower + space_war_upper.payload == space_war_variant

    pauls_printer = read(
        PROTOTYPES / "Paul's Printer [AUD_2464_09_B41_ID13_01].rom"
    )
    color_runs = read(
        PROTOTYPES / "Color Runs [AUD_2464_09_B41_ID16_02].rom"
    )
    pauls_resident = read(
        ALTERNATES
        / "180 XL-1 Resident Interpreter (Paul's Printer extraction) "
        "[AUD_2464_09_B41_ID13_01].rom"
    )
    color_runs_resident = read(
        PROTOTYPES
        / "180 XL-1 Resident Interpreter (Color Runs extraction) "
        "[AUD_2464_09_B41_ID16_02].rom"
    )
    pauls_program = read(
        COMPONENTS
        / "Paul's Printer program pages $0400-$07FF "
        "[AUD_2464_09_B41_ID13_01].bin"
    )
    color_runs_program = read(
        COMPONENTS
        / "Color Runs program pages $0400-$07FF "
        "[AUD_2464_09_B41_ID16_02].bin"
    )
    assert pauls_resident == pauls_printer[:0x400]
    assert color_runs_resident == color_runs[:0x400]
    assert pauls_program == pauls_printer[0x400:]
    assert color_runs_program == color_runs[0x400:]
    assert pauls_resident + pauls_program == pauls_printer
    assert color_runs_resident + color_runs_program == color_runs


def verify_culled_prototype_set() -> None:
    numbers_source = parse_st2(
        HAGLEY
        / "Numbers (82-F4) 1-2=Bagels, 3=Reverse "
        "[AUD_2464_09_B41_ID12_01].st2"
    )
    numbers = read(PROTOTYPES / "Numbers [AUD_2464_09_B41_ID12_01].bin")
    numbers_st2 = parse_st2(
        PROTOTYPES / "Numbers [AUD_2464_09_B41_ID12_01].st2"
    )
    assert numbers == numbers_source.payload[:0x200]
    assert numbers_st2.declared_total_blocks == 3
    assert numbers_st2.pages == (4, 5)
    assert numbers_st2.payload == numbers
    assert_hash(
        numbers,
        "419ef74835a5d0554f6ec3138402c14080afc0b4c81feca270e0f6c0273c241a",
    )
    assert (
        read(
            ARCHIVAL_COMPOSITES
            / "Numbers ID12_01"
            / "Numbers [AUD_2464_09_B41_ID12_01].bin"
        )
        == numbers_source.payload
    )

    space_explorer = parse_st2(
        PROTOTYPES / "Space Explorer (1978) (Thomas Lenihan).st2"
    )
    assert space_explorer.declared_total_blocks == 9
    assert space_explorer.pages == (4, 5, 6, 7, 0x0C, 0x0D, 0x0E, 0x0F)
    assert not (PROTOTYPES / "Space Explorer (1978) (Thomas Lenihan).bin").exists()
    block_bin = read(
        ARCHIVAL_COMPOSITES
        / "Space Explorer block-concatenated BIN"
        / "Space Explorer (1978) (Thomas Lenihan).bin"
    )
    assert block_bin == space_explorer.payload
    low = read(COMPONENTS / "Space Explorer region $0400-$07FF (Thomas Lenihan).bin")
    high = parse_st2(
        COMPONENTS / "Space Explorer region $0C00-$0FFF (Thomas Lenihan).st2"
    )
    assert low == space_explorer.payload[:0x400]
    assert high.pages == (0x0C, 0x0D, 0x0E, 0x0F)
    assert high.payload == space_explorer.payload[0x400:]
    assert_hash(
        low,
        "060475138169f1908be11b99ec920b9c5839415326577573feea6479b6a8caa3",
    )
    assert_hash(
        high.payload,
        "4a0f9ca5b95e130714d57ca9f777f04c5f446a3d6cf2d31d44d2d04b0c46f477",
    )

    absent_stems = (
        "Quiz [AUD_2464_09_B41_ID04_02]",
        "Tag-Race (Joyce) [AUD_2464_09_B41_ID17_01]",
        "Space War 2 + 3 [AUD_2464_09_B41_ID05_01]",
    )
    for stem in absent_stems:
        assert not any(
            path.is_file() and path.stem == stem for path in PROTOTYPES.iterdir()
        )

    binary_extensions = {".bin", ".rom", ".st2"}
    excluded_fullset_hashes = {
        "f99591c280e9f29ff98889e87d23306bfa980e730d367e2307dc0a55fcee4110",
        "53cd4aba4e2ed136face90cf109c17ab9e695610de40845566b936b9dec4fab2",
        "2c09bd0b585c3c52ad727e52f11b676ef267335860608dd5ebcbb55e8fac74c6",
        "9ae8353fcb4e5d83f455a8acd135b8fddf8c2ea93a02f81f4a367e70bd5d9a22",
        "2287da62bd0ee845683f9873b06d3d7c813ea95102ab2025ec74c9c99a7fb08b",
        "73833f33891d5af1e6f5090b28350451a549d88be8f66ff006e4c4c73981ca52",
        "088d37168dbefe863acb0fabe999c837abd371b92d0a9430bda5ca3672f93051",
        "a568a6bb40fd5cb172ec1a2c424f6bc9a5e2084adb2a531ea22f409518ed33db",
        "08b68e8662d66c77e675ff4142288e63536af0ae35cd0a4d7d916405f49d138b",
    }
    for path in PROTOTYPES.rglob("*"):
        if path.is_file() and path.suffix.lower() in binary_extensions:
            assert path.with_suffix(".txt").exists(), f"missing note for {path}"
            assert sha256(read(path)) not in excluded_fullset_hashes, path
        if path.is_file() and path.suffix.lower() == ".st2":
            st2 = parse_st2(path)
            physical_total_blocks = 1 + len(st2.payload) // 256
            assert st2.declared_total_blocks == physical_total_blocks, path
            assert len(set(st2.pages)) == len(st2.pages), path

    defective_alt = (
        HEADER_DEFECTS
        / "Space War 2"
        / "Space War 2 (Alt) [AUD_2464_09_B41_ID05_01].st2"
    )
    repaired_alt = parse_st2(
        ALTERNATES / "Space War 2 (Alt) [AUD_2464_09_B41_ID05_01].st2"
    )
    defective_alt_data = read(defective_alt)
    assert defective_alt_data[4] == 5
    assert repaired_alt.declared_total_blocks == 3
    assert repaired_alt.pages == (4, 5)
    assert defective_alt_data[256:] == repaired_alt.payload
    assert_only_byte_changed(defective_alt_data, repaired_alt.data, 4)


def verify_tcnj_st3cta() -> None:
    source = parse_st2(HAGLEY / "ST3CTA Tester 3 Cartridge.st2")
    result_bin = read(
        FULLSET / "2 Other" / "ST3CTA Test Cartridge - Tester 3 (197x) (unknown).bin"
    )
    result_st2 = read(
        FULLSET / "2 Other" / "ST3CTA Test Cartridge - Tester 3 (197x) (unknown).st2"
    )
    assert source.declared_total_blocks == 13
    assert source.pages == (
        0x00,
        0x01,
        0x02,
        0x03,
        0x24,
        0x25,
        0x26,
        0x27,
        0x2C,
        0x2D,
        0x2E,
        0x2F,
    )
    assert source.data == result_st2
    assert source.payload == result_bin


def verify_id33_01_tv_tennis() -> None:
    source_path = (
        HAGLEY
        / "Studio II-TV Tennis (ANDY) 8Pages@0000 [AUD_2464_09_B41_ID33_01].bin"
    )
    source = parse_st2(source_path)
    repaired = parse_st2(
        PROTOTYPES / "TV Tennis (ANDY) [AUD_2464_09_B41_ID33_01].st2"
    )
    result_bin = read(
        PROTOTYPES / "TV Tennis (ANDY) [AUD_2464_09_B41_ID33_01].bin"
    )
    inherited_half = read(
        HAGLEY_WORK / "TV Tennis (ANDY) [AUD_2464_09_B41_ID33_01].bin"
    )
    assert len(source.data) == 0x500
    assert_hash(
        source.data,
        "6953879de16511310f1d165281936de801f826fe3b40e4390bb50587db1bebd4",
    )
    assert source.declared_total_blocks == 3
    assert repaired.declared_total_blocks == 5
    assert source.pages == repaired.pages == (0x04, 0x05, 0x06, 0x07)
    assert source.payload == repaired.payload == result_bin
    assert inherited_half == source.payload[:0x200]
    assert_only_byte_changed(source.data, repaired.data, 4)


def verify_id33_02_unidentified_side() -> None:
    source = read(
        HAGLEY
        / "Studio II-TV Tennis -Unidentified Side 02 [AUD_2464_09_B41_ID33_02].bin"
    )
    companion = parse_st2(
        HAGLEY_WORK
        / "TV Tennis (Unidentified Side 02) [AUD_2464_09_B41_ID33_02].st2"
    )
    classified = parse_st2(
        HOLDING
        / "6 Alternates - Review"
        / "Non-standalone fragments"
        / "FRED 1.5 Tape Software [AUD_2464_09_B41_ID33_02].st2"
    )
    result_bin = read(
        HOLDING
        / "6 Alternates - Review"
        / "Non-standalone fragments"
        / "FRED 1.5 Tape Software [AUD_2464_09_B41_ID33_02].bin"
    )
    assert len(source) == 0xFB
    assert_hash(
        source,
        "8d14312c225d12aaf6dd2dd12e5c0a7c54a589345a68fc1d81f00132c5222c4b",
    )
    assert companion.declared_total_blocks == 3
    assert companion.pages == (0x04,)
    assert companion.payload == source + b"\0" * 5
    assert classified.declared_total_blocks == 2
    assert classified.pages == (0x04,)
    assert classified.payload == companion.payload == result_bin
    assert_only_byte_changed(companion.data, classified.data, 4)


def main() -> None:
    checks = (
        verify_id03_new_game_set,
        verify_id04_quiz,
        verify_id05_space_war,
        verify_standard_four_page_items,
        verify_id05_02_game_pack,
        verify_id13_pauls_printer,
        verify_id14_print_snoopy,
        verify_id16_color_runs,
        verify_id17_01_tag_race,
        verify_shared_game_pack_upper_pages,
        verify_assembled_variants_and_split_components,
        verify_culled_prototype_set,
        verify_id33_01_tv_tennis,
        verify_id33_02_unidentified_side,
        verify_tcnj_st3cta,
    )
    for check in checks:
        check()
        print(f"PASS {check.__name__}")
    print(f"PASS all {len(checks)} Studio II/III provenance checks")


if __name__ == "__main__":
    main()
