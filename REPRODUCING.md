# Reproducing the L203X archive checks

This procedure covers the Hisense 58A51LUR / Roku `L203X` Sandia reference archive, Roku OS **15.2.4** (`HEF.64E45400A` main and `HEF.64R45400A` rescue). A captured TV reported **15.3.4** (`HEG.34E02402A`). Keep the full build string with any comparison. [Published evidence](EVIDENCE.md)

## Verify inputs

Use Python 3.11 or newer with the [Python verifier](verify_roku_reference.py). Supply a local copy of the archive you acquired. The first command verifies the original download. The second also checks a separately prepared decoded TAR that retains the trailing SFYR data.

```text
python verify_roku_reference.py update.roku
python verify_roku_reference.py update.roku --decoded-tar outer.tar
```

The second command checks the decoded manifest’s build identity, both main and rescue members against SHA-1 and SHA-256 in that manifest, and the SHA-256 over the 62,976-page SFYR extent. The expected result is four matches. The file named `outer.tar` is the decoded byte stream, including the data after the TAR members. A three-member TAR recreated from extracted files lacks the trailing extent.

The commands read the supplied files without modifying either input and exit nonzero on a mismatch. They verify reference bytes and internal checksums. The manifest signer and coverage of the signature-like trailer remain unresolved. The original outer decoding used the independently maintained `unixtract`; the script here verifies existing inputs. [Pinned unixtract Roku implementation](https://github.com/theubusu/unixtract/blob/d1f4b98e975dc86008c3dbe89943dd78819d7f4c/src/formats/roku/mod.rs) · [Roku USB updater](https://tvupdate.roku.com/)

## Two checks that failed

- **The apparent U-Boot header in the opaque download failed validation.** The single legacy uImage magic match in the original package failed both the header CRC and the declared payload bounds. The separate decoded main and rescue uImages passed their CRC checks. Report the byte layer with any signature-scan result. [U-Boot legacy image format](https://github.com/u-boot/u-boot/blob/master/include/image.h)
- **The main AppFS `boot.digest` did not match SHA-1 of `boot.bin` as stored.** The trimmed digest file contained 40 hex characters. Hashing all 751,088 bytes of the reconstructed `boot.bin` gave a different value. This rules out that single coverage interpretation. The actual input to the stored digest remains unresolved. With these two files already reconstructed from main AppFS, compare them without printing either file.

```text
python -c "import hashlib; from pathlib import Path; print(hashlib.sha1(Path('boot.bin').read_bytes(), usedforsecurity=False).hexdigest().encode() == Path('boot.digest').read_bytes().strip().lower())"
```

The packaged device tree describes NAND and SPI NOR and contains an MMC node. Physical storage population and the live partition map remain open. Compare those independently before treating this firmware as a match for a different Hisense board. [Flattened Devicetree specification](https://devicetree-specification.readthedocs.io/en/stable/flattened-format.html)
