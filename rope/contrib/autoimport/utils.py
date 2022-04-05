"""Utility functions for the autoimport code."""
import pathlib
import sys
from collections import OrderedDict
from typing import List, Optional, Set, Tuple

from rope.base.project import Project

from .defs import PackageType, Source


def get_package_name_from_path(
    package_path: pathlib.Path,
) -> Optional[Tuple[str, PackageType]]:
    """Get package name and type from a path."""
    package_name = package_path.name
    if package_name.endswith(".egg-info"):
        return None
    if package_name.endswith(".so"):
        name = package_name.split(".")[0]
        return (name, PackageType.COMPILED)
    if package_name.endswith(".py"):
        stripped_name = package_name.removesuffix(".py")
        return (stripped_name, PackageType.SINGLE_FILE)
    return (package_name, PackageType.STANDARD)


def get_modname_from_path(
    modpath: pathlib.Path, package_path: pathlib.Path, add_package_name: bool = True
) -> str:
    """Get module name from a path in respect to package."""
    package_name: str = package_path.name
    modname = (
        modpath.relative_to(package_path)
        .as_posix()
        .removesuffix("/__init__.py")
        .removesuffix(".py")
        .replace("/", ".")
    )
    if add_package_name:
        modname = package_name if modname == "." else package_name + "." + modname
    else:
        assert modname != "."
    return modname


def get_package_source(
    package: pathlib.Path, project: Optional[Project] = None
) -> Source:
    """Detect the source of a given package. Rudimentary implementation."""
    if project is not None and package.as_posix().__contains__(project.address):
        return Source.PROJECT
    if package.as_posix().__contains__("site-packages"):
        return Source.SITE_PACKAGE
    if package.as_posix().startswith(sys.prefix):
        return Source.STANDARD
    return Source.UNKNOWN


def sort_and_deduplicate(results: List[Tuple[str, int]]) -> List[str]:
    """Sort and deduplicate a list of name, source entries."""
    if len(results) == 0:
        return []
    results.sort(key=lambda y: y[-1])
    results_sorted = list(zip(*results))[0]
    return list(OrderedDict.fromkeys(results_sorted))


def sort_and_deduplicate_tuple(
    results: List[Tuple[str, str, int]]
) -> List[Tuple[str, str]]:
    """Sort and deduplicate a list of name, module, source entries."""
    if len(results) == 0:
        return []
    results.sort(key=lambda y: y[-1])
    results_sorted = []
    for result in results:
        results_sorted.append(result[:-1])
    return list(OrderedDict.fromkeys(results_sorted))


def submodules(mod: pathlib.Path) -> Set[pathlib.Path]:
    """Find submodules in a given path using __init__.py."""
    result = set()
    if mod.is_dir() and (mod / "__init__.py").exists():
        result.add(mod)
        for child in mod.iterdir():
            result |= submodules(child)
    return result
