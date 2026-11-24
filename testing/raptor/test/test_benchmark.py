# testing/raptor/test/test_benchmark.py

import os
import subprocess
import sys
from unittest import mock

import mozunit

# Make the Raptor implementation modules importable.
here = os.path.abspath(os.path.dirname(__file__))
raptor_dir = os.path.join(os.path.dirname(here), "raptor")
sys.path.insert(0, raptor_dir)

from benchmark import Benchmark


def _git(repository, *args):
    subprocess.check_call(
        ["git", *args],
        cwd=repository,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _create_repository(repository):
    repository.mkdir(parents=True)

    subprocess.check_call(
        ["git", "init", "--initial-branch=main", str(repository)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    _git(repository, "config", "user.name", "Raptor tests")
    _git(repository, "config", "user.email", "raptor-tests@example.invalid")

    (repository / "index.html").write_text(
        "<!doctype html><title>Speedometer test</title>\n"
    )

    _git(repository, "add", "index.html")
    _git(repository, "commit", "-m", "Initial benchmark")

    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        text=True,
    ).strip()


def _make_benchmark(repository, revision):
    benchmark = Benchmark.__new__(Benchmark)
    benchmark.test = {
        "name": "speedometer3",
        "repository": str(repository),
        "repository_revision": revision,
        "host_from_parent": False,
        "test_url": "http://<host>:<port>/index.html",
    }
    benchmark.debug_mode = False
    return benchmark


def _prepare_paths(tmp_path):
    mozbuild_path = tmp_path / "mozbuild"
    cache_parent = mozbuild_path / "performance-tests"
    cache_parent.mkdir(parents=True)

    benchmark_dest = tmp_path / "benchmark-output"
    return mozbuild_path, cache_parent, benchmark_dest


def _run_setup(benchmark, paths):
    mozbuild_path, _, benchmark_dest = paths
    return benchmark._setup_git_benchmarks(
        mozbuild_path,
        benchmark_dest,
        run_local=True,
    )


def _assert_cache_is_valid(cache, repository, revision):
    assert (cache / "index.html").is_file()

    origin = subprocess.check_output(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=cache,
        text=True,
    ).strip()
    assert origin == str(repository)

    head = subprocess.check_output(
        ["git", "rev-parse", "--verify", "HEAD^{commit}"],
        cwd=cache,
        text=True,
    ).strip()
    assert head == revision


def test_missing_benchmark_cache_is_cloned(tmp_path):
    repository = tmp_path / "Speedometer"
    revision = _create_repository(repository)
    benchmark = _make_benchmark(repository, revision)
    paths = _prepare_paths(tmp_path)
    cache = paths[1] / "Speedometer"

    with mock.patch.object(benchmark, "_update_benchmark_repo") as update:
        _run_setup(benchmark, paths)

    update.assert_not_called()
    _assert_cache_is_valid(cache, repository, revision)


def test_non_git_cache_directory_is_replaced(tmp_path):
    repository = tmp_path / "Speedometer"
    revision = _create_repository(repository)
    benchmark = _make_benchmark(repository, revision)
    paths = _prepare_paths(tmp_path)
    cache = paths[1] / "Speedometer"

    cache.mkdir()
    (cache / "incomplete-clone-marker").write_text("incomplete\n")

    with mock.patch.object(benchmark, "_update_benchmark_repo") as update:
        _run_setup(benchmark, paths)

    update.assert_not_called()
    assert not (cache / "incomplete-clone-marker").exists()
    _assert_cache_is_valid(cache, repository, revision)


def test_cache_without_valid_head_is_replaced(tmp_path):
    repository = tmp_path / "Speedometer"
    revision = _create_repository(repository)
    benchmark = _make_benchmark(repository, revision)
    paths = _prepare_paths(tmp_path)
    cache = paths[1] / "Speedometer"

    cache.mkdir()
    _git(cache, "init", "--initial-branch=main")
    _git(cache, "remote", "add", "origin", str(repository))

    with mock.patch.object(benchmark, "_update_benchmark_repo") as update:
        _run_setup(benchmark, paths)

    update.assert_not_called()
    _assert_cache_is_valid(cache, repository, revision)


def test_cache_with_different_origin_is_replaced(tmp_path):
    repository = tmp_path / "Speedometer"
    revision = _create_repository(repository)

    other_repository = tmp_path / "Other"
    _create_repository(other_repository)

    benchmark = _make_benchmark(repository, revision)
    paths = _prepare_paths(tmp_path)
    cache = paths[1] / "Speedometer"

    subprocess.check_call(
        ["git", "clone", str(other_repository), str(cache)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    with mock.patch.object(benchmark, "_update_benchmark_repo") as update:
        _run_setup(benchmark, paths)

    update.assert_not_called()
    _assert_cache_is_valid(cache, repository, revision)


def test_valid_cache_with_matching_origin_is_updated(tmp_path):
    repository = tmp_path / "Speedometer"
    revision = _create_repository(repository)
    benchmark = _make_benchmark(repository, revision)
    paths = _prepare_paths(tmp_path)
    cache = paths[1] / "Speedometer"

    subprocess.check_call(
        ["git", "clone", str(repository), str(cache)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    with mock.patch.object(benchmark, "_update_benchmark_repo") as update:
        _run_setup(benchmark, paths)

    update.assert_called_once_with(cache)
    _assert_cache_is_valid(cache, repository, revision)


if __name__ == "__main__":
    mozunit.main()
