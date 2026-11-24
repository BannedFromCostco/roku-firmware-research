# Evidence for the L203X reference package

The owner reported obtaining `update.roku` from Roku’s official USB updater. The archived download has a known byte length and digest. A transaction record tying those exact bytes to the vendor server was unavailable, and publisher verification of the manifest did not complete. Roku documents the download filename and the TV-side validation step. [Roku USB updater](https://tvupdate.roku.com/) · [Roku USB update instructions](https://support.roku.com/article/update-your-roku-tv-system-with-usb)

## Artifact identifiers

| Byte range or object | Bytes | SHA-256 |
| --- | ---: | --- |
| Archived `update.roku` | 373,057,600 | `8201984e423fc2d7b691a47d4331bfb4a7ea874d4c1480af72139c7d65aa3854` |
| Main TAR image member `HEF.64E45400A` | 95,203,328 | `b7cba7c8581b16d3226a00900a5fb6fd771f4f898cf574de695798f9198370c0` |
| Rescue TAR image member `HEF.64R45400A` | 19,894,272 | `07a682494cf7d3451cd4a7fdb111eb0989530e574b71ba55382dd77ee66b1ac6` |
| SFYR page extent | 257,949,696 | `abc90965d72c570e1616f94e86ec828210e280c743bcb1013157e4335611d722` |
| Shared embedded DTB | 91,142 | `94c92859b4cd9b443193dfc4f2c3f86a900ef21d22795b702af0ee7c02a1e012` |
| Decoded main kernel | 15,458,820 | `0653983371b8fc109958c4b85c1fdd51247002a70fc2c368800bdf72b677f201` |
| Decoded rescue kernel | 14,299,952 | `e3ff70ae5810808ca2722043af44903260e1eabbd3e9f3bc0859804ea5b8e169` |

## Checks and limits

| Evidence | Observation | Limit |
| --- | --- | --- |
| Decoded manifest and image records | The manifest identifies `sandia_his_his_x035`, OS `15.2.4` and main build `HEF.64E45400A`. The declared SHA-1 and SHA-256 match both full TAR image members. All 38 saved AImage component digests also match the corresponding slices of the archived decoded TAR. | These comparisons check byte consistency. The installed `HEG.34E02402A` image was unavailable. |
| L203X and device tree | Main and rescue independently contain the L203X model mapping and matching model data in BootData and AppFS. The complete FDT structure and bounds passed; the decoded trees have 693 nodes and 2,909 properties. | A package configuration can describe multiple models. The TV’s exact mainboard assembly and silicon population were outside the inspection. |
| SFYR reconstruction | The header digest matches the complete 62,976-page extent. The inventory accounts for 31 object-header, 58,957 file-data, 930 summary and 3,058 unused pages. All 24 reconstructed file hashes matched the saved inventory, including the index itself. Each of the index’s 23 entries matched its file. | The observed page and summary structure is consistent with YAFFS2. This is a comparison of one package, with no claim about other Roku releases. |
| SFYR library duplication | Seventeen full library records map to 18 matches in the two TAR image inventories because one boot-logo record appears in both images. Matches use complete records, including headers and padding. | This result concerns the two libraries in this archive. |
| Kernels and AppFS | Both U-Boot image headers and payload CRCs passed. Kernel configuration blocks decoded in both images. Both AppFS inode counts agreed with their superblocks, and the 925 regular files passed bounded decompression. | Build-time config and linked code do not establish runtime controls or equivalence to individual vendor security patches. |
| Signature tests | A packaged ARM kernel module’s detached CMS verified against the main kernel’s embedded certificate and failed against the rescue kernel’s different certificate. Verification pinned the candidate certificate and skipped PKI chain validation. The tested combinations for the outer manifest’s signature-like trailer did not verify with the candidate public key. | The outer manifest signer and exact signed byte range remain unresolved. Runtime module admission and complete boot-chain enforcement were outside the test. |

The original analysis used `unixtract` for outer decoding and component framing. Separate offline checks covered member digests, file boundaries, page and object accounting, and format-specific checksums. The publication audit independently rehashed the archives, TAR members, saved components, kernel files, and SFYR extent and reconstructed file streams. [Pinned unixtract revision](https://github.com/theubusu/unixtract/tree/d1f4b98e975dc86008c3dbe89943dd78819d7f4c) · [YAFFS2 summary code](https://github.com/Aleph-One-Ltd/yaffs2/blob/master/core/yaffs_summary.c) · [Flattened Devicetree specification](https://devicetree-specification.readthedocs.io/en/stable/flattened-format.html) · [Linux module signing documentation](https://docs.kernel.org/admin-guide/module-signing.html)
