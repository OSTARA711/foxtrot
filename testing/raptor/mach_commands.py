# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# File: testing/raptor/mach_commands.py
# Originally taken from /talos/mach_commands.py

# Integrates raptor mozharness with mach

import json
import logging
import os
import socket
import subprocess
import sys

from mach.decorators import Command
from mach.util import get_state_dir
from mozbuild.base import BinaryNotFoundException, MozbuildObject
from mozbuild.base import MachCommandConditions as Conditions

HERE = os.path.dirname(os.path.realpath(__file__))

# Fenix is deliberately excluded. GeckoView and Reference Browser remain
# separate Android targets pending their own platform-scope assessment.
ANDROID_BROWSERS = ["geckoview", "refbrow", "chrome-m", "cstm-car-m"]


class RaptorRunner(MozbuildObject):
    def run_test(self, raptor_args, kwargs):
        """Set up and run mozharness."""
        # Validate the supported Python version before doing anything else.
        max_python = (3, 13)
        current_python = sys.version_info[:2]

        if current_python > max_python:
            message = (
                f"\tRaptor does not yet support Python versions greater than "
                f"{max_python[0]}.{max_python[1]}."
                f"\n\tYou are currently using Python "
                f"{current_python[0]}.{current_python[1]}."
                "\n\tSee the following documentation for help debugging "
                "your Python environment: "
                "https://firefox-source-docs.mozilla.org/testing/perfdocs/"
                "debugging.html#debugging-local-python-environment"
            )
            raise PythonVersionException(message)

        self.init_variables(raptor_args, kwargs)
        self.make_config()
        self.write_config()
        self.make_args()
        return self.run_mozharness()

    def init_variables(self, raptor_args, kwargs):
        self.raptor_args = raptor_args

        if kwargs.get("host") == "HOST_IP":
            kwargs["host"] = os.environ["HOST_IP"]

        self.host = kwargs["host"]
        self.is_release_build = kwargs["is_release_build"]
        self.live_sites = kwargs["live_sites"]
        self.disable_perf_tuning = kwargs["disable_perf_tuning"]
        self.conditioned_profile = kwargs["conditioned_profile"]
        self.device_name = kwargs["device_name"]
        self.enable_marionette_trace = kwargs["enable_marionette_trace"]
        self.browsertime_visualmetrics = kwargs["browsertime_visualmetrics"]
        self.browsertime_node = kwargs["browsertime_node"]
        self.clean = kwargs["clean"]
        self.screenshot_on_failure = kwargs["screenshot_on_failure"]

        if Conditions.is_android(self) or kwargs["app"] in ANDROID_BROWSERS:
            self.binary_path = None
        else:
            self.binary_path = kwargs.get("binary") or self.get_binary_path()

        self.python = sys.executable

        self.raptor_dir = os.path.join(self.topsrcdir, "testing", "raptor")
        self.mozharness_dir = os.path.join(self.topsrcdir, "testing", "mozharness")
        self.config_file_path = os.path.join(
            self._topobjdir, "testing", "raptor-in_tree_conf.json"
        )

        self.virtualenv_script = os.path.join(
            self.topsrcdir, "third_party", "python", "virtualenv", "virtualenv.py"
        )
        self.virtualenv_path = os.path.join(self._topobjdir, "testing", "raptor-venv")

    def make_config(self):
        default_actions = [
            "populate-webroot",
            "create-virtualenv",
            "install-chromium-distribution",
            "run-tests",
        ]

        self.config = {
            "run_local": True,
            "binary_path": self.binary_path,
            "repo_path": self.topsrcdir,
            "raptor_path": self.raptor_dir,
            "obj_path": self.topobjdir,
            "log_name": "raptor",
            "virtualenv_path": self.virtualenv_path,
            "pypi_url": "http://pypi.org/simple",
            "base_work_dir": self.mozharness_dir,
            "exes": {
                "python": self.python,
                "virtualenv": [self.python, self.virtualenv_script],
            },
            "title": socket.gethostname(),
            "default_actions": default_actions,
            "raptor_cmd_line_args": self.raptor_args,
            "host": self.host,
            "live_sites": self.live_sites,
            "disable_perf_tuning": self.disable_perf_tuning,
            "conditioned_profile": self.conditioned_profile,
            "is_release_build": self.is_release_build,
            "device_name": self.device_name,
            "enable_marionette_trace": self.enable_marionette_trace,
            "browsertime_visualmetrics": self.browsertime_visualmetrics,
            "browsertime_node": self.browsertime_node,
            "mozbuild_path": get_state_dir(),
            "clean": self.clean,
            "screenshot_on_failure": self.screenshot_on_failure,
        }

        original_sys_path = sys.path[:]
        sys.path.insert(0, os.path.join(self.topsrcdir, "tools", "browsertime"))

        try:
            import platform

            import mach_commands as browsertime

            # Chromedriver and geckodriver are found by Browsertime in its
            # node_modules directory. FFmpeg must currently be available
            # through PATH.
            self.config.update(
                {
                    "browsertime_browsertimejs": browsertime.browsertime_path(),
                    "browsertime_vismet_script": browsertime.visualmetrics_path(),
                }
            )

            def _get_browsertime_package():
                package_path = os.path.join(
                    self.topsrcdir,
                    "tools",
                    "browsertime",
                    "node_modules",
                    "browsertime",
                    "package.json",
                )
                with open(package_path) as package:
                    return json.load(package)

            def _get_browsertime_resolved():
                lock_path = os.path.join(
                    self.topsrcdir,
                    "tools",
                    "browsertime",
                    "node_modules",
                    ".package-lock.json",
                )
                try:
                    with open(lock_path) as package_lock:
                        return json.load(package_lock)["packages"][
                            "node_modules/browsertime"
                        ]["resolved"]
                except FileNotFoundError:
                    # Older Node/npm versions store this metadata in package.json.
                    return _get_browsertime_package()["_from"]

            def _should_install():
                # Install if FFmpeg is missing from the Browsertime cache.
                btime_cache = os.path.join(
                    self.config["mozbuild_path"], "browsertime"
                )
                if not os.path.exists(btime_cache) or not any(
                    "ffmpeg" in cache_dir for cache_dir in os.listdir(btime_cache)
                ):
                    return True

                # Install if the Browsertime scripts are missing.
                if not os.path.exists(
                    self.config["browsertime_browsertimejs"]
                ) or not os.path.exists(self.config["browsertime_vismet_script"]):
                    return True

                # Check whether the installed Browsertime version is outdated.
                package_path = os.path.join(
                    self.topsrcdir, "tools", "browsertime", "package.json"
                )
                with open(package_path) as new:
                    new_pkg = json.load(new)

                return not _get_browsertime_resolved().endswith(
                    new_pkg["devDependencies"]["browsertime"]
                )

            def _get_browsertime_version():
                return (
                    _get_browsertime_package()["version"],
                    _get_browsertime_resolved(),
                )

            if _should_install():
                print("Missing browsertime files...attempting to install")

                subprocess.check_output(
                    [
                        os.path.join(self.topsrcdir, "mach"),
                        "browsertime",
                        "--setup",
                        "--clobber",
                    ],
                    shell="windows" in platform.system().lower(),
                )

                if _should_install():
                    raise Exception(
                        "Failed installation attempt. Cannot find browsertime "
                        "scripts. Run `./mach browsertime --setup --clobber` "
                        "to set it up."
                    )

                # Bug 1766112: rebuild the Python environment when upgrading
                # Browsertime.
                print(
                    "Setting --clean to True to rebuild Python "
                    "environment for Browsertime upgrade..."
                )
                self.config["clean"] = True

            print(
                "Using browsertime version %s from %s"
                % _get_browsertime_version()
            )

        finally:
            sys.path[:] = original_sys_path

    def make_args(self):
        self.args = {
            "config": {},
            "initial_config_file": self.config_file_path,
        }

    def write_config(self):
        try:
            config_dir = os.path.dirname(self.config_file_path)
            os.makedirs(config_dir, exist_ok=True)

            with open(self.config_file_path, "w") as config_file:
                json.dump(self.config, config_file)

        except OSError as e:
            err_str = "Error writing Raptor Mozharness config file {0}:{1}"
            print(err_str.format(self.config_file_path, str(e)))
            raise

    def run_mozharness(self):
        sys.path.insert(0, self.mozharness_dir)
        from mozharness.mozilla.testing.raptor import Raptor

        raptor_mh = Raptor(
            config=self.args["config"],
            initial_config_file=self.args["initial_config_file"],
        )
        return raptor_mh.run()


def setup_node(command_context):
    """Find Node.js or download Node 22 into the .mozbuild directory."""
    import platform

    from mozbuild.nodeutil import find_node_executable
    from packaging.version import Version

    print("Setting up node for browsertime...")

    state_dir = get_state_dir()
    cache_path = os.path.join(state_dir, "browsertime", "node-22")

    def __check_for_node():
        # Check standard locations first, including the Mozilla toolchain.
        node_exe = find_node_executable(min_version=Version("22.0.0"))
        if node_exe and node_exe[0] is not None:
            return node_exe[0]

        if not os.path.exists(cache_path):
            return None

        # Check the Browsertime-specific Node.js cache.
        node_name = "node"
        if platform.system() == "Windows":
            node_name = "node.exe"
            node_exe_path = os.path.join(cache_path, "node")
        else:
            node_exe_path = os.path.join(cache_path, "node", "bin")

        node_exe = os.path.join(node_exe_path, node_name)
        if not os.path.exists(node_exe):
            return None

        return node_exe

    node_exe = __check_for_node()

    if node_exe is None:
        # Taskcluster artifact tooling is needed only when Node.js must be
        # downloaded. This avoids importing Taskcluster dependencies when
        # a suitable local Node.js installation is already available.
        from mozbuild.artifact_commands import artifact_toolchain

        toolchain_job = "{}-node-22"
        plat = platform.system()

        if plat == "Windows":
            toolchain_job = toolchain_job.format("win64")
        elif plat == "Darwin":
            if platform.processor() == "arm":
                toolchain_job = toolchain_job.format("macosx64-aarch64")
            else:
                toolchain_job = toolchain_job.format("macosx64")
        else:
            toolchain_job = toolchain_job.format("linux64")

        print(
            f"Downloading Node 22 from Taskcluster toolchain {toolchain_job}..."
        )

        os.makedirs(cache_path, exist_ok=True)

        # Install into the Node.js cache rather than the repository root.
        original_dir = os.getcwd()
        try:
            os.chdir(cache_path)
            artifact_toolchain(
                command_context,
                verbose=False,
                from_build=[toolchain_job],
                no_unpack=False,
                retry=0,
                cache_dir=cache_path,
            )
        finally:
            os.chdir(original_dir)

        node_exe = __check_for_node()
        if node_exe is None:
            raise Exception(
                "Could not find Node v22 binary for Raptor-Browsertime"
            )

        print("Finished downloading Node v22 from Taskcluster")

    print("Node v22+ found at: %s" % node_exe)
    return node_exe


def create_parser():
    sys.path.insert(0, HERE)  # Allow importing the Raptor package.
    from raptor.cmdline import create_parser

    return create_parser(mach_interface=True)


@Command(
    "raptor",
    category="testing",
    description="Run Raptor performance tests.",
    parser=create_parser,
)
def run_raptor(command_context, **kwargs):
    build_obj = command_context

    if kwargs.get("app") == "fenix":
        command_context.log(
            logging.ERROR,
            "raptor",
            {"error": "Fenix support has been removed from Foxtrot."},
            "ERROR: {error}",
        )
        return 1

    # Set up Node.js for Browsertime.
    kwargs["browsertime_node"] = setup_node(command_context)

    is_android = (
        Conditions.is_android(build_obj) or kwargs["app"] in ANDROID_BROWSERS
    )

    if is_android:
        from mozrunner.devices.android_device import (
            InstallIntent,
            verify_android_device,
        )

        install = (
            InstallIntent.NO if kwargs.pop("no_install", False) else InstallIntent.YES
        )
        verbose = False

        if (
            kwargs.get("log_mach_verbose")
            or kwargs.get("log_tbpl_level") == "debug"
            or kwargs.get("log_mach_level") == "debug"
            or kwargs.get("log_raw_level") == "debug"
        ):
            verbose = True

        if not verify_android_device(
            build_obj,
            install=install,
            app=kwargs["binary"],
            verbose=verbose,
            xre=True,
        ):
            print(
                "****************************************************************************"
            )
            print(
                "Unable to verify device, please check your attached/connected android device"
            )
            print(
                "****************************************************************************"
            )
            return 1

        # Disable fission until GeckoView supports fission by default.
        # Enable it explicitly with '--setpref fission.autostart=true'.
        kwargs["fission"] = False

    # Remove mach global arguments from sys.argv before passing arguments
    # to Raptor. Arguments before the "raptor" command belong to mach.
    argv = []
    in_mach = True

    for arg in sys.argv:
        if not in_mach:
            argv.append(arg)
        if arg.startswith("raptor"):
            in_mach = False

    raptor = command_context._spawn(RaptorRunner)

    try:
        return raptor.run_test(argv, kwargs)

    except BinaryNotFoundException as e:
        command_context.log(
            logging.ERROR, "raptor", {"error": str(e)}, "ERROR: {error}"
        )
        command_context.log(
            logging.INFO, "raptor", {"help": e.help()}, "{help}"
        )
        return 1

    except Exception as e:
        print(repr(e))
        return 1


@Command(
    "raptor-test",
    category="testing",
    description="Run Raptor performance tests.",
    parser=create_parser,
)
def run_raptor_test(command_context, **kwargs):
    return run_raptor(command_context, **kwargs)


class PythonVersionException(Exception):
    pass
