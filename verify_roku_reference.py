#!/usr/bin/env python3
"""Verify saved L203X research inputs without extracting their contents."""

# SPDX-License-Identifier: MIT
# Copyright 2026 BannedFromCostco

import argparse
import hashlib
import struct
import tarfile
from pathlib import Path

ARCHIVE_SIZE = 373_057_600
ARCHIVE_SHA = "8201984e423fc2d7b691a47d4331bfb4a7ea874d4c1480af72139c7d65aa3854"
IMAGES = {
    "HEF.64E45400A": (
        "/dev/mtd2",
        95_203_328,
        "b7cba7c8581b16d3226a00900a5fb6fd771f4f898cf574de695798f9198370c0",
    ),
    "HEF.64R45400A": (
        "/dev/mtd_Rescue",
        19_894_272,
        "07a682494cf7d3451cd4a7fdb111eb0989530e574b71ba55382dd77ee66b1ac6",
    ),
}
SFYR_OFFSET = 0x06DC6800
SFYR_HEADER = struct.Struct("<4s4I32s")
SFYR_SHA = "abc90965d72c570e1616f94e86ec828210e280c743bcb1013157e4335611d722"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_archive(path):
    with path.open("rb") as data:
        size = data.seek(0, 2)
        require(size == ARCHIVE_SIZE, "unexpected update.roku byte length")
        data.seek(0)
        require(
            hashlib.file_digest(data, "sha256").hexdigest() == ARCHIVE_SHA,
            "update.roku does not match the reference SHA-256",
        )
    print("Matched archived update.roku:", ARCHIVE_SHA)


def verify_tar(path):
    with tarfile.open(path, mode="r:") as archive:
        members = archive.getmembers()
        sizes = {"manifest": 756, **{name: item[1] for name, item in IMAGES.items()}}
        require(
            len(members) == len(sizes)
            and {member.name: member.size for member in members} == sizes
            and all(member.isfile() for member in members),
            "unexpected decoded TAR member names, lengths or types",
        )
        with archive.extractfile("manifest") as manifest:
            fields = dict(
                line.split("=", 1)
                for line in manifest.read(500).decode("utf-8").splitlines()
                if "=" in line
            )
        require(
            fields.get("update_name", "").split()[:3]
            == ["sandia_his_his_x035", "HEF.64E45400A", "15.2.4"],
            "decoded manifest identifies a different reference build",
        )
        for name, (target, _, expected) in IMAGES.items():
            with archive.extractfile(name) as image:
                sha256 = hashlib.sha256()
                sha1 = hashlib.sha1(usedforsecurity=False)
                for block in iter(lambda: image.read(1 << 20), b""):
                    sha256.update(block)
                    sha1.update(block)
            require(
                sha256.hexdigest() == expected == fields.get(f"sha256({target})")
                and sha1.hexdigest() == fields.get(f"sha1({target})"),
                f"{name} failed the image digest check",
            )
            print(f"Matched {name} and its manifest digests:", expected)


def verify_sfyr(path):
    with path.open("rb") as data:
        data.seek(SFYR_OFFSET)
        header = data.read(SFYR_HEADER.size)
        require(len(header) == SFYR_HEADER.size, "truncated SFYR header")
        magic, version, page, group, length, embedded = SFYR_HEADER.unpack(header)
        require(
            (magic, version, page, group, length)
            == (b"SFYR", 1, 4096, 64, 257_949_696),
            "unexpected SFYR header geometry",
        )
        digest = hashlib.sha256()
        remaining = length
        while remaining:
            block = data.read(min(remaining, 1 << 20))
            require(block, "truncated SFYR extent")
            digest.update(block)
            remaining -= len(block)
    require(
        digest.hexdigest() == SFYR_SHA == embedded.hex(),
        "SFYR extent differs from its stored and published SHA-256",
    )
    print(f"Matched SFYR extent ({length // page:,} pages):", SFYR_SHA)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="original update.roku")
    parser.add_argument(
        "--decoded-tar", type=Path, help="optional local TAR with its trailing SFYR extent"
    )
    args = parser.parse_args()
    try:
        verify_archive(args.archive)
        if args.decoded_tar is not None:
            verify_tar(args.decoded_tar)
            verify_sfyr(args.decoded_tar)
    except (ValueError, OSError, tarfile.TarError) as exc:
        parser.exit(1, f"Verification failed: {exc}\n")


if __name__ == "__main__":
    main()
