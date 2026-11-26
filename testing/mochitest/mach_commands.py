# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import functools
import logging
import os
import sys
import warnings
from argparse import Namespace
from collections import defaultdict

from mach.decorators import Command
from mozbuild.base import MachCommandConditions as conditions
from mozbuild.base import MozbuildObject
from mozfile import load_source

here = os.path.abspath(os.path.dirname(__file__))


ENG_BUILD_REQUIRED = """
The mochitest command requires an engineering build. It may be the case that
VARIANT=user or PRODUCTION=1 were set. Try re-building with VARIANT=eng:

    $ VARIANT=eng ./build.sh

There should be an app called 'test-container.gaiamobile.org' located in
{}.
""".lstrip()

SUPPORTED_TESTS_NOT_FOUND = """
The mochitest command could not find any supported tests to run! The
following flavors and subsuites were found, but are either not supported on
{} builds, or were excluded on the command line:

{}

Double check the command line you used, and make sure you are running in
context of the proper build. To switch build contexts, either run |mach|
from the appropriate objdir, or export the correct mozconfig:

    $ export MOZCONFIG=path/to/mozconfig
""".lstrip()

TESTS_NOT_FOUND = """
The mochitest command could not find any mochitests under the following
test path(s):

{}

Please check spelling and make sure there are mochitests living there.
""".lstrip()

SUPPORTED_APPS = ["firefox"]

parser = None


class MochitestRunner(MozbuildObject):
    """Easily run mochitests.

    This currently contains just the basics for running mochitests. We may want
    to hook up result parsing, etc.
    """

    def __init__(self, *args, **kwargs):
        MozbuildObject.__init__(self, *args, **kwargs)

        # TODO Bug 794506 remove once mach integrates with virtualenv.
        build_path = os.path.join(self.topobjdir, "build")
        if build_path not in sys.path:
            sys.path.append(build_path)

        self.tests_dir = os.path.join(self.topobjdir, "_tests")
        self.mochitest_dir = os.path.join(self.tests_dir, "testing", "mochitest")
        self.bin_dir = os.path.join(self.topobjdir, "dist", "bin")

    def resolve_tests(self, test_paths, test_objects=None, cwd=None):
        if test_objects:
            return test_objects

        from moztest.resolve import TestResolver

        resolver = self._spawn(TestResolver)
        tests = list(resolver.resolve_tests(paths=test_paths, cwd=cwd))
        return tests

    def run_desktop_test(self, command_context, tests=None, **kwargs):
        """Runs a mochitest."""
        # runtests.py is ambiguous, so we load the file/module manually.
        if "mochitest" not in sys.modules:
            path = os.path.join(self.mochitest_dir, "runtests.py")
            load_source("mochitest", path)

        import mochitest

        # This is required to make other components happy. Sad, isn't it?
        os.chdir(self.topobjdir)

        # Automation installs its own stream handler to stdout. Since we want
        # all logging to go through us, we just remove their handler.
        remove_handlers = [
            l
            for l in logging.getLogger().handlers
            if isinstance(l, logging.StreamHandler)
        ]
        for handler in remove_handlers:
            logging.getLogger().removeHandler(handler)

        options = Namespace(**kwargs)
        options.topsrcdir = self.topsrcdir
        options.topobjdir = self.topobjdir

        from manifestparser import TestManifest

        if tests and not options.manifestFile:
            manifest = TestManifest()
            manifest.tests.extend(tests)
            options.manifestFile = manifest

            # When developing mochitest-plain tests, it's often useful to be able to
            # refresh the page to pick up modifications. Therefore leave the browser
            # open if only running a single mochitest-plain test. This behaviour can
            # be overridden by passing in --keep-open=false.
            if (
                len(tests) == 1
                and options.keep_open is None
                and not options.headless
                and getattr(options, "flavor", "plain") == "plain"
            ):
                options.keep_open = True

        # We need this to enable colorization of output.
        self.log_manager.enable_unstructured()
        result = mochitest.run_test_harness(parser, options)
        self.log_manager.disable_unstructured()
        return result



# parser


def setup_argument_parser():
    build_obj = MozbuildObject.from_environment(cwd=here)

    build_path = os.path.join(build_obj.topobjdir, "build")
    if build_path not in sys.path:
        sys.path.append(build_path)

    mochitest_dir = os.path.join(build_obj.topobjdir, "_tests", "testing", "mochitest")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        path = os.path.join(build_obj.topobjdir, mochitest_dir, "runtests.py")
        if not os.path.exists(path):
            path = os.path.join(here, "runtests.py")

        load_source("mochitest", path)

        from mochitest_options import MochitestArgumentParser

    global parser
    parser = MochitestArgumentParser()
    return parser




@Command(
    "mochitest",
    category="testing",
    conditions=[functools.partial(conditions.is_buildapp_in, apps=SUPPORTED_APPS)],
    description="Run any flavor of mochitest (integration test).",
    parser=setup_argument_parser,
)
def run_mochitest_general(
    command_context, flavor=None, test_objects=None, resolve_tests=True, **kwargs
):
    from mochitest_options import ALL_FLAVORS
    from mozlog.commandline import setup_logging
    from mozlog.handlers import StreamHandler
    from moztest.resolve import get_suite_definition

    # TODO: This is only strictly necessary while mochitest is using Python
    # 2 and can be removed once the command is migrated to Python 3.
    command_context.activate_virtualenv()

    buildapp = None
    for app in SUPPORTED_APPS:
        if conditions.is_buildapp_in(command_context, apps=[app]):
            buildapp = app
            break

    flavors = None
    if flavor:
        for fname, fobj in ALL_FLAVORS.items():
            if flavor in fobj["aliases"]:
                if buildapp not in fobj["enabled_apps"]:
                    continue
                flavors = [fname]
                break
    else:
        flavors = [f for f, v in ALL_FLAVORS.items() if buildapp in v["enabled_apps"]]

    from mozbuild.controller.building import BuildDriver

    command_context._ensure_state_subdir_exists(".")

    test_paths = kwargs["test_paths"]
    kwargs["test_paths"] = []

    if kwargs.get("debugger", None):
        import mozdebug

        if not mozdebug.get_debugger_info(kwargs.get("debugger")):
            sys.exit(1)

    mochitest = command_context._spawn(MochitestRunner)
    tests = []
    if resolve_tests:
        tests = mochitest.resolve_tests(
            test_paths, test_objects, cwd=command_context._mach_context.cwd
        )

    if not kwargs.get("log"):
        # Create shared logger
        format_args = {"level": command_context._mach_context.settings["test"]["level"]}
        if len(tests) == 1:
            format_args["verbose"] = True
            format_args["compact"] = False

        default_format = command_context._mach_context.settings["test"]["format"]
        kwargs["log"] = setup_logging(
            "mach-mochitest", kwargs, {default_format: sys.stdout}, format_args
        )
        for handler in kwargs["log"].handlers:
            if isinstance(handler, StreamHandler):
                handler.formatter.inner.summary_on_shutdown = True

    driver = command_context._spawn(BuildDriver)
    driver.install_tests()

    subsuite = kwargs.get("subsuite")
    if subsuite == "default":
        kwargs["subsuite"] = None

    suites = defaultdict(list)
    is_webrtc_tag_present = False
    unsupported = set()
    for test in tests:
        # Check if we're running a webrtc test so we can enable webrtc
        # specific test logic later if needed.
        if "webrtc" in test.get("tags", ""):
            is_webrtc_tag_present = True

        # Filter out non-mochitests and unsupported flavors.
        if test["flavor"] not in ALL_FLAVORS:
            continue

        key = (test["flavor"], test.get("subsuite", ""))
        if test["flavor"] not in flavors:
            unsupported.add(key)
            continue

        if subsuite == "default":
            # "--subsuite default" means only run tests that don't have a subsuite
            if test.get("subsuite"):
                unsupported.add(key)
                continue
        elif subsuite and test.get("subsuite", "") != subsuite:
            unsupported.add(key)
            continue

        suites[key].append(test)

    # Only webrtc mochitests in the media suite need the websocketprocessbridge.
    if ("mochitest", "media") in suites and is_webrtc_tag_present:
        req = os.path.join(
            "testing",
            "tools",
            "websocketprocessbridge",
            "websocketprocessbridge_requirements_3.txt",
        )
        command_context.virtualenv_manager.activate()
        command_context.virtualenv_manager.install_pip_requirements(
            req, require_hashes=False
        )

        # sys.executable is used to start the websocketprocessbridge, though for some
        # reason it doesn't get set when calling `activate_this.py` in the virtualenv.
        sys.executable = command_context.virtualenv_manager.python_path

    if ("browser-chrome", "a11y") in suites and sys.platform == "win32":
        # Only Windows a11y browser tests need this.
        req = os.path.join(
            "accessible",
            "tests",
            "browser",
            "windows",
            "a11y_setup_requirements.txt",
        )
        command_context.virtualenv_manager.activate()
        command_context.virtualenv_manager.install_pip_requirements(
            req, require_hashes=False
        )

    # This is a hack to introduce an option in mach to not send
    # filtered tests to the mochitest harness. Mochitest harness will read
    # the master manifest in that case.
    if not resolve_tests:
        for flavor in flavors:
            key = (flavor, kwargs.get("subsuite"))
            suites[key] = []

    if not suites:
        # Make it very clear why no tests were found
        if not unsupported:
            print(
                TESTS_NOT_FOUND.format(
                    "\n".join(sorted(list(test_paths or test_objects)))
                )
            )
            return 1

        msg = []
        for f, s in unsupported:
            fobj = ALL_FLAVORS[f]
            apps = fobj["enabled_apps"]
            name = fobj["aliases"][0]
            if s:
                name = f"{name} --subsuite {s}"

            if buildapp not in apps:
                reason = "requires {}".format(" or ".join(apps))
            else:
                reason = "excluded by the command line"
            msg.append(f"    mochitest -f {name} ({reason})")
        print(SUPPORTED_TESTS_NOT_FOUND.format(buildapp, "\n".join(sorted(msg))))
        return 1

    run_mochitest = mochitest.run_desktop_test

    overall = None
    for (flavor, subsuite), tests in sorted(suites.items()):
        suite_name, suite = get_suite_definition(flavor, subsuite)
        if "test_paths" in suite["kwargs"]:
            del suite["kwargs"]["test_paths"]

        harness_args = kwargs.copy()
        harness_args.update(suite["kwargs"])
        # Pass in the full suite name as defined in moztest/resolve.py in case
        # chunk-by-runtime is called, in which case runtime information for
        # specific mochitest suite has to be loaded. See Bug 1637463.
        harness_args.update({"suite_name": suite_name})

        result = run_mochitest(
            command_context._mach_context, tests=tests, **harness_args
        )

        if result:
            overall = result

        # Halt tests on keyboard interrupt
        if result == -1:
            break

    # Only shutdown the logger if we created it
    if kwargs["log"].name == "mach-mochitest":
        kwargs["log"].shutdown()

    return overall
