# Foxtrot Source Cleanup Audit

**Repository:** `OSTARA711/foxtrot`  
**Working branch:** `main`  
**Baseline commit:** `d429867af0` — Remove mobile download promotions and obsolete build images  
**Latest reviewed commit:** `6ab711feb9` — Remove remaining Android-only platform code  
**Audit status:** Source-level review of committed cleanup; full build and test validation pending

## 1. Purpose and scope

This document records the Foxtrot source cleanup and platform-exclusion work reviewed during the development sessions. It preserves the product decisions, findings, completed changes, retained shared code, and outstanding work.

This is not a claim that every Android or mobile reference has been removed, nor that the browser has been successfully built after these changes.

Foxtrot is intended as a Linux desktop browser and distribution, targeting:

- x86_64 (`amd64`)
- ARM64 (`aarch64`)

The intended product excludes:

- Android and mobile browser products.
- Windows and macOS product builds.
- Snap and Flatpak packaging or runtime support.
- Non-English localisation and translation functionality; the product is en-US only.
- Integrated AI features and their associated model/runtime delivery.
- Browser page translation and its associated models/runtime.
- Pocket, sponsored Discovery Stream content, mobile download promotions, and unrelated mobile product integrations.

Shared Mozilla code should be retained where it is genuinely required by the Linux desktop browser. A reference to another platform is not, by itself, sufficient reason to delete shared code.

## 2. Repository state and review limitations

The audit began with commit `d429867af0` and has subsequently been
extended to cover the committed cleanup through:

`4e270fde415364964912c5e88e110fa8041e1788`

The latest observed repository commit on `main` is `4e270fde41`.

The Thunderbird and Mochitest cleanup was committed in two stages:

- `cd01d06b84` — Remove Android and Thunderbird Mochitest support.
- `4e270fde41` — Remove Thunderbird-specific code paths.

The latest commit also contains Android-related changes. Those changes are
not all part of the Thunderbird cleanup.

The original GeckoView and Android desktop cleanup was committed in `821e313534`. Subsequent commits extended the removal to Android build tooling, audio backends, performance infrastructure, accessibility, compositor-controller and HardwareBuffer implementations.

The relevant cleanup commits include:

- `821e313534` — Remove GeckoView and Android-only desktop build paths.
- `9a4d014353` — Remove the root Taskcluster directory and its Taskgraph implementation.
- `04f050adfe` — Remove Android cubeb audio backends.
- `4c8f408406` — Remove Android NDK configuration and bootstrap support.
- `512a1eb07f` — Remove Android performance profiling and startup benchmarks.
- `707aafab05` — Improve local Raptor performance testing.
- `6ab711feb9` — Remove remaining Android-only platform code.

These changes are committed to `main`. This document does not assert that the local working tree is clean; that must be checked independently.

No full Linux x86_64 build or test run is established by this audit.

No full Linux ARM64 build or test run is established by this audit.

No successful package build or runtime validation is claimed.

The review is based on committed source changes, targeted searches, build configuration inspection and dependency tracing. Source-level inspection does not replace compiler, linker, packaging or runtime validation.

## 3. GeckoView History removal

The desktop browser uses Places for browsing history. The Android GeckoView-specific history integration was removed from shared desktop paths.

Changes reviewed:

- `dom/push/PushRecord.sys.mjs`
  - Removed the GeckoView History event-dispatch path and related lazy dependency.
  - Retained the Places-backed history query.
- `dom/ipc/BrowserParent.cpp`
- `dom/ipc/BrowserParent.h`
- `dom/ipc/PBrowser.ipdl`
  - Removed the Android-only visited-state IPC method.
- `toolkit/moz.configure`
  - Removed the GeckoView History project option and its Places conflict check.
- `toolkit/modules/AppConstants.sys.mjs`
- `toolkit/modules/moz.build`
- `tools/@types/subs/AppConstants.sys.d.mts`
  - Removed the generated GeckoView History constant and declaration.
- `python/mozperftest/mozperftest/tests/data/browsertime-results-video/browsertime.json`
  - Removed obsolete fixture properties for the removed option.

Places itself and its desktop history implementation remain in scope.

## 4. Shared GeckoView branch cleanup

Android GeckoView-only branches were removed from shared desktop source where a desktop implementation already existed.

Changes reviewed:

- `dom/clients/manager/ClientOpenWindowUtils.cpp`
  - Made the desktop `OpenWindow()` implementation unconditional.
  - Removed the GeckoView-specific window-opening implementation and dispatch path.
- `dom/ipc/ContentParent.cpp`
  - Removed a GeckoView-specific failure branch while retaining the desktop new-window fallback.
- `toolkit/actors/AutoCompleteParent.sys.mjs`
  - Removed GeckoView autocomplete delegation and retained desktop popup handling.
- `toolkit/components/formautofill/FormAutofillChild.sys.mjs`
  - Removed a GeckoView-specific condition while retaining the remaining platform check still used by the file.
- `toolkit/components/windowwatcher/nsWindowWatcher.cpp`
  - Removed GeckoView-specific window-opening, tab-forcing, and preference restriction branches.
  - Retained desktop window handling and restriction logic.

The generated `MOZ_GECKOVIEW` constant and its TypeScript declaration were also removed from:

- `toolkit/modules/AppConstants.sys.mjs`
- `tools/@types/subs/AppConstants.sys.d.mts`

## 5. Extension test infrastructure

The GeckoView-only extension test mode and its Java embedding notifications were removed.

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

Android application packaging and GeckoView archive build targets were removed from central build orchestration.

Changes reviewed:

- `Makefile.in`
  - Removed Android fat-AAR, Android stage-package, and GeckoView archive target rules.
  - Retained unrelated build rules.
- `config/baseconfig.mk`
  - Removed Android-specific tiers and their runnable-tier filters.
- `build/moz.configure/init.configure`
  - Removed project-specific Android/iOS target inference.
  - Retained host-based target defaults and CPU target expansion.
- `build/moz.configure/bindgen.configure`
  - Restricted the relevant project condition to the browser project.
- `build/moz.configure/update-programs.configure`
  - Removed the Android application-specific updater default while retaining the iOS target restriction.
- `moz.configure`
  - Removed mobile Android from the relevant GTest project whitelist and Visual Studio backend exclusion.
  - Removed an obsolete Fennec-specific comment.
- `pyproject.toml`
  - Removed the mobile Android configure-file exclusion.

The Android-only `config/recurse.mk` pre-export rule was identified but retained pending the broader Android target/configuration audit.

Generic cross-compilation and target-platform code was not removed merely because it contains Android conditions. Its remaining consumers require separate review.

## 7. Accessibility and HAL build selection

Android accessibility build selection and Android HAL source selection were removed from desktop build paths.

Accessibility changes reviewed:

- `accessible/moz.build`
- `accessible/aom/moz.build`
- `accessible/base/moz.build`
- `accessible/generic/moz.build`
- `accessible/html/moz.build`
- `accessible/xpcom/moz.build`
- `accessible/xul/moz.build`

The Android accessibility implementation directory `accessible/android/` was subsequently deleted in commit `6ab711feb9`.

Shared accessibility APIs and non-Android platform implementations remain. This deletion does not establish that every Android-related accessibility reference has been removed from the repository.

`hal/moz.build`:

- Removed the Android-only HAL source/include branch.
- Made the Linux HAL branch independent of the removed Android alternative.
- Retained shared HAL sources and fallback implementations.

The `hal/android/` directory has not been established as deleted and remains a separate dependency-audit item.

## 8. Widget and input platform cleanup

Android-specific widget selection and input handling were removed from shared desktop build paths.

Changes reviewed:

- `widget/moz.build`
  - Removed Android platform directory selection and Android-specific IDL/IPDL/source selection.
  - Retained the UIKit-specific branch.
  - Retained `ScrollbarDrawingAndroid.cpp`, which is still referenced by shared scrollbar drawing use cases.
- `widget/Theme.cpp`
  - Removed the Android native theme factory and native scrollbar fallback.
  - Retained shared scrollbar drawing use, including the Android-named drawing implementation used by other code paths.
- `widget/headless/HeadlessWidget.h`
  - Removed Android-specific headless scroll constants.
  - Retained other platform definitions and generic fallback values.
- `widget/nsBaseWidget.cpp`
  - Removed Android-only WebRender/compositor setup branches and the Android-specific bidi keyboard fallback.
  - Retained Android guards around quit-application IME observer handling because the safety of removing that path was not established.
- `widget/nsUserIdleService.cpp`
  - Removed Android-specific logging code.
- `widget/GfxDriverInfo.h`
- `widget/GfxInfoBase.cpp`
  - Removed Android-specific driver-version parsing and comparison paths.
- `widget/IMEData.h`
  - Removed Android-specific IME capability checks while retaining GTK, Windows, macOS, and iOS conditions.
- `widget/WidgetEventImpl.cpp`
  - Removed Android-only multimedia and Japanese keyboard mappings.
- `widget/NativeKeyToDOMCodeName.h`
- `widget/NativeKeyToDOMKeyName.h`
  - Removed Android native-key mapping macros and entries.
  - Retained Windows, macOS, and GTK mappings.

The following changes also remove Android-only build selection or includes:

- `gfx/vr/moz.build`
  - Makes the VR service directory and `VRServiceHost.cpp` unconditional instead of selecting the Android widget include branch.
- `mozglue/moz.build`
  - Removes the Android mozglue directory from build selection.
- `ipc/glue/test/gtest/moz.build`
  - Removes the Android widget include.

These changes are source-reviewed but not build-verified. In particular, the VR and mozglue changes must be covered by the subsequent Linux build and dependency checks.

## 9. Mobile YouTube PiP intervention

The Mobile YouTube picture-in-picture workaround was removed because it depends on the Android-specific `Document.inAndroidPipMode` feature.

Removed:

- `browser/extensions/webcompat/injections/js/bug1956165-www.youtube.com-picture-in-picture-fix.js`
- Its matching registration in `browser/extensions/webcompat/data/interventions.json`

The intervention was identified as a Mobile YouTube fix and checked the Android PiP state. Its JavaScript file and JSON registration were removed in the original cleanup commit.

The WebCompat intervention was removed in the earlier cleanup. The native Android PiP API, IPC messages, Document WebIDL attribute, CSS media feature, preference, static atoms and Gecko media-feature bindings have since been removed in the native platform cleanup.

## 10. Android and mobile dependency findings

The following findings were established during targeted searches, source inspection and subsequent committed cleanup.

### 10.1 `mobile/` directory

The agreed deletion sequence is:

1. Finish auditing shared-source GeckoView/mobile branch cleanup.
2. Audit all `mobile/` references across build configuration, Python tooling, manifests, tests, CI, and packaging.
3. Remove or adapt references that would break Linux desktop builds.
4. Audit `widget/android/` separately.
5. Delete `mobile/` in one dedicated, reviewable change.
6. Validate clean Linux x86_64 and ARM64 desktop builds.

The `mobile/` directory has not yet been established as deleted.

### 10.2 `widget/android/`

`widget/android/` is a dedicated Android widget implementation and is separate from `mobile/`. It contains Android widget, compositor, JNI, Java-binding, window, clipboard, VSync, and related implementation code.

Its consumers and build selectors require a complete audit before deletion. It has not been established as deleted.

### 10.3 Accessibility Android implementation

The Android accessibility build selection was removed from the shared `accessible/moz.build` hierarchy.

The `accessible/android/` implementation directory was subsequently deleted in commit `6ab711feb9`.

Shared accessibility interfaces and non-Android implementations remain. Any remaining references to Android accessibility types or build targets still require verification.

### 10.4 Dynamic toolbar and keyboard IPC

The Android dynamic toolbar and keyboard notification path was traced through:

`widget/android/nsWindow` → `nsView` → `BrowserParent` → `PBrowser.ipdl` → `BrowserChild` → desktop/shared viewport consumers.

The relevant BrowserChild state and getters include dynamic toolbar height and keyboard height. `PresShell.cpp` has a keyboard-height consumer, so removal must adapt that call while preserving generic viewport and keyboard APIs.

The Android keyboard-height notification path has now been removed from the native widget, view and BrowserChild/BrowserParent IPC chain. The PresShell initialisation from BrowserChild has also been removed. Generic keyboard-height and viewport handling in MobileViewportManager and nsPresContext remains intact. The Android dynamic-toolbar path is a separate outstanding audit item.

### 10.5 Android PiP API and media feature

The Android PiP state path was traced through:

- `BrowserParent` and `PBrowser.ipdl`
- `BrowserChild`
- `Document`
- `Document.webidl`
- Gecko media feature bindings
- Servo Gecko media-feature implementation
- The Mobile YouTube WebCompat intervention

The native Android PiP API and its IPC, Document WebIDL, CSS media-feature, preference, static-atom and Servo binding paths have now been removed. The remaining PiP references are in the Android Java/GeckoView product, including GeckoSession and CompositorController. These belong to the separate mobile-product removal. The generated TypeScript declaration for Document.inAndroidPipMode must be regenerated through the normal bindings generation process rather than edited manually.

### 10.6 Compositor toolbar and screen-pixel IPC

Android-only toolbar and screen-pixel message paths were identified in widget and compositor code, including `UiCompositorControllerChild`, `UiCompositorControllerParent`, and WebRender/compositor bridge code.

The dedicated UI compositor-controller IPDL interface and its Android implementation files were subsequently deleted in commit `6ab711feb9`.

The Android HardwareBuffer implementations and their WebRender and shared-surface integrations were also deleted.

Shared compositor functionality was adapted rather than deleted wholesale. Remaining Android-specific compositor messages, cached state and screen-pixel paths still require dependency review.

The Android dynamic toolbar and keyboard IPC chain is a separate outstanding investigation.

### 10.7 Subsequent committed Android platform cleanup

The following additional changes were committed after the original GeckoView and desktop build-path cleanup.

#### Android audio backends — `04f050adfe`

- Removed AAudio, OpenSL ES and AudioTrack backend implementations.
- Removed Android-specific cubeb JNI helpers and associated build configuration, telemetry entries and tests.
- Retained generic audio infrastructure.
- Retained Android platform exclusions for OSS, PulseAudio and sndio while Android target support remained elsewhere in the build configuration at that stage.

#### Android NDK and bootstrap — `4c8f408406`

- Removed Android NDK compiler and linker integration.
- Removed Android-specific toolchain flags, sysroot handling and STLPort configuration.
- Removed Android bootstrap methods and platform-specific mozboot mixins.
- Cleaned Android-specific branches in shared mozbuild infrastructure.
- Preserved Linux desktop build support for amd64 and aarch64.

#### Android performance profiling — `512a1eb07f`

- Removed the Simpleperf profiler and its Android NDK integration.
- Removed the Android mobile-startup benchmark suite and its dedicated alert fixtures and test case.
- Removed the unused ProfilingMediator abstraction and its unit test.
- Preserved desktop performance tests, generic profiling infrastructure and Android Raptor alert tests.

The removal of the Android startup benchmark suite does not imply that all Android-related performance test references were removed.

#### Taskcluster infrastructure — `9a4d014353`

- Removed the root `taskcluster/` directory and its Taskgraph implementation.
- Removed its Docker images, task definitions, scripts, tests and documentation.
- Unregistered the directory from the root `moz.build` configuration.

This was a broader build-infrastructure removal, not exclusively an Android cleanup.

#### Local Raptor performance testing — `707aafab05`

- Retained local Raptor and Talos testing while removing obsolete Taskcluster performance documentation and lint integrations.
- Improved Node.js discovery and Raptor setup so an existing local Node.js installation does not trigger unnecessary Taskcluster dependencies.
- Removed automatic FFmpeg downloads and made FFmpeg and visual-metrics dependencies conditional on requested benchmark features.
- Added support for system-provided FFmpeg without architecture-specific bundled binaries.
- Improved Speedometer benchmark repository cache validation and recovery.
- Fixed Python 3.13 debug-mode timeout handling by replacing an unsafe `sys.maxsize` timeout with a bounded 24-hour timeout.
- Preserved the existing Firefox Window Recorder path and normal benchmark operation without requiring FFmpeg.

This commit improves local performance-testing infrastructure. It does not establish that Foxtrot itself has been built or benchmarked successfully.

#### Accessibility, compositor and HardwareBuffer implementations — `6ab711feb9`

Deleted Android-only implementations and associated registrations:

- `accessible/android/`
- `gfx/gl/SharedSurfaceAndroidHardwareBuffer.cpp`
- `gfx/gl/SharedSurfaceAndroidHardwareBuffer.h`
- `gfx/layers/AndroidHardwareBuffer.cpp`
- `gfx/layers/AndroidHardwareBuffer.h`
- `gfx/webrender_bindings/RenderAndroidHardwareBufferTextureHost.cpp`
- `gfx/webrender_bindings/RenderAndroidHardwareBufferTextureHost.h`
- `gfx/layers/ipc/PUiCompositorController.ipdl`
- `gfx/layers/ipc/UiCompositorControllerChild.cpp`
- `gfx/layers/ipc/UiCompositorControllerChild.h`
- `gfx/layers/ipc/UiCompositorControllerMessageTypes.h`
- `gfx/layers/ipc/UiCompositorControllerParent.cpp`
- `gfx/layers/ipc/UiCompositorControllerParent.h`

The commit also modified shared GPU, compositor, APZ, WebRender, networking and widget interfaces to remove dependencies on these implementations.

Shared graphics infrastructure and Linux desktop functionality were retained. This does not establish that all Android-specific compositor or graphics references have been removed.

### 10.8 Touch resampling and Android VSync

The Android touch-resampling implementation has been removed after confirming that its only production consumer was `widget/android/nsWindow.cpp`.

Removed:

- `widget/TouchResampler.cpp`
- `widget/TouchResampler.h`
- `widget/tests/gtest/TestTouchResampler.cpp`
- The `TouchResampler.cpp` registration in `widget/moz.build`.
- The `TestTouchResampler.cpp` registration in `widget/tests/gtest/moz.build`.
- The `android.touch_resampling.enabled` preference in `modules/libpref/init/StaticPrefList.yaml`.
- The resampler integration in `widget/android/nsWindow.cpp`, including its pending-result queue, observer, resampling state and event-draining path.

Normal Android motion events now use the direct event-handling path. This preserves ordinary input handling without the removed resampling layer.

`AndroidVsync` has deliberately been retained. Its remaining consumers include:

- `gfx/thebes/gfxAndroidPlatform.cpp`, which uses the Android VSync implementation for the graphics platform's render VSync source.
- `widget/android/ScreenHelperAndroid.cpp`, which uses it when screen refresh-rate information changes.

These consumers belong to the remaining Android graphics and widget platform implementation. `AndroidVsync` should be reconsidered during the coordinated removal of those Android-specific components, not removed independently while they still depend on it.

The TouchResampler removal passed the targeted source search and `git diff --check` in the local working tree. No build or test execution is claimed.

### 10.9 Other platform code retained pending review

The following were deliberately not removed wholesale:

- Shared Places history and database APIs.
- Shared viewport and keyboard APIs.
- Shared HAL interfaces and Linux fallback implementations.
- Shared VR and OOP compositing abstractions.
- Shared print settings interfaces and non-Android implementations.
- Shared file-picker APIs.
- Shared accessibility interfaces.
- Shared GTK/Linux code paths.
- Generic Android cross-compilation/configuration branches whose remaining consumers have not been fully scoped.
- UIKit code and its GeckoView-named support files; these are iOS-specific and were not assumed to be Android code.
- `ScrollbarDrawingAndroid` because it remains used by shared code paths.

Windows and macOS product builds are outside Foxtrot's supported scope. Their shared source code should nevertheless only be removed where it is demonstrably unnecessary and does not break retained Mozilla infrastructure.

### 10.10 Thunderbird application removal

Foxtrot is a Firefox-based Linux desktop browser. Thunderbird is not a supported
application target. Thunderbird-specific application selection, configuration
branches and test exclusions have therefore been removed where they were no
longer required by the Firefox desktop build.

The removal was committed in two stages.

#### Mochitest application support — `cd01d06b84`

- Restricted supported Mochitest applications to Firefox.
- Removed dedicated Android and GeckoView JUnit runners, their command
  registration and dispatch logic.
- Removed Thunderbird-specific browser-test handling.
- Retained shared desktop Mochitest infrastructure.

#### Thunderbird application-specific code — `4e270fde41`

**FxAccounts**

- Removed `CLIENT_IS_THUNDERBIRD`.
- Removed Thunderbird's OAuth client ID and Thunderbird Sync scope.
- Made Firefox's OAuth client ID and Sync scope unconditional.
- Removed Thunderbird-specific branches from FxAccounts commands and tests.
- Removed Thunderbird-only test exclusions from
  `services/fxaccounts/tests/xpcshell/xpcshell.toml`.

**Sync**

- Made Firefox Sync engine registration unconditional.
- Removed Thunderbird application selection from Sync module loading and
  startup tests.
- Retained Firefox bookmarks, forms, history and tabs Sync functionality.

**Remote Settings**

- Made the Firefox Remote Settings server URL unconditional.
- Enabled signature verification unconditionally.
- Made the default Remote Settings bucket `main`.

**Build configuration and application handling**

- Removed Thunderbird from the Windows notification-server default condition
  in `build/moz.configure/update-programs.configure`.
- Removed Thunderbird-specific handling from toolkit build configuration,
  application constants, localisation, content and extension build selection.
- Removed Thunderbird-specific startup and profile-directory handling from
  `toolkit/xre/nsXREDirProvider.cpp`.
- Restricted the relevant Debian packaging and Remote Settings dump handling
  to the Firefox browser application.

**Extensions and other shared components**

- Removed Thunderbird-specific content-process selection logic from the
  extension implementation.
- Removed Thunderbird-specific message-manager group handling from
  `toolkit/components/extensions/ExtensionPolicyService.cpp`.
- Removed Thunderbird-specific crash-handling and platform-specific branches
  where they were no longer applicable.

#### Retained functionality

The removal does not mean that all Mozilla code shared with Thunderbird
should be deleted.

Shared Gecko, networking, account, extension, security, Remote Settings and
Sync infrastructure remains where required by Firefox. Firefox account and
Sync functionality remain; the changes remove Thunderbird-specific application
selection and behaviour.

#### Validation status

The committed source changes were inspected. Targeted searches in
`services/fxaccounts/` found no remaining `CLIENT_IS_THUNDERBIRD` references,
Thunderbird OAuth client ID or Thunderbird Sync scope. Thunderbird-specific
test exclusions were removed from the FxAccounts test manifest.

This does not establish that every Thunderbird reference has been removed from
the entire repository. Remaining matches must be assessed individually,
distinguishing obsolete application code from shared Mozilla infrastructure,
historical comments, documentation and unrelated test data.

The latest commit also contains Android cleanup. Its entire changed-file list
must not be attributed to Thunderbird removal.

No successful full Linux build or complete test-suite execution is claimed
for these changes.

## 11. Remaining work

The following work remains outstanding:

1. Complete the repository-wide `mobile/` reference audit.
2. Complete the separate `widget/android/` dependency audit.
3. Review and remove the remaining Android dynamic-toolbar IPC and cached-state paths, preserving shared desktop compositor and viewport functionality.
4. Remove remaining Android Java PiP and keyboard callbacks as part of the mobile-product cleanup, then regenerate and verify generated bindings.
5. Continue auditing Android-specific compositor messages, screen-pixel paths and cached state after removal of the UI compositor controller.
6. Review remaining Android build configuration, test infrastructure and platform-specific references after the NDK, audio and performance cleanup.
7. Audit `hal/android/` and its remaining consumers.
8. Review remaining Android accessibility references after deletion of `accessible/android/`.
9. Complete clean Linux x86_64 and ARM64 builds.
10. Run relevant test suites and packaging checks.
11. Review the complete cumulative source changes before declaring the platform cleanup complete.
12. Complete a repository-wide Thunderbird reference audit. Inspect remaining
    `thunderbird`, `MOZ_THUNDERBIRD`, `comm/mail` and application-name matches.
    Remove obsolete Thunderbird-specific code while retaining genuinely shared
    Gecko infrastructure and unrelated historical references where appropriate.


## 12. Validation and security claims

The original cleanup recorded a clean `git diff --check` result at the time of its working-tree inspection. That historical result is not a validation of all subsequent commits or the current working tree.

The commits recorded by this audit represent source-level changes. They do not establish successful compilation, linking, packaging or runtime operation.

Local Raptor and Talos performance-testing infrastructure was improved in commit `707aafab05`. This work does not establish that Foxtrot itself has been built or benchmarked successfully.

No successful full Linux x86_64 build, Linux ARM64 build, complete test suite or package build is claimed here.

This audit does not claim that ESR153 security patches have been migrated to the ESR140.16.0 baseline. Any such migration must be assessed individually against the actual source changes and Foxtrot product requirements. No security fix should be considered migrated without source-level evidence.

## 13. Historical changed-file inventory

The following paths record the tracked-file changes reviewed during the original cleanup committed in `821e313534`.

This is a historical inventory, not a list of all files changed by subsequent commits and not a description of the current working tree.

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

This historical list does not include the files changed by the subsequent commits documented in section 10.7. It does not imply that every line in every file has been independently reviewed against a complete build.
