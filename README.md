# Foxtrot

**Linux-focused, English-US browser built from Mozilla Firefox ESR.**

<p align="center">
  <img src="browser/branding/foxtrot/content/foxtrot.svg"
       alt="Foxtrot"
       width="500">
</p>

Foxtrot is an independently maintained Gecko browser for Linux desktops, built around security, user control, predictable behaviour and freedom from unwanted AI integration.

The project retains Mozilla's Gecko engine and the upstream browser infrastructure required for a functional desktop browser, while maintaining its own branding, Debian packaging configuration and carefully selected product-level changes.

> **Development status:** Foxtrot is under active development. Its source tree and packaging configuration are being adapted for the intended Linux desktop distribution. Not every planned product change, security improvement or distribution service should be considered implemented.

## Project objectives

Foxtrot is developed according to five priorities:

1. **Secure defaults** — choose browser defaults that reduce unnecessary exposure without compromising ordinary desktop use.
2. **Remote-interface isolation** — prevent debugging, automation and other remote interfaces from being exposed to untrusted networks by default.
3. **Extension and credential protection** — make browser privileges, extension permissions and credential handling understandable and appropriately restricted.
4. **Stability** — favour predictable behaviour, upstream-compatible changes and dependable desktop integration.
5. **Carefully selected features** — add functionality only where its benefits justify its maintenance and security costs.

Foxtrot is not intended to accumulate features for their own sake. Every proposed feature must justify its maintenance cost, security implications and impact on future upstream rebasing.

## Supported platforms

The intended Foxtrot product is a Linux desktop browser.

| Area | Supported scope |
|---|---|
| Operating system | Linux desktop |
| CPU architectures | AMD64 / x86_64 and ARM64 / aarch64 |
| Browser engine | Mozilla Gecko |
| Upstream foundation | Firefox Extended Support Release (ESR) |
| Interface language | English-US (`en-US`) |
| Distribution format | Debian packages |
| Packaging direction | Independent APT repository |

Other operating systems, mobile products and unsupported CPU architectures are outside the intended product scope.

Shared Mozilla source code is not removed merely because it also supports another platform. Components required by Linux desktop functionality, shared browser infrastructure or compatibility interfaces must be retained where necessary.

## Product scope

Foxtrot concentrates on the Linux desktop browsing experience.

The intended product excludes:

- Android, iOS and other mobile browser products and mobile-specific interfaces.
- Visual Studio Code integration.
- Non-English browser interface translations and language packs.
- Integrated AI features and AI-specific runtime components.
- Browser page-translation functionality and its translation models or runtime dependencies.
- Snap and Flatpak packaging.

These exclusions apply to product functionality and separable platform-specific infrastructure. They do not justify indiscriminate removal of shared Mozilla code that remains necessary for the desktop browser.

## Security priorities

Security is a development and testing priority. The following areas guide implementation and review; their inclusion here does not imply that every objective has already been completed.

### Credential protection

Foxtrot aims to make browser-controlled password prompts unmistakable and maintain clear boundaries between web content and privileged browser interfaces.

Development and review should cover:

- Credential storage and protection.
- Password prompts and autofill behaviour.
- Extension access to credentials and related browser interfaces.
- Separation between untrusted web content and privileged browser functionality.

### Extension containment

Extensions can introduce significant privileges. Foxtrot prioritises clear permission visibility and containment.

Development and review should cover:

- Understandable permission requests.
- Site-specific access controls where supported.
- The distinction between trusted browser components and third-party extensions.
- Unnecessary extension privileges and access to sensitive browser data.

### Secure connection defaults

HTTPS-Only Mode is a priority for evaluation as a default browser setting.

Testing must cover:

- Automatic HTTPS upgrades.
- Fallback behaviour for websites that do not support HTTPS.
- Local network services and development environments.
- Compatibility and usability when secure connections cannot be established.

HTTPS-Only Mode must not be described as enabled by default until the Foxtrot configuration and corresponding tests establish that behaviour.

### Remote-interface isolation

Debugging and automation interfaces must not become unintended network entry points.

Development and review should cover:

- Default network binding and exposure.
- Authentication and access controls where supported.
- Deliberate configuration before remote access is enabled.
- Preservation of useful local desktop development and debugging capabilities.

Removing mobile-specific functionality must not result in the unnecessary removal of shared Linux desktop debugging infrastructure.

### Stability and maintainability

Security improvements must remain maintainable across upstream ESR updates.

Foxtrot favours:

- Small, independently reviewable changes.
- Upstream-supported solutions where practical.
- Changes that are straightforward to test and revert.
- Avoidance of unnecessary background services and runtime dependencies.
- Attention to memory consumption and resource usage.
- Testing across both supported CPU architectures.

Foxtrot does not claim to be inherently more secure than Mozilla Firefox. Its security objectives must be demonstrated through implementation, configuration, testing and maintenance.

## Upstream foundation

Foxtrot originated from **Mozilla Firefox ESR 140.16.0**.

The source tree was subsequently rebased onto **Firefox ESR 153.7.0**, whenever deem fit, as recorded in the Debian packaging changelog. The project continues to follow the Firefox ESR source and security-maintenance lineage while maintaining its own product decisions and distribution configuration.

Foxtrot retains the upstream browser engine and the shared Mozilla infrastructure required for desktop browsing, including networking, rendering, JavaScript, accessibility, developer tools and supporting components.

Upstream changes are evaluated with regard to desktop compatibility, security, maintainability and the cost of future ESR rebases.

Useful upstream references:

- [Mozilla Firefox](https://www.mozilla.org/firefox/)
- [Firefox Source Documentation](https://firefox-source-docs.mozilla.org/)
- [Mozilla Security Advisories](https://www.mozilla.org/security/advisories/)

## Repository structure

The repository contains the Firefox source tree and Foxtrot's Debian packaging.

| Directory | Purpose |
|---|---|
| `browser/` | Browser application, interface and branding |
| `debian/` | Debian packaging, build rules, patches and configuration |
| `devtools/` | Developer tools |
| `dom/` | Document Object Model and web platform implementation |
| `gfx/` | Graphics and rendering |
| `intl/` | Internationalisation infrastructure |
| `js/` | JavaScript engine |
| `netwerk/` | Networking components |
| `security/` | Browser security components |
| `testing/` | Automated tests and test infrastructure |
| `third_party/` | Vendored third-party dependencies |
| `toolkit/` | Shared browser application infrastructure |

Other directories contain additional Mozilla platform components, libraries, build infrastructure and supporting source code.

## Building

Foxtrot uses the Mozilla build system and Debian packaging infrastructure.

The Debian packaging configuration is maintained in `debian/`, including:

- `debian/control` — package build and runtime dependencies.
- `debian/rules` — Debian build instructions.
- `debian/browser.mozconfig.in` — browser build configuration.
- `debian/patches/` — Debian-specific patches.
- `debian/vendor.js` — distribution-specific browser preferences.

Build requirements depend on the target Debian release and architecture. Consult the [Firefox build documentation](https://firefox-source-docs.mozilla.org/setup/) before preparing a build environment.

A Debian package build can be initiated with:

```bash
dpkg-buildpackage -b -uc -us
```

This assumes that the required build dependencies have been installed and that the source tree is correctly prepared.

Build instructions and supported configurations may evolve during development. A successful build alone does not establish that all Foxtrot product objectives have been implemented or tested.

## Localisation

Foxtrot is intended to ship with the English-US (`en-US`) browser interface.

Non-English interface translations and language packs are outside the intended product scope. Shared localisation infrastructure may remain where required by the Mozilla build system or other retained desktop components.

The spell-checking engine is retained. Dictionaries are provided separately by the operating system when installed.

## Updates and security maintenance

Foxtrot disables the browser's built-in application updater in its Debian build configuration.

The intended distribution model is to deliver browser updates through Debian packages and an independently maintained APT repository.

This requires ongoing maintenance:

- Track relevant Firefox ESR security releases.
- Review upstream changes and Debian packaging updates.
- Rebuild and test packages for supported architectures.
- Distribute security updates promptly.
- Verify that Foxtrot-specific changes remain compatible with upstream updates.

Disabling the browser updater does not itself provide an update mechanism or make an installation secure. Users and distributors must obtain and install maintained Foxtrot packages.

See [SECURITY.md](SECURITY.md) for security reporting information.

## Licensing

Foxtrot is based on Mozilla Firefox and includes software distributed under multiple open-source licences.

The Mozilla Public License 2.0 (MPL-2.0) applies to substantial portions of the source tree. Other components retain their respective upstream licences.

Consult the repository's `LICENSE` and `debian/copyright` files for licensing information.

Mozilla trademarks and branding remain subject to their respective owners' terms. Foxtrot branding does not imply endorsement by Mozilla.

## Contributing

Development takes place in this repository:

[https://github.com/OSTARA711/foxtrot](https://github.com/OSTARA711/foxtrot)

Issues, bug reports and development discussions can be submitted through the repository's GitHub issue tracker.

Contributions should:

- Preserve applicable upstream copyright notices and licence information.
- Respect Foxtrot's Linux desktop product scope.
- Avoid unnecessary divergence from upstream Mozilla code.
- Include appropriate tests for behavioural changes.
- Consider security, resource usage and future ESR maintenance.

---

**Foxtrot**  
An independently maintained Gecko browser for Linux desktops.
