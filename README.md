# Foxtrot

**A Linux-focused, English-US browser built from Mozilla Firefox ESR.**

Foxtrot is a customised Firefox Extended Support Release (ESR) source tree, maintained with a focus on Linux desktop systems, English-US localisation, and Debian-based distribution.

The project retains Mozilla's browser engine and upstream source code while introducing its own branding and a streamlined Debian packaging configuration.

> **Development status:** Foxtrot is currently a source-code project. Binary packages and installation instructions will be published when a build has been completed and tested.

## Project objectives

- **Linux desktop focus** — prioritise Linux desktop integration and Debian-based distribution.
- **English-US interface** — ship the browser with the `en-US` locale.
- **Independent branding** — use Foxtrot branding for ESR, Beta, and Release builds.
- **Debian packaging** — maintain Debian build rules and package integration.
- **System integration** — use available system libraries where supported by the build configuration.
- **Controlled updates** — disable the browser's built-in application updater; software updates are intended to be handled through the distribution's package management.
- **Optional spell-checking dictionaries** — retain Hunspell integration without requiring an English-US dictionary to be bundled with the browser.

## Upstream

Foxtrot is based on Mozilla Firefox ESR.

The current source version is **140.16.0**.

Foxtrot retains the upstream Mozilla source tree, including the browser engine, networking, security, rendering, JavaScript, accessibility, developer tools, and supporting components.

- [Mozilla Firefox](https://www.mozilla.org/firefox/)
- [Firefox Source Documentation](https://firefox-source-docs.mozilla.org/)
- [Mozilla Security Advisories](https://www.mozilla.org/security/advisories/)

## Repository structure

The repository contains the Firefox source tree and Debian packaging.

| Directory | Purpose |
|---|---|
| `browser/` | Browser application, interface, and branding |
| `debian/` | Debian packaging, build rules, patches, and package configuration |
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

Other directories contain additional Mozilla platform components, libraries, build infrastructure, and supporting source code.

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

This command assumes that the required build dependencies have already been installed and that the source tree is correctly prepared.

Build instructions and supported configurations may evolve during development.

## Localisation

The browser is configured to ship with the English-US (`en-US`) locale.

The upstream localisation infrastructure and source directories remain in the repository. Their presence does not mean that translated browser interfaces or language packs are included in the intended Foxtrot build.

The spell-checking engine is retained. Dictionaries are provided separately by the operating system when installed.

## Updates and security

The built-in application updater is disabled in the Debian build configuration.

The intended distribution model is to deliver browser updates through Debian packages rather than through the browser's own application updater.

Security fixes and upstream ESR updates remain essential. A customised browser must not be considered secure merely because its updater has been disabled.

Users and distributors should follow Mozilla security advisories and ensure that Foxtrot packages are rebuilt and distributed with relevant security updates.

See [SECURITY.md](SECURITY.md) for security reporting information.

## Licensing

Foxtrot is based on Mozilla Firefox and includes software distributed under multiple open-source licences.

The Mozilla Public License 2.0 (MPL-2.0) applies to substantial portions of the source tree. Other components retain their respective upstream licences.

Consult the repository's `LICENSE` and `debian/copyright` files for licensing information.

Mozilla trademarks and branding remain subject to their respective owners' terms. Foxtrot branding does not imply endorsement by Mozilla.

## Contributing

Development takes place in this repository:

[https://github.com/OSTARA711/foxtrot](https://github.com/OSTARA711/foxtrot)

Issues, bug reports, and development discussions can be submitted through the repository's GitHub issue tracker.

Contributions should preserve applicable upstream copyright notices and licence information.

---

**Foxtrot**  
Linux-focused Firefox ESR development.
