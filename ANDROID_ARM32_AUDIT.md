# Huawei MatePad T 8 / ARM32 compatibility audit

Audited locally on 10 November 2026. No working build configuration, release
package, bundled database, signing key or phone installation was changed.
The separate, requested 8-pixel Sermon Notes left inset was applied to website
and Android source only.

**Finding: an additional `armeabi-v7a` APK is feasible using a separate Python
3.11 build. The existing Python 3.13 ARM64 build can remain unchanged.**
Dependency packaging succeeded; a complete ARM32 APK and physical-device
acceptance tests have not been performed.

## Current application

| Item | Audited value | Consequence |
| --- | --- | --- |
| Application ID | `org.iowo.d4.biblestudy` | Keep this for upgrades that retain the same app storage. |
| Minimum Android | API 26 / Android 8.0 | Android 10 / API 29 meets this requirement. |
| Target / compile SDK | 36 / 36 | These do not make Android 16 the minimum OS. |
| Android Gradle plugin | 8.7.3 | Compatible with the current Chaquopy plugin. |
| Chaquopy | 17.2.0 | Retain this version for the legacy build too. |
| Embedded Python | 3.13, resolved runtime 3.13.16 | No ARM32 target is available. |
| Configured and packaged ABIs | `arm64-v8a`, `x86_64` | Neither matches an ARM32-only Android installation. |
| Direct Android dependencies | AndroidX WebKit 1.12.1, Core 1.15.0 | Dependency resolution and native-library merging passed for ARM32. |
| Rendering / PDF | System WebView; Android `PdfDocument` and text renderer | No separately bundled PDF rendering native library is required. |

These settings are in `app/build.gradle` and `build.gradle`. The release
merged manifest and the actual release APK were inspected as well.
[Android documents the distinction between minimum and target SDK](https://developer.android.com/guide/topics/manifest/uses-sdk-element).

The Huawei tablet was not attached during the audit; the attached device was
an Oppo. Huawei's specifications confirm Android 10 and 2 GB RAM, but do not
identify the firmware's supported application ABIs. A 64-bit-capable CPU does
not by itself establish which app ABIs this firmware exposes. Confirm on the
MatePad using these read-only commands:

```text
adb -s <MatePad-serial> shell getprop ro.product.cpu.abilist
adb -s <MatePad-serial> shell getprop ro.product.cpu.abilist32
adb -s <MatePad-serial> shell getprop ro.product.cpu.abilist64
adb -s <MatePad-serial> shell getprop ro.build.version.sdk
adb -s <MatePad-serial> shell dumpsys webviewupdate
```

If its list includes `armeabi-v7a` and excludes `arm64-v8a`, the audited
release has no matching ABI. This explains an ABI installation failure,
although the tablet's actual installer error has not been captured.
[Huawei specifications](https://consumer.huawei.com/ie/tablets/t/matepad-t-8/specs/),
[Android ABI documentation](https://developer.android.com/ndk/guides/abis).

## Exact blocker and dependency results

Adding `armeabi-v7a` while retaining Python 3.13 fails before compilation.
The isolated Gradle probe reproduced:

```text
Variant 'debug': Python 3.13 is not available for the ABI 'armeabi-v7a'.
Supported ABIs are [arm64-v8a, x86_64].
```

Chaquopy provides ARM32 for Python 3.11 and earlier; Python 3.12 and later
are 64-bit only. A host Python with the same major/minor version is also
required. The probe used host Python 3.11.15 and Chaquopy's Android 3.11
runtime. No downgrade of the existing 64-bit app is necessary.
[Chaquopy build and ABI requirements](https://chaquo.com/chaquopy/doc/current/android.html).

| Dependency | Existing release | Successful ARM32 resolution |
| --- | --- | --- |
| Flask | 3.1.2 | 3.1.2, architecture-independent wheel |
| requests | 2.32.5 | 2.32.5, architecture-independent wheel |
| MarkupSafe | 3.0.4, CPython 3.13 native extension | 3.0.3, `cp311-cp311-android_24_armeabi_v7a` wheel |
| charset-normalizer | 3.5.2, CPython 3.13 native extensions | 3.5.2, `py3-none-any` wheel |
| Jinja2 / Werkzeug | 3.1.6 / 3.1.9 | Same versions, architecture-independent wheels |
| Remaining transitive packages | blinker, certifi, click, idna, itsdangerous, urllib3 | Same resolved versions; all accept Python 3.11 |

Thus the release's exact CPython 3.13 binary artifacts cannot be reused, but
no required dependency was found that prevents a separate ARM32 build.
For reproducibility, lock the legacy requirements to the successful versions,
including MarkupSafe 3.0.3; leave the modern requirements unchanged.
The pure-Python charset-normalizer wheel preserves functionality without its
optional acceleration. The available ARM32 MarkupSafe wheel is listed in the
[official Chaquopy wheel repository](https://chaquo.com/pypi-13.1/markupsafe/).

Python imports of ReportLab, Pillow and PDFium remain in shared website-only
or optional source paths. They are not Android pip requirements. The Android
adapter replaces sermon PDF generation with `NativeServices.createPdf` and
`SermonPdf.java`; no new PDF/Pillow dependency is needed for ARM32.

## Offline features and database preservation

The successful probe contains nine top-level native libraries: Python 3.11,
its stable ABI stub, Chaquopy's Java bridge, OpenSSL libraries/stubs, and SQLite
libraries/stubs. All are verified ELF32 / ARM (`e_machine=40`). An additional
49 native extensions inside the generated Chaquopy assets also passed that
check, including the ARM32 MarkupSafe extension.

The ARM32 SQLite binary identifies version 3.53.4 and contains the
`ENABLE_FTS5`, `json_extract` and `json_each` strings. This is binary evidence,
not an Android runtime query. FTS5 is required by the bundled illustration
search database, and JSON SQL functions are used by study queries. Retain
Chaquopy 17.2: its recent SQLite feature support matters here.
[Chaquopy's SQLite change](https://chaquo.com/chaquopy/doc/current/changelog.html).

The same 32 resource files total 2,162,016,256 bytes; the largest single
file is 1,081,921,536 bytes. They can remain byte-for-byte identical in the
additional APK. SQLite's database format is portable between 32-bit and
64-bit environments; CPU bitness does not require database conversion.
[SQLite database portability](https://www.sqlite.org/onefile.html).

The existing installer streams resources in small buffers rather than
loading the entire collection into RAM. It uses Java `long` for resource
sizes, which matters because the combined resources exceed a signed 32-bit
byte count. All resource hashes passed the existing offline resource audit.
No study content was removed or reduced.

For a later install, retain the same application ID, production signing
certificate and data paths, and use an appropriate monotonically increasing
version code. Do not uninstall or clear storage as part of an upgrade.
Keep `study-data/personal/sermon_notes.db`, the reader database, local drafts,
settings and encrypted session handling unchanged.

## Evidence and practical implementation

The independent project is under `.test-data/abi-audit-20261110/probe`.
It uses the same Chaquopy and Android dependency versions and reads the
existing Python source without changing it. Only dependency/source asset
generation and native-library merging were run; no APK was assembled.

Verified results:

- Python 3.13 + ARM32: rejected with the exact ABI error above.
- Python 3.11 + ARM32: Gradle asset generation and native merge passed.
- Existing Python source: parsed with Python 3.11 grammar.
- PC Python 3.11 offline tests: 20 passed; two browser suites intentionally
  skipped. Coverage includes Bible/study APIs, notes, synchronization,
  native PDF handoff, setup preservation and bundled resource integrity.
- Native Android ARM32 execution, PDF output and EMUI keyboard/WebView
  behavior: still require testing on the MatePad.
- All six original APK/AAB files: SHA-256 unchanged after the audit.

Logs and machine-readable evidence are in `.test-data/abi-audit-20261110/`:
`python313-arm32.log`, `python311-arm32.log`, `android-dependencies.log`,
`python311-offline-tests.log`, `arm32-dependency-evidence.json`,
`original-packages.json` and `preservation-check.json`.

Recommended implementation: add a separate legacy build profile or isolated
build project using `armeabi-v7a`, Python 3.11 and a matching build-time
interpreter. Keep `minSdk 26`, the existing Java/UI source, all offline assets
and the current Python 3.13 64-bit profile. Give its output a distinct filename
such as `IOWO-D4-Bible-Study-legacy-arm32.apk` and an independent output path.
Do not mix or copy Python 3.13 bytecode/Chaquopy runtime assets into it.

Before distribution, perform a complete signed build to the separate output
path, inspect its packaged ABIs and resource checksums, then test on the
MatePad: offline startup, all translations, Thompson chains, dictionaries,
concordance, commentaries, outlines, illustrations, sermon editing/highlights,
save/reopen, PDF/share and synchronization. Confirm its WebView provider is
current: existing UI scripts use modern JavaScript such as optional chaining
and `Array.at`, plus CSS `:has`. An old EMUI WebView can be a separate runtime
compatibility problem even after installation succeeds. The tablet's 2 GB RAM
also warrants checking startup and long study pages under memory pressure.

No new distributable APK, GitHub upload, Docker action or device installation
was performed during this audit.
