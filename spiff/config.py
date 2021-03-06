"""
Configure glymur to use installed libraries if possible.
"""
import ctypes
from ctypes.util import find_library
import os
import pathlib
import platform
import sys
import warnings

# default library locations for MacPorts
_macports_default_location = {'tiff': '/opt/local/lib/libtiff.dylib'}


def load_libraries(*pargs):
    """
    Get a list of ctypes handles, one for each library.
    """
    lst = []
    for name in pargs:
        handle = load_library(name)
        lst.append(handle)

    return tuple(lst)


def load_library(name):

    path = None

    if ((('Anaconda' in sys.version) or
         ('Continuum Analytics, Inc.' in sys.version) or
         ('packaged by conda-forge' in sys.version))):
        # If Anaconda, then openjpeg may have been installed via conda.
        python_path = pathlib.Path(sys.executable)
        if platform.system() in ['Linux', 'Darwin']:
            suffix = '.so' if platform.system() == 'Linux' else '.dylib'
            basepath = python_path.parents[1]
            lib = basepath / 'lib' / (f"lib{name}{suffix}")
        elif platform.system() == 'Windows':
            lib = basepath / 'Library' / 'bin' / f"{name}.dll"

        if lib.exists():
            path = lib

    if path is None:
        # Can ctypes find it in the default system locations?
        path = find_library(name)

    if path is None:
        if platform.system() == 'Darwin':
            # OpenJPEG may have been installed via MacPorts
            path = _macports_default_location[name]

        if path is not None and not os.path.exists(path):
            # the mac/win default location does not exist.
            return None

    return load_library_handle(name, path)


def load_library_handle(libname, path):
    """Load the library, return the ctypes handle."""

    if path is None or path in ['None', 'none']:
        # Either could not find a library via ctypes or
        # user-configuration-file, or we could not find it in any of the
        # default locations, or possibly the user intentionally does not want
        # one of the libraries to load.
        msg = "The tiff library could be loaded.  "
        warnings.warn(msg)

        return None

    try:
        if os.name == "nt":
            opj_lib = ctypes.windll.LoadLibrary(path)
        else:
            opj_lib = ctypes.CDLL(path)
    except (TypeError, OSError):
        msg = 'The {libname} library at {path} could not be loaded.'
        msg = msg.format(path=path, libname=libname)
        warnings.warn(msg, UserWarning)
        opj_lib = None

    return opj_lib
