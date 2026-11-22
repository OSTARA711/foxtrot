# Foxtrot Source Cleanup Audit

**Repository:** `OSTARA711/foxtrot`
**Working branch:** `main`
**Baseline commit:** `d429867af0` — Remove mobile download promotions and obsolete build images
**Audit status:** Source-level review; build validation pending

## 1. Purpose and scope

This document records the Foxtrot source cleanup and platform-exclusion work
reviewed during the current development session. It is intended to preserve
the decisions, findings, completed changes, retained shared code, and
outstanding work.

This is not a claim that every Android or mobile reference has been removed,
nor that the browser has been successfully built after these changes.

Foxtrot is intended as a Linux desktop browser and distribution, targeting:

- x86_64 (`amd64`)
- ARM64 (`aarch64`)

The intended product excludes:

- Android and mobile browser products.
- Windows and macOS product builds.
- Snap and Flatpak packaging or runtime support.
- Non-English localisation and translation functionality; the product is
  en-US only.
- Integrated AI features and their associated model/runtime delivery.
- Browser page translation and its associated models/runtime.
- Pocket, sponsored Discovery Stream content, mobile download promotions,
  and unrelated mobile product integrations.

Shared Mozilla code should be retained where it is genuinely required by
the Linux desktop browser. A reference to another platform is not, by itself,
sufficient reason to delete shared code.

## 2. Working-tree state and review limitations

At the time of this audit:

- The working branch is `main`.
- The last known baseline commit is `d429867af0`.
- The cleanup changes are local working-tree changes.
- The YouTube mobile PiP intervention and its registration are removed in
  the working tree.
- The cumulative diff contained 52 modified or deleted tracked files before
  this audit document was added.
- `git diff --check` produced no reported whitespace errors.
- No full Linux x86_64 build or test run has been completed.
- No full Linux ARM64 build or test run has been completed.
- No security-patch migration is claimed by this audit.
- No commit is represented by this document.

The review was based on source diffs, targeted searches, build configuration
inspection, and dependency tracing. Source-level inspection does not replace
compiler, linker, packaging, or runtime validation.

## 3. GeckoView History removal

The desktop browser uses Places for browsing history. The Android
GeckoView-specific history integration was removed from shared desktop paths.

Changes reviewed:

- `dom/push/PushRecord.sys.mjs`
  - Removed the GeckoView History event-dispatch path and related lazy
    dependency.
  - Retained the Places-backed history query.
- `dom/ipc/BrowserParent.cpp`
- `dom/ipc/BrowserParent.h`
- `dom/ipc/PBrowser.ipdl`
  - Removed the Android-only visited-state IPC method.
- `toolkit/moz.configure`
  - Removed the GeckoView History project option and its Places conflict
    check.
- `toolkit/modules/AppConstants.sys.mjs`
- `toolkit/modules/moz.build`
- `tools/@types/subs/AppConstants.sys.d.mts`
  - Removed the generated GeckoView History constant and declaration.
- `python/mozperftest/mozperftest/tests/data/browsertime-results-video/browsertime.json`
  - Removed obsolete fixture properties for the removed option.

Places itself and its desktop history implementation remain in scope.

## 4. Shared GeckoView branch cleanup

Android GeckoView-only branches were removed from shared desktop source
where a desktop implementation already existed.

Changes reviewed:

- `dom/clients/manager/ClientOpenWindowUtils.cpp`
  - Made the desktop `OpenWindow()` implementation unconditional.
  - Removed the GeckoView-specific window-opening implementation and
    dispatch path.
- `dom/ipc/ContentParent.cpp`
  - Removed a GeckoView-specific failure branch while retaining the desktop
    new-window fallback.
- `toolkit/actors/AutoCompleteParent.sys.mjs`
  - Removed GeckoView autocomplete delegation and retained desktop popup
    handling.
- `toolkit/components/formautofill/FormAutofillChild.sys.mjs`
  - Removed a GeckoView-specific condition while retaining the remaining
    platform check still used by the file.
- `toolkit/components/windowwatcher/nsWindowWatcher.cpp`
  - Removed GeckoView-specific window-opening, tab-forcing, and preference
    restriction branches.
  - Retained desktop window handling and restriction logic.

The generated `MOZ_GECKOVIEW` constant and its TypeScript declaration were
also removed from:

- `toolkit/modules/AppConstants.sys.mjs`
- `tools/@types/subs/AppConstants.sys.d.mts`

## 5. Extension test infrastructure

The GeckoView-only extension test mode and its Java embedding notifications
were removed.

Changes reviewed:

- `toolkit/components/extensions/ExtensionTestCommon.sys.mjs`
  - Removed the `geckoview-only` AddonManager mode.
  - Retained ordinary AddonManager test support.
- `testing/specialpowers/content/SpecialPowersParent.sys.mjs`
  - Removed automatic selection of the GeckoView-only mode.
- `toolkit/components/extensions/ExtensionXPCShellUtils.sys.mjs`
  - Removed GeckoView Java embedding install/uninstall notifications.
- Four browser-action popup tests no longer request the removed mode:
  - `toolkit/components/extensions/test/mochitest/test_ext_browserAction_openPopup.html`
  - `toolkit/components/extensions/test/mochitest/test_ext_browserAction_openPopup_incognito_window.html`
  - `toolkit/components/extensions/test/mochitest/test_ext_browserAction_openPopup_windowId.html`
  - `toolkit/components/extensions/test/mochitest/test_ext_browserAction_openPopup_without_pref.html`

The tests themselves and ordinary extension test infrastructure remain.

## 6. Android build configuration cleanup

Android application packaging and GeckoView archive build targets were
removed from central build orchestration.

Changes reviewed:

- `Makefile.in`
  - Removed Android fat-AAR, Android stage-package, and GeckoView archive
    target rules.
  - Retained unrelated build rules.
- `config/baseconfig.mk`
  - Removed Android-specific tiers and their runnable-tier filters.
- `build/moz.configure/init.configure`
  - Removed project-specific Android/iOS target inference.
  - Retained host-based target defaults and CPU target expansion.
- `build/moz.configure/bindgen.configure`
  - Restricted the relevant project condition to the browser project.
- `build/moz.configure/update-programs.configure`
  - Removed the Android application-specific updater default while retaining
    the iOS target restriction.
- `moz.configure`
  - Removed mobile Android from the relevant GTest project whitelist and
    Visual Studio backend exclusion.
  - Removed an obsolete Fennec-specific comment.
- `pyproject.toml`
  - Removed the mobile Android configure-file exclusion.

The Android-only `config/recurse.mk` pre-export rule was identified but
retained pending the broader Android target/configuration audit.

Generic cross-compilation and target-platform code was not removed merely
because it contains Android conditions. Its remaining consumers require
separate review.

## 7. Accessibility and HAL build selection

Android accessibility build selection and Android HAL source selection were
removed from desktop build paths.

Accessibility changes reviewed:

- `accessible/moz.build`
- `accessible/aom/moz.build`
- `accessible/base/moz.build`
- `accessible/generic/moz.build`
- `accessible/html/moz.build`
- `accessible/xpcom/moz.build`
- `accessible/xul/moz.build`

The Android accessibility implementation directory was not deleted.
Shared accessibility APIs and non-Android platform implementations remain.

`hal/moz.build`:

- Removed the Android-only HAL source/include branch.
- Made the Linux HAL branch independent of the removed Android alternative.
- Retained shared HAL sources and fallback implementations.

The `hal/android/` directory was not deleted.

## 8. Widget and input platform cleanup

Android-specific widget selection and input handling were removed from
shared desktop build paths.

Changes reviewed:

- `widget/moz.build`
  - Removed Android platform directory selection and Android-specific
    IDL/IPDL/source selection.
  - Retained the UIKit-specific branch.
  - Retained `ScrollbarDrawingAndroid.cpp`, which is still referenced by
    shared scrollbar drawing use cases.
- `widget/Theme.cpp`
  - Removed the Android native theme factory and native scrollbar fallback.
  - Retained shared scrollbar drawing use, including the Android-named
    drawing implementation used by other code paths.
- `widget/headless/HeadlessWidget.h`
  - Removed Android-specific headless scroll constants.
  - Retained other platform definitions and generic fallback values.
- `widget/nsBaseWidget.cpp`
  - Removed Android-only WebRender/compositor setup branches and the
    Android-specific bidi keyboard fallback.
  - Retained Android guards around quit-application IME observer handling
    because the safety of removing that path was not established.
- `widget/nsUserIdleService.cpp`
  - Removed Android-specific logging code.
- `widget/GfxDriverInfo.h`
- `widget/GfxInfoBase.cpp`
  - Removed Android-specific driver-version parsing and comparison paths.
- `widget/IMEData.h`
  - Removed Android-specific IME capability checks while retaining GTK,
    Windows, macOS, and iOS conditions.
- `widget/WidgetEventImpl.cpp`
  - Removed Android-only multimedia and Japanese keyboard mappings.
- `widget/NativeKeyToDOMCodeName.h`
- `widget/NativeKeyToDOMKeyName.h`
  - Removed Android native-key mapping macros and entries.
  - Retained Windows, macOS, and GTK mappings.

The following changes also remove Android-only build selection or includes:

- `gfx/vr/moz.build`
  - Makes the VR service directory and `VRServiceHost.cpp` unconditional
    instead of selecting the Android widget include branch.
- `mozglue/moz.build`
  - Removes the Android mozglue directory from build selection.
- `ipc/glue/test/gtest/moz.build`
  - Removes the Android widget include.

These changes are source-reviewed but not build-verified. In particular,
the VR and mozglue changes must be covered by the subsequent Linux build
and dependency checks.

## 9. Mobile YouTube PiP intervention

The Mobile YouTube picture-in-picture workaround was removed because it
depends on the Android-specific `Document.inAndroidPipMode` feature.

Removed:

- `browser/extensions/webcompat/injections/js/bug1956165-www.youtube.com-picture-in-picture-fix.js`
- Its matching registration in
  `browser/extensions/webcompat/data/interventions.json`

The intervention was identified as a Mobile YouTube fix and checked the
Android PiP state. Its JavaScript file and JSON registration were both
removed from the local working tree.

This change removes that particular WebCompat intervention only. It does
not mean that the complete Android PiP API or its IPC and media-feature
plumbing has been removed.

## 10. Android and mobile dependency findings

The following findings were established during targeted searches and source
inspection.

### 10.1 `mobile/` directory

The agreed deletion sequence is:

1. Finish auditing shared-source GeckoView/mobile branch cleanup.
2. Audit all `mobile/` references across build configuration, Python tooling,
   manifests, tests, CI, and packaging.
3. Remove or adapt references that would break Linux desktop builds.
4. Audit `widget/android/` separately.
5. Delete `mobile/` in one dedicated, reviewable change.
6. Validate clean Linux x86_64 and ARM64 desktop builds.

The `mobile/` directory has not yet been deleted.

### 10.2 `widget/android/`

`widget/android/` is a dedicated Android widget implementation and is
separate from `mobile/`. It contains Android widget, compositor, JNI,
Java-binding, window, clipboard, VSync, and related implementation code.

Its consumers and build selectors require a complete audit before deletion.
It has not been deleted.

### 10.3 Accessibility Android implementation

Android accessibility build selection was removed from the shared
`accessible/moz.build` hierarchy, but `accessible/android/` remains in the
source tree. Its eventual deletion should be coordinated with the
`widget/android/` and Android target audits.

### 10.4 Dynamic toolbar and keyboard IPC

The Android dynamic toolbar and keyboard notification path was traced
through:

`widget/android/nsWindow` → `nsView` → `BrowserParent` →
`PBrowser.ipdl` → `BrowserChild` → desktop/shared viewport consumers.

The relevant BrowserChild state and getters include dynamic toolbar height
and keyboard height. `PresShell.cpp` has a keyboard-height consumer, so
removal must adapt that call while preserving generic viewport and keyboard
APIs.

The full dynamic toolbar and keyboard IPC chain has not yet been removed.

### 10.5 Android PiP API and media feature

The Android PiP state path was traced through:

- `BrowserParent` and `PBrowser.ipdl`
- `BrowserChild`
- `Document`
- `Document.webidl`
- Gecko media feature bindings
- Servo Gecko media-feature implementation
- the Mobile YouTube WebCompat intervention

The WebCompat intervention has been removed. The Android-specific
`Document.inAndroidPipMode` API and associated IPC/media-feature plumbing
have not yet been removed.

### 10.6 Compositor toolbar and screen-pixel IPC

Android-only toolbar and screen-pixel message paths were identified in
widget and compositor code, including `UiCompositorControllerChild`,
`UiCompositorControllerParent`, and WebRender/compositor bridge code.

Shared compositor functionality such as compositor scroll updates and
general lifecycle messages must be preserved. Android-only messages and
their cached state require a coordinated audit before removal.

### 10.7 Other platform code retained pending review

The following were deliberately not removed wholesale:

- Shared Places history and database APIs.
- Shared viewport and keyboard APIs.
- Shared HAL interfaces and Linux fallback implementations.
- Shared VR and OOP compositing abstractions.
- Shared print settings interfaces and non-Android implementations.
- Shared file-picker APIs.
- Shared accessibility interfaces.
- Shared GTK/Linux, Windows, macOS, and UIKit code paths.
- Generic Android cross-compilation/configuration branches whose remaining
  consumers have not been fully scoped.
- UIKit code and its GeckoView-named support files; these are iOS-specific
  and were not assumed to be Android code.
- `ScrollbarDrawingAndroid` because it remains used by shared code paths.

## 11. Remaining work

The following work remains outstanding:

1. Complete the repository-wide `mobile/` reference audit.
2. Complete the separate `widget/android/` dependency audit.
3. Decide and implement removal of the remaining Android dynamic toolbar
   and keyboard IPC chain.
4. Decide and implement removal of the Android PiP API, WebIDL, media
   feature, and associated bindings if required by the product scope.
5. Complete the Android compositor toolbar and screen-pixel IPC audit.
6. Review remaining Android build/configuration and test infrastructure,
   removing only code no longer needed by supported targets.
7. Delete `mobile/` in the agreed dedicated change after its references are
   resolved.
8. Complete clean Linux x86_64 and ARM64 builds.
9. Run the relevant test suites and packaging checks.
10. Review the complete cumulative diff before committing.

## 12. Validation and security claims

The reported `git diff --check` result was clean at the time of the working
tree inspection.

No successful full build, test suite, package build, or runtime validation
is claimed here.

This audit does not claim that ESR153 security patches have been migrated
to the ESR140.16.0 baseline. Any such migration must be assessed
individually against the actual source changes and Foxtrot product
requirements. No security fix should be considered migrated without
source-level evidence.

## 13. Changed files reviewed

The cumulative tracked-file status before adding this document listed the
following paths:

- `Makefile.in`
- `accessible/aom/moz.build`
- `accessible/base/moz.build`
- `accessible/generic/moz.build`
- `accessible/html/moz.build`
- `accessible/moz.build`
- `accessible/xpcom/moz.build`
- `accessible/xul/moz.build`
- `browser/extensions/webcompat/data/interventions.json`
- `browser/extensions/webcompat/injections/js/bug1956165-www.youtube.com-picture-in-picture-fix.js`
- `build/moz.configure/bindgen.configure`
- `build/moz.configure/init.configure`
- `build/moz.configure/update-programs.configure`
- `config/baseconfig.mk`
- `dom/clients/manager/ClientOpenWindowUtils.cpp`
- `dom/ipc/BrowserParent.cpp`
- `dom/ipc/BrowserParent.h`
- `dom/ipc/ContentParent.cpp`
- `dom/ipc/PBrowser.ipdl`
- `dom/push/PushRecord.sys.mjs`
- `gfx/vr/moz.build`
- `hal/moz.build`
- `ipc/glue/test/gtest/moz.build`
- `moz.configure`
- `mozglue/moz.build`
- `pyproject.toml`
- `python/mozperftest/mozperftest/tests/data/browsertime-results-video/browsertime.json`
- `testing/specialpowers/content/SpecialPowersParent.sys.mjs`
- `toolkit/actors/AutoCompleteParent.sys.mjs`
- `toolkit/components/extensions/ExtensionTestCommon.sys.mjs`
- `toolkit/components/extensions/ExtensionXPCShellUtils.sys.mjs`
- `toolkit/components/extensions/test/mochitest/test_ext_browserAction_openPopup.html`
- `toolkit/components/extensions/test/mochitest/test_ext_browserAction_openPopup_incognito_window.html`
- `toolkit/components/extensions/test/mochitest/test_ext_browserAction_openPopup_windowId.html`
- `toolkit/components/extensions/test/mochitest/test_ext_browserAction_openPopup_without_pref.html`
- `toolkit/components/formautofill/FormAutofillChild.sys.mjs`
- `toolkit/components/windowwatcher/nsWindowWatcher.cpp`
- `toolkit/modules/AppConstants.sys.mjs`
- `toolkit/modules/moz.build`
- `toolkit/moz.configure`
- `tools/@types/subs/AppConstants.sys.d.mts`
- `widget/GfxDriverInfo.h`
- `widget/GfxInfoBase.cpp`
- `widget/IMEData.h`
- `widget/NativeKeyToDOMCodeName.h`
- `widget/NativeKeyToDOMKeyName.h`
- `widget/Theme.cpp`
- `widget/WidgetEventImpl.cpp`
- `widget/headless/HeadlessWidget.h`
- `widget/moz.build`
- `widget/nsBaseWidget.cpp`
- `widget/nsUserIdleService.cpp`

This list records the working-tree paths observed during the audit. It does
not imply that every line in every file has been independently reviewed
against a complete build.
