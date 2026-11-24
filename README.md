# Hisense Roku TV L203X firmware research

Offline analysis of the Roku USB update archive for the Hisense 58A51LUR, Roku hardware ID `L203X`. The archive is a useful hardware reference for Roku OS **15.2.4**, build **`HEF.64E45400A`**. The TV in the device record reported **15.3.4**, build **`HEG.34E02402A`**. The full build strings matter when comparing binaries or claiming a security fix. [Evidence and methods](EVIDENCE.md)

For commands and expected output, see [Reproducing the verification checks](REPRODUCING.md).

## Findings

- **Package-to-hardware mapping.** Main and rescue each contain an explicit `L203X` configuration. Their embedded Amlogic T5W X9 1G device trees match byte for byte. They describe four Cortex-A55 cores and a 1 GiB usable-memory range. Both packaged Linux 5.4.180 kernels are 32-bit ARM images. These are observations about the package. The physical board revision and live storage map remain open.
- **SFYR contents.** The data after the TAR members is a checksummed page stream with YAFFS2-style tags. I reconstructed 24 named files and verified the 23 digests in its file index. The two AImage libraries contain 17 complete records, all already present in the main or rescue TAR members. The remaining files are primarily branding, media, and packaged channel assets. This inventory can save a second search of the same archive for extra OS images.
- **Readable filesystem coverage.** Main and rescue AppFS yielded 553 and 372 regular files respectively. Both InitFS payloads remained opaque at their inner layer. The package gives useful visibility into the board, kernels and application resources. The full system userspace remains unresolved.
- **Integrity boundaries.** SHA-1 and SHA-256 over both TAR image members match their manifest entries. Publisher authentication of the outer Roku manifest remains unresolved. A separate detached signature on one packaged kernel module verified against the certificate embedded in the main kernel. Testing against the rescue certificate failed. That comparison covers the archived module and certificates. Effective trust on a running TV remains unmeasured. [Evidence and methods](EVIDENCE.md)

## Prior work

`unixtract` already recognizes the Roku wrapper and enumerates the main and rescue AImage records. The contributions here are the build-specific L203X mapping, the SFYR inventory and its duplicate-record result, and the independent integrity checks. The page tags were compared against the public YAFFS2 implementation. Roku describes Sandia at the device-family level. A separate L816X report records OS 15.3.4 build 2402 with a different full build string, `HXG.34E02402A`. [unixtract source](https://github.com/theubusu/unixtract/tree/d1f4b98e975dc86008c3dbe89943dd78819d7f4c) · [YAFFS2 packed tags](https://github.com/Aleph-One-Ltd/yaffs2/blob/master/core/yaffs_packedtags2.c) · [Roku hardware specifications](https://developer.roku.com/dev/docs/hardware) · [L816X device record](https://github.com/Catnip202X/roku-writeup/blob/main/docs/01-device.md)

These results apply to one archived package. Exact-build acquisition for `HEG.34E02402A`, bootloader enforcement on the physical TV, and a recovery rehearsal remain open. Roku documents USB update and Recovery Mode as device-side procedures. [USB update documentation](https://support.roku.com/article/update-your-roku-tv-system-with-usb) · [Roku recovery documentation](https://support.roku.com/article/roku-tv-keeps-restarting)

[Documentation license](LICENSE.md)
