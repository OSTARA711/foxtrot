# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# An easy way for distribution-specific bootstrappers to share the code
# needed to install Stylo and Node dependencies.  This class must come before
# BaseBootstrapper in the inheritance list.

import platform


def is_non_x86_64():
    return platform.machine() != "x86_64"


class LinuxBootstrapper:
    def __init__(self, **kwargs):
        pass

    def ensure_sccache_packages(self):
        pass

    def install_system_packages(self):
        self.install_packages(
            [
                "bash",
                "findutils",  # contains xargs
                "gzip",
                "libxml2",  # used by bootstrapped clang
                "make",
                "perl",
                "tar",
                "unzip",
            ]
        )
        # Optional packages
        try:
            self.install_packages(["watchman"])
        except Exception:
            pass

    def install_browser_packages(self, mozconfig_builder, artifact_mode=False):
        pass

    def install_browser_artifact_mode_packages(self, mozconfig_builder):
        pass
