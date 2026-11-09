# IOWO Bible Study Andriod App

Android source for **IOWO D4 Bible Study**, package `org.iowo.d4.biblestudy`,
version **1.0.2 (3)**. Native Java hosts a local Python/Flask study engine in
Android WebView. Bible texts, dictionaries and study resources work offline
once prepared. Personal sermon notes save locally, with optional account-based
Google Drive backup through the District 4 website.

The finished release folder is kept separately from source. It contains a
signed standalone APK for sharing, a signed Google Play AAB with three
install-time asset packs, store listing assets and publishing instructions.
Signing keys, credentials, installed personal data and large resource databases
are deliberately excluded from this repository.

## Restore the offline library

The source manifest records every required file, byte size and SHA-256 hash.
Restore the matching resources from the standalone release APK you already
have permission to use:

```powershell
.\scripts\restore-library.ps1 -ApkPath 'C:\path\to\IOWO-D4-Bible-Study-1.0.1-share.apk'
```

This extracts only the bundled study library, not personal device data. It
refuses to overwrite a different existing resource. Distribution permissions
for the included publishers' materials remain the publisher's responsibility.

## Build

Use Android Studio / Java 17+, Android SDK 36 and Python 3.13. Set SDK location
in your untracked `local.properties`. Chaquopy 17.2 installs Python packages
from the Gradle configuration. `arm64-v8a` and `x86_64` devices on Android 8+
are supported.

```powershell
$env:JAVA_HOME='C:\Program Files\Android\Android Studio\jbr'
.\gradlew.bat :app:assembleDebug --console=plain
```

Release builds require the environment variables `IOWO_RELEASE_STORE`,
`IOWO_RELEASE_STORE_PASSWORD`, `IOWO_RELEASE_KEY_ALIAS` and
`IOWO_RELEASE_KEY_PASSWORD`. Never commit their values or a keystore.

```powershell
.\gradlew.bat :app:assembleRelease --console=plain
.\gradlew.bat :app:bundleRelease -PplayDelivery=true --console=plain
```

A release-signed APK cannot update an existing debug-signed installation.
Keep the debug test installation and its notes safe; back up/export before
planning a signing-key migration. For consistent future Play and shared-APK
updates, configure Play App Signing with the same existing production key
using the Play Console's key-import instructions.

## Source layout and tests

- `app/src/main/java`: native splash, secure token vault, PDF/export and backup service.
- `app/src/main/python`: local reader engine and authenticated website adapter.
- `app/src/main/assets/runtime`: actual app HTML/CSS/JavaScript and offline privacy page.
- `app/src/main/assets/tutorials`: screenshot guide and compressed screenshots.
- `study_core`, `study_library`, `study_illustrations`: install-time asset-pack configuration.
- `server_integration/mobile_bible_api.py`: website bridge source matching this app.

Install `requirements-desktop.txt` plus Playwright and its Chromium/WebKit
browsers in a development environment, then run `tests/test_offline.py` with
`IOWO_BROWSER_TESTS=1`. Tests use fictional accounts and isolated databases.
Screenshot refreshes use `scripts/capture_tutorials.py`; they never read live
phone notes. `TEST_RESULTS.md` records automated and device checks.

## Saving and backup

The conversion button, conversion endpoints and conversion tutorial were
removed after the existing sermon import. Converted notes remain ordinary
stored notes. Save, Sync Notes, conflict handling and PDF export remain.
Background syncing is user-initiated. After a process kill or reboot, tap
Sync Notes again; confirmed versions and pending request IDs persist.

## Offline screenshot tutorials (Android only)

The app shows an eight-topic guided tour on first launch after installation
(or once when an existing installation first receives tutorials). Skip or finish
to continue; later launches do not automatically reopen the guide. Library
preparation continues behind it. Help works before login and resource setup,
and takes priority over the optional support reminder.

Open **Tutorials** on the native splash screen, or **Reading settings > Help >
Tutorials & guided tour**, to replay the tour or search the 41-topic outline.
Topics include Thompson Chain Index, Bible navigation/translations, dictionaries,
commentaries, outlines, illustrations, Bible marks/bookmarks, Sermon Notes,
formatting, PDF/share, save/sync/conflicts, setup/account and help.

Each topic displays one cropped screenshot of the actual app with numbered
vector arrows and matching labels. Tap it to enlarge, use Zoom in/Fit screen,
and scroll to inspect a control. Back/Escape first closes the enlargement.
Screenshots use a fictional account and sample sermons; viewing help never
calls study/account APIs or edits notes. The previous practice activities have
been removed. Reviewed topic IDs remain compatible with the earlier guide.

All 41 topics share 27 WebP images totaling 621,704 bytes (about 622 KB). Arrows
and labels use a small shared script/manifest, with no duplicated bitmap text.
Only the current topic's image is loaded. All assets and existing app fonts
are bundled for offline use. Automated tests cap the image bundle at 800 KB.
The native guide bridge exposes only closing; external resources are blocked.

To refresh screenshots after controls change, run:

```powershell
$env:PYTHONUTF8='1'
.tools/test-env/Scripts/python.exe scripts/capture_tutorials.py
```

The capture script uses the real local reader and an isolated fictional-data
folder, `.test-data/tutorial-capture`, with a fake online-backup service. It
never uses a live account, phone notes or website connection. Its startup
image comes from `.test-data/tutorial-native-startup.png`, an inspected native
720x1612 screenshot containing only the startup progress, verse and help
buttons. Refresh that source when the native splash changes. Capture and
encoding dependencies are development tools only, not app dependencies.

Sermon conversion has been retired in the app and website. Existing notes and Sync Notes remain available.

## Huawei / universal compatibility release

The default modern profile still embeds Python 3.13 for ARM64 and x86-64.
Use `-PcompatibilityBuild=true` for a separate Python 3.11 build including
armeabi-v7a, arm64-v8a and x86_64. This is the current production/share APK
profile. Keep a matching host Python 3.11 under `.tools/python` or supply
`-PbuildPython=C:/path/to/python.exe`. MarkupSafe is pinned to 3.0.3 for its
verified ARM32 wheel.

```powershell
.\gradlew.bat :app:assembleRelease :app:lintRelease -PcompatibilityBuild=true --console=plain
```

Production signing still uses the existing IOWO_RELEASE_* environment variables.
Do not uninstall a debug-signed test app to replace it with this production APK.
The startup splash keeps the full artwork visible with the original rounded
About Publisher and Tutorials buttons. A loading bar and 30 rotating study
verses show while the Bible and saved notes prepare. Once ready, these controls
hide and the artwork remains alone for three visible seconds before the reader
opens. Help dialogs and backgrounding restart that visible interval.

The connected test phone was updated in place to 1.0.3 (4), preserving both
database hashes. See test-results/splash-device-verification.json. The current
production/share APK is ../District4-Release-20261109/APK/IOWO-D4-Bible-Study-1.0.3-share.apk; prior 1.0.2 is archived.
