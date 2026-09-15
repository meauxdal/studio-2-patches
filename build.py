#!/usr/bin/env python3
"""Build usable binary derivatives from canonical Hagley downloads."""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "derived"


def accession_dir(accession: str) -> Path:
    return Path(f"AUD_2464_09_B41_{accession}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_plain_text_sidecar(data: bytes) -> bool:
    if not data:
        return True
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return all(character.isprintable() or character in "\r\n\t" for character in text)


@dataclass(frozen=True)
class St2:
    data: bytes
    pages: tuple[int, ...]
    payload: bytes


def parse_st2(data: bytes) -> St2:
    if len(data) < 256 or data[:4] != b"RCA2":
        raise ValueError("not an RCA2/ST2 container")
    declared_blocks = data[4]
    if declared_blocks < 2:
        raise ValueError(f"invalid ST2 block count {declared_blocks}")
    physical_pages = (len(data) - 256) // 256
    if len(data) != 256 + physical_pages * 256:
        raise ValueError("ST2 payload is not page aligned")
    pages = tuple(data[64 : 64 + physical_pages])
    if len(set(pages)) != len(pages):
        raise ValueError("ST2 page table contains duplicate addresses")
    return St2(data, pages, data[256:])


def make_st2(payload: bytes, pages: tuple[int, ...], title: bytes) -> bytes:
    if len(payload) != 256 * len(pages):
        raise ValueError("payload length does not match the ST2 page table")
    if len(title) > 32:
        raise ValueError("ST2 title field exceeds 32 bytes")
    header = bytearray(256)
    header[:4] = b"RCA2"
    header[4] = len(pages) + 1
    header[5] = 1
    header[8:12] = b"JWMT"
    header[32 : 32 + len(title)] = title
    header[64 : 64 + len(pages)] = bytes(pages)
    return bytes(header) + payload


def payload(data: bytes, pages: tuple[int, ...]) -> bytes:
    if data[:4] != b"RCA2":
        if len(data) != 256 * len(pages):
            raise ValueError(
                f"expected {len(pages)} raw pages, found {len(data)} bytes"
            )
        return data
    parsed = parse_st2(data)
    if parsed.pages != pages:
        raise ValueError(
            f"expected ST2 pages {pages}, found {parsed.pages}"
        )
    return parsed.payload


def parse_intel_hex(data: bytes) -> bytes:
    """Decode a contiguous Intel HEX image and verify every record checksum."""
    memory: dict[int, int] = {}
    upper = 0
    saw_eof = False
    for line_number, raw_line in enumerate(data.splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        if not line.startswith(b":"):
            raise ValueError(f"Intel HEX line {line_number} does not start with ':'")
        try:
            record = bytes.fromhex(line[1:].decode("ascii"))
        except (UnicodeDecodeError, ValueError) as error:
            raise ValueError(f"invalid Intel HEX at line {line_number}") from error
        if len(record) < 5 or len(record) != record[0] + 5:
            raise ValueError(f"invalid Intel HEX length at line {line_number}")
        if sum(record) & 0xFF:
            raise ValueError(f"Intel HEX checksum failed at line {line_number}")
        count = record[0]
        address = int.from_bytes(record[1:3], "big")
        kind = record[3]
        body = record[4 : 4 + count]
        if kind == 0:
            for offset, value in enumerate(body):
                absolute = upper + address + offset
                if absolute in memory:
                    raise ValueError(f"overlapping Intel HEX data at {absolute:#x}")
                memory[absolute] = value
        elif kind == 1:
            saw_eof = True
        elif kind == 2:
            if len(body) != 2:
                raise ValueError("invalid Intel HEX segment-address record")
            upper = int.from_bytes(body, "big") << 4
        elif kind == 4:
            if len(body) != 2:
                raise ValueError("invalid Intel HEX linear-address record")
            upper = int.from_bytes(body, "big") << 16
        elif kind not in (3, 5):
            raise ValueError(f"unsupported Intel HEX record type {kind}")
    if not saw_eof or not memory:
        raise ValueError("Intel HEX image is empty or has no EOF record")
    first, last = min(memory), max(memory)
    if first != 0 or len(memory) != last + 1:
        raise ValueError(f"Intel HEX image is not contiguous from zero: {first:#x}-{last:#x}")
    return bytes(memory[address] for address in range(last + 1))

SOURCE_HASHES: dict[str, frozenset[str]] = {
    "ID03_01": frozenset({
        "60240a06b9baf54257b61ebd97e40ef74b8a295bbc31311cb188cc3e2a712889",
    }),
    "ID04_02": frozenset({
        "53cd4aba4e2ed136face90cf109c17ab9e695610de40845566b936b9dec4fab2",
    }),
    "ID05_01": frozenset({
        "088d37168dbefe863acb0fabe999c837abd371b92d0a9430bda5ca3672f93051",
    }),
    "ID05_02": frozenset({
        "680c4e032e009864847dbc5e2ac77df0fd467330108313dea11f2ccc3417c9d3",
    }),
    "ID06_01": frozenset({
        "0f615a35dc32c2f5698e8acbf342e429ef851a3670c390ea4f30f0b6b66d9ad4",
    }),
    "ID06_02": frozenset({
        "5ab697da25b5de74d8433614b6fda8b4af67764293827de0e5731764431d0ef9",
    }),
    "ID07": frozenset({
        "82ee252b9003bcff895ff00c163ad650ae5cde05e52684ba3f1338fe5d421079",
    }),
    "ID08_01": frozenset({
        "7c134efa56f2cde8c238e83dc3e50efecc91a8c32f44f9ba3fb18d097291568b",
    }),
    "ID08_02": frozenset({
        "0c156614054447e02c96db798bd0e3c953919e1fbaeaf5ef94ca070ada106e7a",
    }),
    "ID09_01": frozenset({
        "f8185ab78469dcd14453ed81f97c44c6dbe6c131eebcb981236346286c915e79",
    }),
    "ID09_02": frozenset({
        "8c95a7f749cb0e46ee82b3c2018d8bb671023f90adc2d6976544506a3f4ffbbf",
    }),
    "ID12_01": frozenset({
        "73833f33891d5af1e6f5090b28350451a549d88be8f66ff006e4c4c73981ca52",
    }),
    "ID13_01": frozenset({
        "667954da803715a25a8d5559349a4f1a75b8560a8f229b9a994961d43b0a06bb",
    }),
    "ID14_01": frozenset({
        "f103f5a39b1ed7fe53f6317ce901b09dba97730c4bad92c8c1b78fab524c4c75",
    }),
    "ID15_01": frozenset({
        "75e2d7d31056a78a415f64b97248dd78830be40e7d6cc8f01605b6f27510c1c0",
    }),
    "ID16_02": frozenset({
        "4c4f2058b3bb412db8edf1eea9b490a63b7f185a58816c31611372acf4f49826",
    }),
    "ID17_01": frozenset({
        "9ae8353fcb4e5d83f455a8acd135b8fddf8c2ea93a02f81f4a367e70bd5d9a22",
    }),
    "ID17_02": frozenset({
        "9305538e7cdabfc78e1d2742b76b2372ae53110412210ce354e8eca7c3713bb5",
    }),
    "ID20_01": frozenset({
        "66160413301e7476c125ff6add429fe4c6dc78cfca240130468d189af04220e7",
    }),
    "ID21_02": frozenset({
        "c17bb25fad23b73b4117895399f5bd9d269492446b9d5d10d398c508689fc8ca",
    }),
    "ID26_01_1": frozenset({
        "9df7ea9e055b5e4c5a1429bf24c1cb318ef4052977453285424e11ca76b40987",
    }),
    "ID26_02_2": frozenset({
        "26c1fb4e585a6edfa8e4f36c8ab778920ab9b5799879d35b195a176f7472c87c",
    }),
    "ID27_01_2": frozenset({
        "918418c96e2a9da2541eed7858a3f86af22d554fd73b42d747423f68c4340857",
    }),
    "ID32_01_2": frozenset({
        "9a447bdc3cd0c50cfa3a4459f6a3c1499b29dab186e9472c6acaf4749332d494",
    }),
    "ID33_01": frozenset({
        "6953879de16511310f1d165281936de801f826fe3b40e4390bb50587db1bebd4",
    }),
    "ID10": frozenset({
        "2bba48ca1e49cd48112a4240ad5c5ccce7e12e8d55b09169b591cb0f59099a47",
    }),
    "ID13_02": frozenset({
        "55484365a66c56327622b66ed77a31bfde7336f3b2a0b53c6f0ba8226f68e1d0",
    }),
    "ID16_01": frozenset({
        "44db71ad57ba04c5fcdad739c815c28ab0e50c46b3697c1768ef026ab6a41a2e",
    }),
    "ID33_02": frozenset({
        "8d14312c225d12aaf6dd2dd12e5c0a7c54a589345a68fc1d81f00132c5222c4b",
    }),
}


# Hashes are part of the recipe: a changed transformation fails before writing.
OUTPUT_HASHES: dict[str, str] = {
    "New Studio 2-5 Game Set.bin": "f7d72fa0ef3215aebd517bffebd0ebb3dbde0acfafe816ce55ed80d71da33a85",
    "New Studio 2-5 Game Set.st2": "31e646300d547ab26ccc58fc87c492a5f4837558238a4ce412d6a1310f418f03",
    "Baseball-2K.bin": "0264f192cbaac2631b69b2e658d2354506b10ba82933eca816c41636eb143a2c",
    "Baseball-2K.st2": "82ee252b9003bcff895ff00c163ad650ae5cde05e52684ba3f1338fe5d421079",
    "Biorhythm.bin": "b87ef737f560b67a264b22d6ccaab79e462945fd5dafda9e86e6fc80e5e8b51b",
    "Biorhythm.st2": "17390f3f0e2b420683fa8f2e2f7f76fe26226b3d78644c960ec4c0aa64805863",
    "Secret Number.bin": "08b27f303e1e7707096d5950ba1717edccbdf7a8072ed338ff57dad6437b4fb8",
    "Secret Number.st2": "0c156614054447e02c96db798bd0e3c953919e1fbaeaf5ef94ca070ada106e7a",
    "Color Demo.bin": "1c998ef575fc4c5b10b61f14104c1e64b017f86f00dc5ad5e83fdec23f5ac546",
    "Color Demo.st2": "f8185ab78469dcd14453ed81f97c44c6dbe6c131eebcb981236346286c915e79",
    "Colors Stars and Trek.bin": "ca6e04260fdf71a30096b492944f637c1738628e3e340b8616c54cdc4aaafdba",
    "Colors Stars and Trek.st2": "8c95a7f749cb0e46ee82b3c2018d8bb671023f90adc2d6976544506a3f4ffbbf",
    "Numbers.bin": "419ef74835a5d0554f6ec3138402c14080afc0b4c81feca270e0f6c0273c241a",
    "Numbers.st2": "dfaa54602e15fbecdd5bc9d49ce3faad5123b6caa5e2c8de738e3211f52b91b1",
    "Paul's Printer.rom": "47d62cfaa6b0c31d485ef543976a2f732c64c8a95367c1d971a50f0f94371323",
    "Paul's resident.rom": "9b9dd1528ba59f0ea0ef7e487cc8bd92488641f7d9d47dfef85f2a6905558a9c",
    "Print Snoopy.bin": "f103f5a39b1ed7fe53f6317ce901b09dba97730c4bad92c8c1b78fab524c4c75",
    "Print Snoopy.st2": "dc5ecd2ae0059952bc8cb5b8842233755c3d61ad9012e8e833db29006cff0baa",
    "Color Runs.rom": "50e4abe8b4449d2f284a15b732509ce7856ea537bd4817dd58ddbd6460a91e15",
    "Color Runs resident.rom": "6765e9ed45f6375b6d1fac21f44653e4bf3d826b81020a64ec21e23e4574d5a6",
    "Gunfight.bin": "9d5cd31e13d393eb96cfb4b125e1fe58b4bd11379e0ac6f8a73c1804207362ef",
    "Gunfight.st2": "9305538e7cdabfc78e1d2742b76b2372ae53110412210ce354e8eca7c3713bb5",
    "Space War.bin": "fd26fa0e1c4a3a611684088175170b5a1f8b3dac5a0c58306ecfc98c407c1703",
    "Space War.st2": "8bd39731a0c7f64ba4612755ea2def9fda61aa93ca6d2ef65f23a5f8c86cc4be",
    "Game Pack.bin": "05a941a757db1b5ef0e46f7501eae2cf3c9ed3bba978a96b6713b04c3554727d",
    "Basic Videomate Game Pack.st2": "680c4e032e009864847dbc5e2ac77df0fd467330108313dea11f2ccc3417c9d3",
    "Game Pack quiz.bin": "a5aef0a4faea97fd600a24974ff6e03283f26de1490b3bce8ef6a1627170e5f2",
    "Game Pack quiz.st2": "0de9701c6bba7cff17aaf4721e93bd00203c6a408fd36d85a30de4c2c4d8b3da",
    "Game Pack space.bin": "7450d2e96129822d00fa122638981604cdba4d9dd27ff62040d8324a9d9301ca",
    "Game Pack space.st2": "5bcf3f0f717788386c6cad729c51377e1ed5ab9199a36e766fbae0a3898c03c2",
    "TV Tennis.bin": "14eae0eeb44118a5984d07feffc7d331351e53b57f7c1a88c8b0a5ed7d540c3f",
    "TV Tennis.st2": "b08b8256b310197bd65ec3c13e7f50753ef1ce3bfe10f7bba2cc52b5726ea35f",
    "Color Etch.rom": "2bba48ca1e49cd48112a4240ad5c5ccce7e12e8d55b09169b591cb0f59099a47",
    "180 XL-1.rom": "55484365a66c56327622b66ed77a31bfde7336f3b2a0b53c6f0ba8226f68e1d0",
    "Snoopy Snipe Shoot.rom": "712c36ff83a23df3c742b9e6d3aa0480bb52b050fe6d52605f5ecf133c59c9db",
    "FRED 1.5 fragment.bin": "38fbfa3bb6abf2776eefd55941a702d858e74d32cc5fd5b79c1f3140f825abca",
    "FRED 1.5 fragment.st2": "ad9423d4a34ed51ff72a0bbbf1f402fa31d8f8011830fe2b047d0f303ab5c3e3",
    "TV School House I.bin": "c0d9d9a3a05e773b9d9561bb386f4ac824596d52304a12748ee14650716075a3",
    "Speedway and Tag.bin": "4d5b8fb8bcf2212ee574842d5a0972560a94c3c39630f73a486453fbbf401df0",
    "Coin Bowling.arc": "0f615a35dc32c2f5698e8acbf342e429ef851a3670c390ea4f30f0b6b66d9ad4",
    "Computer Bowling.bin": "2bf1091bf7a0ce231bd1dbf275c80116b65aed6064dc1dfd240a91aa2343f4f9",
    "Shrink.bin": "75e2d7d31056a78a415f64b97248dd78830be40e7d6cc8f01605b6f27510c1c0",
    "VIP Pinball.ch8": "5b3d8958165ce99e7fe2d2b7f3a34874867e8933bfd5c8caad242732f84dfb4f",
    "4096 Bit Picture.bin": "c17bb25fad23b73b4117895399f5bd9d269492446b9d5d10d398c508689fc8ca",
    "COSMAC VIP Monitor.rom": "9df7ea9e055b5e4c5a1429bf24c1cb318ef4052977453285424e11ca76b40987",
    "FPL-4 Race Example.bin": "26c1fb4e585a6edfa8e4f36c8ab778920ab9b5799879d35b195a176f7472c87c",
    "FEL-1 Example.bin": "918418c96e2a9da2541eed7858a3f86af22d554fd73b42d747423f68c4340857",
    "Snoopy COSMAC Picture.ch8": "038442ad806b90d3de30bb5b78e855107426ca8165661f131b84bbe7915f014d",
}


def checked(label: str, data: bytes) -> bytes:
    actual = sha256(data)
    expected = OUTPUT_HASHES[label]
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, produced {actual}")
    return data


def accession_from_name(name: str) -> str | None:
    marker = "AUD_2464_09_B41_"
    upper = name.upper()
    start = upper.find(marker)
    if start < 0:
        return None
    tail = upper[start + len(marker) :]
    token = []
    for char in tail:
        if char.isdigit() or char == "_" or char == "I" or char == "D":
            token.append(char)
        else:
            break
    value = "".join(token).rstrip("_")
    return value if value.startswith("ID") else None


def discover(source_dirs: tuple[Path, ...]) -> tuple[dict[str, bytes], list[str]]:
    found: dict[str, bytes] = {}
    notes: list[str] = []
    for source_dir in source_dirs:
        if not source_dir.is_dir():
            raise FileNotFoundError(f"source directory does not exist: {source_dir}")
        for path in sorted(p for p in source_dir.iterdir() if p.is_file()):
            accession = accession_from_name(path.name)
            if accession is None:
                continue
            data = path.read_bytes()
            digest = sha256(data)
            accepted = SOURCE_HASHES.get(accession)
            if accepted is None:
                notes.append(
                    f"unmapped {accession}: {path.name} ({len(data)} bytes, {digest})"
                )
                continue
            if digest not in accepted:
                if is_plain_text_sidecar(data):
                    continue
                notes.append(
                    f"unrecognized version {accession}: {path.name} "
                    f"({len(data)} bytes, {digest})"
                )
                continue
            if accession in found:
                raise ValueError(f"more than one canonical input for {accession}")
            found[accession] = data
    return found, notes


def four_page(
    sources: dict[str, bytes],
    accession: str,
    stem: str,
    title: bytes,
    outputs: dict[Path, bytes],
) -> None:
    if accession not in sources:
        return
    data = sources[accession]
    if data[:4] != b"RCA2" and len(data) == 0x800 and accession in {
        "ID03_01",
        "ID08_01",
    }:
        raw = data[0x400:]
    else:
        raw = payload(data, (4, 5, 6, 7))
    container = data if data[:4] == b"RCA2" else make_st2(raw, (4, 5, 6, 7), title)
    hash_stem = stem.partition(" [AUD_")[0]
    outputs[accession_dir(accession) / f"{stem}.bin"] = checked(
        f"{hash_stem}.bin", raw
    )
    outputs[accession_dir(accession) / f"{stem}.st2"] = checked(
        f"{hash_stem}.st2", container
    )


def build(sources: dict[str, bytes]) -> dict[Path, bytes]:
    outputs: dict[Path, bytes] = {}

    four_page(
        sources,
        "ID03_01",
        "New Studio 2-5 Game Set [AUD_2464_09_B41_ID03_01]",
        b"2-5 GAME SET 2464_09_B41_ID03_01",
        outputs,
    )

    if "ID04_02" in sources:
        quiz = payload(sources["ID04_02"], (4, 5, 6, 7))
        outputs[
            accession_dir("ID04_02")
            / "TV School House I (USA) (1977) (Joyce Weisbecker).bin"
        ] = checked("TV School House I.bin", quiz[:0x200])

    if "ID17_01" in sources:
        tag_race = payload(sources["ID17_01"], (4, 5, 6, 7))
        outputs[
            accession_dir("ID17_01")
            / "TV Arcade Series - Speedway + Tag (USA) (1977) "
            "(Joyce Weisbecker).bin"
        ] = checked("Speedway and Tag.bin", tag_race[:0x200])
    four_page(
        sources,
        "ID07",
        "Baseball-2K [AUD_2464_09_B41_ID07]",
        b"Baseball 2K\0\0" + b"2464_09_B41_ID07",
        outputs,
    )
    four_page(
        sources,
        "ID08_01",
        "Biorhythm [AUD_2464_09_B41_ID08_01]",
        b"BIORHYTHM\0\0\0\0" + b"2464_09_B41_ID08_01",
        outputs,
    )
    four_page(
        sources,
        "ID08_02",
        "Secret Number [AUD_2464_09_B41_ID08_02]",
        b"SECRET NUMBER2464_09_B41_ID08_02",
        outputs,
    )
    four_page(
        sources,
        "ID09_01",
        "Color Demo [AUD_2464_09_B41_ID09_01]",
        b"Color Demo\0\0\0" + b"2464_09_B41_ID09_01",
        outputs,
    )
    four_page(
        sources,
        "ID09_02",
        "Colors Stars and Trek [AUD_2464_09_B41_ID09_02]",
        # The archival header says ID09_01.  Preserve it byte-for-byte.
        b"Stars & Trek\0" + b"2464_09_B41_ID09_01",
        outputs,
    )
    four_page(
        sources,
        "ID17_02",
        "Gunfight [AUD_2464_09_B41_ID17_02]",
        b"Gunfight\0\0\0\0\0" + b"2464_09_B41_ID17_02",
        outputs,
    )

    if "ID12_01" in sources:
        raw = payload(sources["ID12_01"], (4, 5, 6, 7))[:0x200]
        st2 = make_st2(
            raw, (4, 5), b"Numbers\0\0\0\0\0\0" + b"2464_09_B41_ID12_01"
        )
        stem = "Numbers [AUD_2464_09_B41_ID12_01]"
        outputs[accession_dir("ID12_01") / f"{stem}.bin"] = checked(
            "Numbers.bin", raw
        )
        outputs[accession_dir("ID12_01") / f"{stem}.st2"] = checked(
            "Numbers.st2", st2
        )

    if "ID13_01" in sources:
        raw = payload(sources["ID13_01"], tuple(range(8)))
        outputs[
            accession_dir("ID13_01")
            / "Paul's Printer [AUD_2464_09_B41_ID13_01].rom"
        ] = checked(
            "Paul's Printer.rom", raw
        )
        resident = raw[:0x400]
        outputs[
            accession_dir("ID13_01")
            / "180 XL-1 Resident Interpreter (Paul's Printer extraction) "
            "[AUD_2464_09_B41_ID13_01].rom"
        ] = checked("Paul's resident.rom", resident)

    if "ID14_01" in sources:
        raw = payload(sources["ID14_01"], (4, 5))
        st2 = make_st2(raw, (4, 5), b"Print Snoopy\0" + b"2464_09_B41_ID14_01")
        stem = "Print Snoopy [AUD_2464_09_B41_ID14_01]"
        outputs[accession_dir("ID14_01") / f"{stem}.bin"] = checked(
            "Print Snoopy.bin", raw
        )
        outputs[accession_dir("ID14_01") / f"{stem}.st2"] = checked(
            "Print Snoopy.st2", st2
        )

    if "ID16_02" in sources:
        raw = payload(sources["ID16_02"], tuple(range(8)))
        outputs[
            accession_dir("ID16_02")
            / "Color Runs [AUD_2464_09_B41_ID16_02].rom"
        ] = checked("Color Runs.rom", raw)
        outputs[
            accession_dir("ID16_02")
            / "180 XL-1 Resident Interpreter (Color Runs extraction) "
            "[AUD_2464_09_B41_ID16_02].rom"
        ] = checked("Color Runs resident.rom", raw[:0x400])

    if "ID05_01" in sources:
        composite = payload(sources["ID05_01"], (4, 5, 6, 7))
        raw = composite[:0x200]
        st2 = make_st2(raw, (4, 5), b"SPACE WAR 2 HAGLEY ID05_01")
        stem = "Space War (S2-A3) [AUD_2464_09_B41_ID05_01]"
        outputs[accession_dir("ID05_01") / f"{stem}.bin"] = checked(
            "Space War.bin", raw
        )
        outputs[accession_dir("ID05_01") / f"{stem}.st2"] = checked(
            "Space War.st2", st2
        )

    if "ID05_02" in sources:
        source_st2 = sources["ID05_02"]
        game_pack = payload(source_st2, (4, 5, 6, 7))
        stem = "Game Pack (Doodle, Curling, Pong, Addition, Freeway)"
        outputs[accession_dir("ID05_02") / f"{stem}.bin"] = checked(
            "Game Pack.bin", game_pack
        )
        outputs[
            accession_dir("ID05_02")
            / "Basic Videomate 3 Game Package (Alt) "
            "[AUD_2464_09_B41_ID05_02].st2"
        ] = checked(
            "Basic Videomate Game Pack.st2", source_st2
        )

        variants = (
            (
                "ID04_02",
                "Game Pack (Quiz and Tag-Race upper-page variant) "
                "[AUD_2464_09_B41_ID04_02, ID17_01]",
                b"GAME PACK QUIZ-TAG UPPER",
                "Game Pack quiz",
            ),
            (
                "ID05_01",
                "Game Pack (Space War upper-page variant) "
                "[AUD_2464_09_B41_ID05_01]",
                b"GAME PACK SPACEWAR UPPER",
                "Game Pack space",
            ),
        )
        for accession, name, title, label in variants:
            if accession not in sources:
                continue
            alternate = payload(sources[accession], (4, 5, 6, 7))
            variant = game_pack[:0x200] + alternate[0x200:]
            outputs[Path("combined") / f"{name}.bin"] = checked(
                f"{label}.bin", variant
            )
            outputs[Path("combined") / f"{name}.st2"] = checked(
                f"{label}.st2", make_st2(variant, (4, 5, 6, 7), title)
            )

    if "ID33_01" in sources:
        original = parse_st2(sources["ID33_01"])
        if original.pages != (4, 5, 6, 7):
            raise ValueError(f"ID33_01 has unexpected pages {original.pages}")
        repaired = bytearray(original.data)
        repaired[4] = 5
        stem = "TV Tennis (ANDY) [AUD_2464_09_B41_ID33_01]"
        outputs[accession_dir("ID33_01") / f"{stem}.bin"] = checked(
            "TV Tennis.bin", original.payload
        )
        outputs[accession_dir("ID33_01") / f"{stem}.st2"] = checked(
            "TV Tennis.st2", bytes(repaired)
        )

    if "ID06_01" in sources:
        outputs[
            accession_dir("ID06_01")
            / "Coin Bowling (GPL-4 Variant) [AUD_2464_09_B41_ID06_01].arc"
        ] = checked("Coin Bowling.arc", sources["ID06_01"])

    if "ID06_02" in sources:
        captured = sources["ID06_02"]
        if len(captured) != 0x801 or any(captured[0x700:]):
            raise ValueError("ID06_02 no longer has its evidenced 257-byte zero tail")
        outputs[
            accession_dir("ID06_02")
            / "Computer Bowling (FPL-4 Variant) [AUD_2464_09_B41_ID06_02].bin"
        ] = checked("Computer Bowling.bin", captured[:0x700])

    if "ID15_01" in sources:
        outputs[
            accession_dir("ID15_01")
            / "Shrink (Word Language Conversation Program) "
            "[AUD_2464_09_B41_ID15_01].bin"
        ] = checked("Shrink.bin", sources["ID15_01"])

    if "ID20_01" in sources:
        captured = sources["ID20_01"]
        if len(captured) != 0x700:
            raise ValueError("ID20_01 is not the expected seven-page capture")
        outputs[
            accession_dir("ID20_01")
            / "VIP Pinball (Andrew Modla, Hagley Capture) "
            "[AUD_2464_09_B41_ID20_01].ch8"
        ] = checked("VIP Pinball.ch8", captured[0x200:])

    if "ID21_02" in sources:
        outputs[
            accession_dir("ID21_02")
            / "4096 Bit Picture [AUD_2464_09_B41_ID21_02].bin"
        ] = checked("4096 Bit Picture.bin", sources["ID21_02"])

    if "ID26_01_1" in sources:
        outputs[
            accession_dir("ID26_01_1")
            / "COSMAC VIP Monitor ROM [AUD_2464_09_B41_ID26_01_1].rom"
        ] = checked("COSMAC VIP Monitor.rom", sources["ID26_01_1"])

    if "ID26_02_2" in sources:
        outputs[
            accession_dir("ID26_02_2")
            / "FPL-4 Race Example [AUD_2464_09_B41_ID26_02_2].bin"
        ] = checked("FPL-4 Race Example.bin", sources["ID26_02_2"])

    if "ID27_01_2" in sources:
        outputs[
            accession_dir("ID27_01_2")
            / "FEL-1 Example [AUD_2464_09_B41_ID27_01_2].bin"
        ] = checked("FEL-1 Example.bin", sources["ID27_01_2"])

    if "ID32_01_2" in sources:
        captured = sources["ID32_01_2"]
        if len(captured) != 0x800:
            raise ValueError("ID32_01_2 is not the expected eight-page capture")
        outputs[
            accession_dir("ID32_01_2")
            / "Snoopy COSMAC Picture [AUD_2464_09_B41_ID32_01_2].ch8"
        ] = checked("Snoopy COSMAC Picture.ch8", captured[0x200:])

    if "ID10" in sources:
        outputs[
            accession_dir("ID10") / "Color Etch [AUD_2464_09_B41_ID10].rom"
        ] = checked(
            "Color Etch.rom", sources["ID10"]
        )

    if "ID13_02" in sources:
        outputs[
            accession_dir("ID13_02") / "180 XL-1 [AUD_2464_09_B41_ID13_02].rom"
        ] = checked(
            "180 XL-1.rom", sources["ID13_02"]
        )

    if "ID16_01" in sources:
        decoded = parse_intel_hex(sources["ID16_01"])
        outputs[
            accession_dir("ID16_01")
            / "Snoopy Snipe Shoot [AUD_2464_09_B41_ID16_01].rom"
        ] = checked(
            "Snoopy Snipe Shoot.rom", decoded
        )

    if "ID33_02" in sources:
        raw = sources["ID33_02"] + bytes(5)
        st2 = make_st2(raw, (1,), b"FRED 1.5 TAPE SOFTWARE FRAGMENT")
        stem = (
            "FRED 1.5 Tape Save-Load Software (Fragment) "
            "[AUD_2464_09_B41_ID33_02]"
        )
        outputs[accession_dir("ID33_02") / f"{stem}.bin"] = checked(
            "FRED 1.5 fragment.bin", raw
        )
        outputs[accession_dir("ID33_02") / f"{stem}.st2"] = checked(
            "FRED 1.5 fragment.st2", st2
        )

    return outputs


def write_outputs(
    output_dir: Path,
    outputs: dict[Path, bytes],
    sources: dict[str, bytes],
    check: bool,
) -> None:
    # On a normal build, remove obsolete files previously created by this
    # script. Only unchanged files recorded in the old manifest are removed;
    # unrelated or locally edited files are left alone.
    old_manifest = output_dir / "MANIFEST.sha256"
    if not check and old_manifest.is_file():
        expected_paths = {relative.as_posix() for relative in outputs}
        for line in old_manifest.read_text(encoding="utf-8").splitlines():
            fields = line.split("  ", 1)
            if len(fields) != 2 or fields[1] in expected_paths:
                continue
            old_hash, old_name = fields
            parts = PurePosixPath(old_name).parts
            if not parts or any(part in {"", ".", ".."} for part in parts):
                continue
            old_path = output_dir.joinpath(*parts)
            if old_path.is_file() and sha256(old_path.read_bytes()) == old_hash:
                old_path.unlink()
                print(f"removed                       {old_name}")

    for relative, data in sorted(outputs.items(), key=lambda item: str(item[0])):
        path = output_dir / relative
        if check:
            if not path.is_file() or path.read_bytes() != data:
                raise SystemExit(f"stale or missing: {path}")
            state = "checked"
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.is_file() and path.read_bytes() == data:
                state = "unchanged"
            else:
                path.write_bytes(data)
                state = "wrote"
        print(f"{state:9} {len(data):4}  {sha256(data)}  {relative}")

    manifests = {
        "MANIFEST.sha256": "".join(
            f"{sha256(data)}  {relative.as_posix()}\n"
            for relative, data in sorted(outputs.items(), key=lambda item: str(item[0]))
        ).encode("utf-8"),
        "SOURCES.sha256": "".join(
            f"{sha256(data)}  AUD_2464_09_B41_{accession}\n"
            for accession, data in sorted(sources.items())
        ).encode("utf-8"),
    }
    for name, data in manifests.items():
        path = output_dir / name
        if check:
            if not path.is_file() or path.read_bytes() != data:
                raise SystemExit(f"stale or missing: {path}")
            state = "checked"
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.is_file() and path.read_bytes() == data:
                state = "unchanged"
            else:
                path.write_bytes(data)
                state = "wrote"
        print(f"{state:9} {len(data):4}  {sha256(data)}  {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        help=(
            "scan only this directory; by default scan beside build.py and, "
            "when present, its hagley subdirectory"
        ),
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check", action="store_true", help="check existing outputs without writing"
    )
    args = parser.parse_args()

    if args.source_dir is not None:
        source_dirs = (args.source_dir.resolve(),)
    else:
        source_dirs = (ROOT, ROOT / "hagley") if (ROOT / "hagley").is_dir() else (ROOT,)

    sources, notes = discover(source_dirs)
    for note in notes:
        print(note, file=sys.stderr)
    outputs = build(sources)
    if not outputs:
        print("no supported finalized outputs can be built from the current inputs")
        return
    write_outputs(args.output_dir, outputs, sources, args.check)
    print(f"built {len(outputs)} files from {len(sources)} recognized accessions")


if __name__ == "__main__":
    main()
