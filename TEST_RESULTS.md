# Source verification: IOWO D4 Bible Study

Startup progress/30 NIV verses and preloaded Bible/notes/current-chapter tools:
all 20 app checks pass; Android compilation, lint and debug assembly pass.
The website regression suite passes all 436 tests.


## Compact top selection toolbar and launcher update, 9 November 2026

Website and Android runtime now replace the normal Sermon Notes top action bar
while editor text is selected. The compact bar contains Copy, underline and six
highlight swatches; the existing font/colour/undo controls are under More
formatting. Selection collapse, dismissal, Escape and tab changes restore the
normal actions. Saved selection ranges, native formatting and autosave remain
in use. The collapsed toolbar is about 60 CSS pixels high.

All six website sermon-editor browser tests pass, including 320 px through
1366 px viewports. The app browser scenario passes in Chromium desktop/phone
and WebKit phone, checking hidden normal actions, top placement, height,
clipboard, highlighting, formatting and export. Debug assembly and APK/source
asset comparisons pass. The launcher uses the original emblem, with XML
insets reduced from 27/29 percent to 20/22.5 percent and a white background.

The update was installed in place on the connected OPPO A57. A fresh private
backup was made first. All 514 sermon-note records compared identically after
installation, and the saved account and prepared-library state were retained.
The installed runtime HTML/CSS/JavaScript match the tested sources. The existing
emblem PNG remains unchanged; the launcher size/background changes are XML.

## Bible-style sermon selection toolbar, 9 November 2026

Updated both the website and bundled app reader. The six highlight swatches,
underline button and Copy action share the Bible selection design and bottom
placement. Existing sermon formatting, selection ranges and save/sync handlers
remain in use; all font/colour/undo controls remain available.

All 20 offline app checks pass. The browser scenario also passes with explicit
palette, bottom-centre placement, clipboard and native highlight assertions in
Chromium desktop/phone and WebKit phone. `:app:assembleDebug` succeeds, and the
APK contains byte-for-byte copies of the updated runtime template, JavaScript
and CSS. The APK was subsequently installed in place on the connected OPPO A57 on 9 November 2026 using `adb install -r`. App ID/signing certificates and the bundled resource manifest matched. A pre-upgrade private-data backup and previous APK were retained. All 514 sermon-note records were compared and remained identical; the saved account and prepared-library state were retained. The reader reopened and the updated runtime template, JavaScript and CSS were verified on the phone.

## Shared website/app editor update, 9 November 2026

Read Notes, Save and Delete now live in the top actions. The Editing tools and
Edit Text & Theme buttons are removed. Selecting editor text opens a compact
formatting popover without changing its style automatically; saved ranges survive
font/color/button interaction. Outside taps/Escape dismiss it. Theme and Text
are editable buttons with small pencil icons, opening the existing metadata form
with the corresponding field focused. Sync status remains a plain status line.
The shared reader also adds iOS-only visual-viewport panning compensation while
editing; Android's positioning is unchanged.

All 20 app checks pass, including Chromium desktop/phone and WebKit phone tests
for typing/autosave, metadata focus/edit/save, automatic selection tools, bold
and underline actions, dismissal and native PDF handoff. Native compilation/lint,
debug assembly, APK signature and 16 KB ZIP alignment checks pass.

The website receives the same reader/editor changes with optimized artwork and
fonts while preserving its banner and burger menu. All 431 website tests pass,
including a WebKit keyboard-viewport opening/panning/dismissal scenario and an
Android control case. Real iPhone keyboard behavior still needs user verification.

- [App selection formatting](test-results/webkit-390-notes-selection.png)
- [Website phone preview](test-results/website-390-reader.png)
- [Website desktop preview](test-results/website-1280-reader.png)
- Current APK: `app/build/outputs/apk/debug/app-debug.apk`, **812,697,482 bytes**.

No adb phone is connected, so the new APK has not been installed. The live
website has not been deployed or restarted for this change. Existing notes and
running backups were not cleared/interrupted.

## Commentary section discovery and compact controls, 9 November 2026

Applied the approved section-navigation concept using the actual bundled section
titles/references. Multi-section chapters show the total, View all (N), numbered
inline themes and Previous / Section X of N / Next navigation. The complete list
opens as a bottom sheet on phones and a centered dialog on desktop, highlights
the selected section and supports long lists. Single-section/full-chapter views
hide the extra navigation. The active inline chip scrolls into view when needed.
The count and theme strip stay with the sticky series controls while reading;
browser checks verify that they remain inside the study pane after selection.

Commentary series buttons are 30 px high (Wiersbe's full series name remains in
its tooltip); inline chapter themes are 32 px high. Full titles and references
remain available in the View all list.

All 20 checks passed, including Chromium desktop/phone and WebKit phone tests.
The tests exercise real Wiersbe Genesis 1 (2 sections), Exalting Jesus John 3
(4 sections), and Exalting Jesus Matthew 5 (9 sections): counts, all choices,
selected titles, first/last navigation limits, Previous/Next, Escape dismissal,
series/chapter changes, single-section hiding and compact control heights.
Test reading positions are reset per browser to avoid sharing navigation state.
Android compilation/lint, debug assembly, signature and 16 KB ZIP alignment pass.

- [Actual four-section phone list](test-results/chromium-390-commentary-sections-4.png)
- [Actual nine-section phone list](test-results/chromium-390-commentary-sections-9.png)
- [Actual commentary reader](test-results/chromium-390-commentary-section-reader.png)
- Current APK: `app/build/outputs/apk/debug/app-debug.apk`, **812,697,225 bytes**.

The connected phone is now absent from adb. This APK has not been installed on
the phone and its physical-device appearance remains to be checked. No live
website, app data or backup was modified to implement these controls.

## Loading states and complete launcher icon, 9 November 2026

Bible startup now says “Preparing Bible…” with an indeterminate loading bar.
Unavailable/empty chapters and failed requests stop the busy state and show an
honest message. Word Study, Concordance, Commentary, Sermon Outlines,
Illustrations and Book Study use matching bars with individual messages.
Dictionary articles, sermon outlines and illustration readers use the same style.

All 20 tests passed, including Chromium desktop/phone and WebKit phone scenarios.
The browser tests deliberately hold Bible and study requests to check visible
loading bars before releasing content and checking that the bars disappear.
Android assembly/lint, APK signature and 16 KB ZIP alignment checks passed.

The launcher uses the original unmodified PNG in an XML inset drawable on a navy
background. Insets preserve its aspect ratio and keep every nontransparent pixel
inside the 66 dp safe circle on the 108 dp adaptive canvas, following
[Android's guidance](https://developer.android.com/develop/ui/compose/system/icon_design_adaptive).
The earlier foreground filled the canvas and was clipped by launcher masks.

- [Bible preparing](test-results/chromium-390-preparing-bible.png)
- [Study preparing](test-results/chromium-390-preparing-commentary.png)
- Latest APK: `app/build/outputs/apk/debug/app-debug.apk`, **812,630,317 bytes**.

The new APK is ready but has not replaced the installed version: Android reports
the phone's SyncService is active. No app restart, force-stop, reinstall or data
clearing was performed during this update. Launcher appearance on the physical
phone still needs verification after this update is installed.

## Physical phone installation, 9 November 2026

The user authorized the connected OPPO A57 (CPH2387), Android 14, arm64 phone
despite initially mentioning an A55. The debug APK was built, installed using
`adb install -r -t`, and launched successfully. No app data was cleared and no
website process or backup was changed.

- APK: `app/build/outputs/apk/debug/app-debug.apk`, **812,509,436 bytes**.
- Android build: `:app:assembleDebug` passed.
- APK signature verification and `zipalign -c -P 16 4` passed.
- ZIP audit found all 32 manifest resources (2,162,016,256 uncompressed bytes),
  with no website environment files, service-account credentials or private
  account/sermon databases.
- Activity launch succeeded; recorded cold launch time was 3,520 ms.
- The first-launch agreement/storage screen renders on the phone. Package logs
  contain no matching fatal exception or Python startup traceback at this check.
- [First-launch screen](test-results/device/first-launch.png).

Agreement acceptance and account login are left to the user. Library preparation,
offline reading, Keystore persistence, native PDF/share and actual Drive round
trips have not yet been verified on the physical phone. Existing desktop/browser
checks below remain useful but do not establish those device results. No release
AAB or Play publication was produced.

## Applied concept login and illustrated tool theme, 9 November 2026

The selected concept login is applied: original emblem, locally bundled lavender
mountains, translucent form, teal Log In button, show/hide password, remembered
sign-in message and measured storage reminder. The rest of the eight-screen
concept remains a proposal.

The Bible and study tab rows are reduced to 34 px. Eight distinct wood/desk
illustrations identify Bible, book study, sermon notes, word study, concordance,
commentary, sermon outlines and sermon illustrations. Compact 49 px phone / 54 px
desktop headers replace the paintbrush treatment. Decorative labels use local
Rye/Bitter fonts; scripture text and stored sermon formatting are preserved.

All 20 source checks pass. Chromium and WebKit tests check every tool view,
distinct scene selection, reduced tab/header heights, removal of the paintbrush
mask, night-mode heading visibility, the new login art and password toggle,
note editing and PDF handoff, with external requests blocked. Android source
compilation and lint pass (no errors). This appearance check preceded the
authorized debug APK build recorded above.

- [Applied login](test-results/preview-login.png)
- [Applied Bible and word-study view](test-results/preview-reader.png)
- [Book study and illustrations](test-results/chromium-390-illustrations.png)
- [Applied artwork and exact generation prompts](design-concepts/APPLIED_ARTWORK_PROMPTS.md)

The running local preview was checked while retaining its remembered account;
it opens directly into the updated Bible reader. The login screenshot comes
from the isolated browser test so no sign-out was needed. The public mobile
endpoint now responds with the expected HTTP 400 username/password validation
message to an empty JSON POST, confirming that it is reachable.

## Appearance update, 9 November 2026

The app header and hamburger drawer are removed. Reading Settings retains saved
reading links and sign-out. The supplied loading art now offers About Publisher
with the two completed profiles; browser preview also shows the loading screen.
The login uses the website's centered glass card, original logo, username and
password fields, green Log In action and account-help text. Local Lora fonts
provide reading typography and Space Grotesk provides interface typography.

The 20 source checks passed after the update. The expanded browser scenarios
also verify header removal, full-height layout, loaded font families, saved
reading access through settings, publisher navigation pausing automatic opening,
the revised login form and sign-in flow. Final Chromium/WebKit checks passed at
desktop/phone sizes; Android source compilation and lint passed without an APK.
The running local preview was checked separately for splash-to-login transition,
no header/drawer and no JavaScript errors.

- [Updated login](test-results/preview-login.png)
- [Updated splash](test-results/preview-splash.png)
- [Updated reader](test-results/chromium-390-reader.png)

Stored personal sermon formatting remains unchanged. Validation also corrected
bookmark labels/removal links in saved reading, and excludes temporary SQLite
journal files from prepared resource inventories.

## Website login integration follow-up, 9 November 2026

The missing live login endpoint was confirmed as HTTP 404. The prepared module
was integrated into the website and published as GitHub commit `a693a49` and
Docker image `pijeme/district4-tool-main:20261109-a693a49`, plus `latest`/`main`.
All 429 website tests pass on Windows. The container run has no failures
(429 discovered, 56 skipped), and all five added API/registration checks pass
inside the container. The local website's mobile endpoint now returns the
expected JSON validation response. The public endpoint was subsequently verified
as reachable too; see `server_integration/INSTALL_AFTER_BACKUP.md`.

The standalone-app checks below remain the recorded source-only verification.

Recorded 9 November 2026 before the authorized phone test above. That source-only
verification did not generate a package or install on a phone/emulator.

## Passed checks

`tests/test_offline.py` passes **20 tests**, including one browser test with three
viewport/engine scenarios. The isolated environment uses Python 3.13.12, Flask
3.1.2 and the pinned desktop requirements. All test writes are under `.test-data`.

| Area | Result |
| --- | --- |
| Loopback access gate, origin validation and CSRF | Pass |
| Agreement, first login and remembered profile | Pass |
| NIV, Cebuano and Tagalog chapter reading with network calls blocked | Pass |
| Word study, three English dictionaries, native-language lookup and concordance | Pass |
| Book study, BE/Wiersbe, Exalting Jesus, Moody and Pulpit | Pass |
| Offline sermon outlines and illustration browsing | Pass |
| Private highlights/bookmarks and local removal | Pass |
| Rich-text sermon note styles, version checks, account separation and deletion | Pass |
| Desktop PDF generation with Unicode/style input | Pass |
| Offline sync failure preserves local notes | Pass |
| Simulated Drive push, website sync coordination and remote deletion applied locally | Pass |
| Account changes blocked during a running backup | Pass |
| Saved study-source annotations, reopening links and deletion | Pass |
| Developer profiles and exclusion of token values from rendered pages | Pass |
| Interrupted setup resume, SHA validation and preservation of changed data | Pass |
| Remembered loopback origin across process restart and native PDF handoff | Pass |
| Website token hashes, scope/revocation, account password change and login throttle | Pass |
| Website role prefixes, including Member, AO and DO aliases | Pass |
| Reuse of an existing website backup job | Pass |
| All 32 shared-resource SHA-256 hashes and absence of private user rows | Pass |
| 24 prepared native-library files checked for 16 KB ELF load alignment | Pass |

Browser scenarios: Chromium at 1280×900 and 390×844, plus WebKit at 390×844.
Each checks offline reader startup, translation switching, compact notes-menu
geometry, note creation/edit/autosave/reopening, PDF download handoff to a native
bridge stub, and navigation to both developer profiles. No external browser
requests, failed resource responses or JavaScript errors were observed.

Review screenshots:

- [Desktop notes menu](test-results/chromium-1280-notes.png)
- [Phone-size Chromium notes menu](test-results/chromium-390-notes.png)
- [Phone-size WebKit notes menu](test-results/webkit-390-notes.png)

Android source tasks completed successfully:

```text
:app:compileDebugJavaWithJavac
:app:lintDebug
:app:mergeDebugNativeLibs
```

Java compilation and lint also pass with `-PplayDelivery=true`. Lint has no
errors; remaining warnings concern JavaScript required by the local reader,
versioned attributes/icon resources, storage allocation suggestions and inlined
Android text-layout constants. They do not establish runtime phone compatibility.
Android native PDF generation uses Android APIs and is compiled here; its
rendered output still requires the later Android device test.

## Adjustments made during validation

- Preserved the website's exact account-role prefixes so mobile sync connects to
  the correct existing notes library for every supported account type.
- Prevented switching accounts while a backup/conversion is running.
- Restored current notes-job progress when the notes screen is recreated.
- Kept a remembered loopback port so WebView local drafts/preferences retain
  their origin after restarting the Android process.
- Used existing website personal-library grouping/deep links for saved items.
- Added interrupted setup/resume checks and refusal to overwrite changed data.
- Removed old Android Pillow/FreeType/JPEG dependencies after detecting 4 KB
  ELF alignment. Android PDF export now uses the platform renderer.
- Added Android data-transfer exclusions for private device authorization.
- Sanitized and vacuumed the shared Bible database, reducing its size while
  removing unused private page data; refreshed the manifest and storage notice.

## Not yet tested or deployed

The live website mobile integration is now reachable, as recorded above.
Automated network tests use fictional accounts and a simulated Drive service.
Real login, Google Drive round trips and developer sermon conversion still need
user-driven verification on the physical phone.

The remaining Android test must verify library setup, storage interruption,
airplane-mode reading, Android Keystore persistence, native PDF rendering and
document picker/sharing, keyboard behavior, Android background limits, process
termination/recovery, and long-note formatting on a real phone. The debug APK
size, signature and ZIP alignment were checked above. Installed footprint,
installer free-space minimum, release signing and Google Play asset delivery
remain unverified. Source checks do not replace those device/release checks.

The startup-preparation build was installed in place on the OPPO A57 on 9 November 2026. The native progress/verse screen was observed, then the reader opened successfully. All 514 sermon-note records and the saved device account were compared against the fresh backup and remained unchanged. Installed runtime sources match the tested build.

Font-row/support update: the six website sermon-editor checks pass; native
Chromium/WebKit verify the support design, Copy, Continue and Escape, including
a warm resume after 72 hours. All 12 offline-engine checks pass, including CSRF,
three-day cadence and persistence across restarts. Debug assembly succeeds.
The update was installed in place on the OPPO A57. All 514 sermon-note records,
the saved account and prepared-library state were verified unchanged. The
phone was unlocked and the installed runtime files were compared with the
tested build. The active Sermon Notes editing session was left intact; the
reminder intentionally defers while editing. Its design and 72-hour timing
were verified in Chromium/WebKit and API checks.


9 November 2026, app-only tutorial update: all 22 automated checks pass
(IOWO_BROWSER_TESTS=1), including Chromium at 1280 and 390 pixels and WebKit at
390 pixels. The eight-step guide, all 42 outline lessons, search/no-results,
Thompson chain demo, selected-text highlight/bold/copy, local-save/sync demo,
reviewed-progress persistence and Back/Skip controls were exercised. Tests
verify no study/account API requests and no changes to sermon-note records.
Native tutorial entry from Reading Settings and splash cancels auto-navigation;
the support card waits for the native guide to close. Tutorial routes retain
the device gate and work before sign-in/setup. Debug assembly succeeds; signing
certificate, library manifest and APK tutorial/runtime assets match expectations.

The tutorial build was installed in place on the OPPO A57 (CPH2387).
A fresh private backup was taken before installation. All 514 sermon-note
records, saved encrypted account and prepared-library state were compared
before first launch and remained unchanged. Installed runtime/tutorial assets
match the tested APK. On the unlocked phone the guided tour was observed on
Thompson Chain Index, step 2 of 8. The active tutorial session was left intact
for the user to test. Launcher foreground insets preserve the original bitmap
and its alpha>=8 silhouette inside a 70dp circular mask on the 108dp layer;
visible scale increases approximately 7.7 percent. The home-screen icon was
not opened for a separate screenshot during the user's active tutorial.
Website source remains unchanged; Android source remains local.


Screenshot tutorial update, 9 November 2026: the sandbox activities were
replaced by one annotated actual-app screenshot per topic. The 42 topics share
27 WebP files totaling 619,748 bytes; numbering/arrows are vectors and labels
remain readable text. Six key figures were visually inspected (passage
selector, Thompson topic, sermon highlight, font tools, native startup and
splash Tutorials). The startup source was freshly captured on the unlocked
OPPO A57; browser captures use only a fictional account and sample note in
an isolated test folder. Thumbnail, modal enlargement, zoom/fit, Back/Escape,
outline search, hash navigation and persistent reviewed markers are covered.
Every topic's image decodes, all arrows have matching labels, and no study
API requests or sermon-note changes occur while viewing tutorials. The
screenshot route preserves the device gate and blocks unrelated files.

All 22 automated checks passed for the screenshot update (96.9 seconds), and
Android debug assembly succeeded. The APK was installed in place on the OPPO
A57. Its certificate and bundled library manifest match the prior installation.
A fresh backup was taken; all 514 sermon-note records, encrypted sign-in and
prepared-library state were compared after installation and before reopening,
and remained unchanged. Installed tutorial HTML/CSS/JavaScript, screenshot
manifest and all WebP files match the tested build. The tutorial welcome flag
was reset for the user's requested first-opening retest. The screenshot tour
was observed on the unlocked device, including the Thompson Chain Index image
and instructions. The active tutorial session was left intact for the user.
Website source was not modified and Android source remains local.


Release 1.0.1 (2): retired sermon conversion in app and website, including its
UI action, API capability and tutorial. Existing note storage and online sync
remain unchanged. The guide now has 41 topics. Screenshot assets were refreshed
without the conversion control. An offline privacy page and corresponding
public website routes are supplied for store preparation.

The production APK and Play AAB were signed with a new private production key.
The separate debug APK preserves compatibility with the existing OPPO test
installation. Bundletool validates the AAB; it has a base module and three
install-time asset packs. APK/AAB signature checks, native 16KB ELF load/ZIP
alignment and PAGE_ALIGNMENT_16K bundle configuration pass. Release metadata
is in Google-Play/validation/release-verification.json outside source. Play
listing graphics and six 1080x1920 screenshots use fictional data.

All 22 Android checks pass for release 1.0.1 (109 seconds), including Chromium
and WebKit. The compatible debug update was installed in place on the OPPO A57.
A fresh backup and record-by-record comparison verify all 514 sermon notes,
saved sign-in and prepared-library state unchanged. The production sharing APK
is separately release-signed and is intended for new installations. Play
submission and Play-delivered asset-pack installation remain owner-side steps.
