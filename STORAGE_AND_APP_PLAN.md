# IOWO D4 Bible Study: source project and storage

Updated 9 November 2026. The Android source, sanitized shared resources,
first-launch screens and test suite are created. An authorized debug APK was
built and installed on the connected OPPO A57 (Android 14). No release AAB was
generated. The website and its backups were not changed for the phone test.

## Agreed behavior

- App name: **IOWO D4 Bible Study**.
- Reuse the website's Bible Study readers/tools and glass login design. The app
  uses a full-height reader without the website header/menu, Lora reading text
  and Space Grotesk controls, with fonts bundled for offline use.
- Include the entire prepared shared study library with installation for offline use.
- Require an existing website account at first online login; securely remember it
  for subsequent offline reading and writing without repeated login.
- Free for account holders; no advertisements, subscriptions or paid upgrades.
- Optional online sermon-note synchronization through the website and Google Drive.
- First-launch agreement/privacy notice and storage check, followed by login/setup.
- Supplied pictures used for splash and launcher icon. The splash's About Publisher
  button pauses opening while the profiles are viewed; otherwise opening continues.
- About Developer includes Pijeme Franco Walawala and Bernard Balansag; the
  unfinished third profile is omitted.
- The initial source-only stage is complete; the user has now authorized a debug
  APK and installation on the connected phone for testing.

## Measured prepared resources

The authoritative inventory is `app/src/main/assets/resource-manifest.json`.
SHA-256 checks pass for all 32 shared resource files.

| Component | Exact bytes | Decimal GB |
| --- | ---: | ---: |
| Sanitized Bible/study database | 1,081,921,536 | 1.081922 |
| Selected public library, catalogue and fresh reader indexes | 1,026,990,080 | 1.026990 |
| Sermon illustrations | 53,104,640 | 0.053105 |
| **Shared resource bundle** | **2,162,016,256** | **2.162016** |
| Working allowance during setup (256 MiB) | 268,435,456 | 0.268435 |
| **Additional free space needed after installation** | **2,430,451,712** | **2.430452** |

Further source assets currently occupy:

| Source assets | Exact bytes |
| --- | ---: |
| Reader interface, local fonts/images and developer portraits | 18,911,439 |
| Self-contained About Developer assets | 3,385,768 |
| Supplied splash and icon copies in app assets | 3,814,447 |

Android resources also include the supplied launcher artwork, and the final
package will include Java/Python code and runtime/native libraries. Those are not
part of the shared resource byte count. Source previews and duplicate development
images are not an estimate of the eventual Android installation size.

The app retains installation assets while creating a private working copy.
Compression, runtime extraction, Android installation staging and personal notes
all affect total storage. Reserve **at least 6 GB before installation for planning**.
This is an allowance, not a measured release minimum. The latest debug APK is
**812,697,482 bytes (about 813 MB / 775 MiB)**. Installed size after library setup
and installation/update free-space minimum still need measurement on the phone.
The app gives the exact resource and post-installation setup amounts above.

The earlier `storage-audit.json` records the original resource selection before
fresh indexes and sanitization. Its earlier baseline is historical; use the new
resource manifest and this document for current measurements.

## Offline library coverage

- NIV, Cebuano and Tagalog Bibles, each with 66 books.
- Dictionaries, original-language lookup, Thompson concordance/chains, book
  studies and embedded study/source images.
- BE/Wiersbe and locally imported commentary in the main database.
- 79 selected public library documents, including 42 Exalting Jesus books, one
  Moody book, nine Pulpit volumes and 36 sermon source editions. The nine Pulpit
  volumes overlap the sermon source selection.
- Prepared portable commentary/sermon catalogues and rich source page caches,
  avoiding a full first-run index rebuild on the phone.
- 80,316 dictionary entries, 14,187 lexicon entries, 16,361 embedded image assets
  and 8,961 illustrations from the audited source library.

Original import PDFs/EPUBs are not duplicated: the study readers use their indexed
text, formatting and embedded images. General whole-library ebook browsing and
unrelated website sections are outside the Bible Study app. Developer conversion
of private sermon PDFs remains an online website operation.

## Privacy and synchronization

Personal Bible marks, bookmarks, history and preferences are stripped from the
shared Bible snapshot; secure deletion and VACUUM remove unused private page data.
Account databases, existing personal sermon-note databases, `.env`, service-account
files, shared Google Drive tokens and unrelated private sources are excluded.

Each phone writes its own personal data under its authenticated website account
key. Android stores only a revocable device token and display profile in an
AES-GCM encrypted Android Keystore vault; it does not retain the password.
Sermon-note backup/restore uses the website integration. Bible marks and reading
preferences remain local, matching the existing scope of the website's Drive
sermon-note backup.

The website bridge is in `server_integration` and is now published in website
commit `a693a49` / Docker tag `20261109-a693a49`. The backup was confirmed complete
before that update. The live mobile-login endpoint now returns the expected
validation response. See `server_integration/INSTALL_AFTER_BACKUP.md` for details.
The latest appearance update applies the selected landscape/glass login and
eight illustrated wood scenes with compact 34 px Bible/study tab rows. These
pictures/fonts are bundled locally; the shared-library setup amount is unchanged.

## Verification and next testing

See `TEST_RESULTS.md` for the completed engine/browser/native-source checks.
Android compilation, lint, debug APK assembly, signature verification and 16 KB
ZIP alignment checks pass. The APK installed and opened successfully on the
authorized phone. Login/library setup, offline reading, Android PDF/share,
background behavior, complete installed storage and Play distribution still
need device/release testing.

Open `README.md` for the project layout, source-check commands and desktop preview.
