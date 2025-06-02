import os
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension


C_INCLUDE_DIR = os.path.join("capsa", "c_extension", "include")
C_SRC_DIR = os.path.join("capsa", "c_extension", "src")
PY_DIR = os.path.join("capsa")  # Destination for compiled C++ binary


setup(
    name="c_extension",
    ext_modules=[
        Pybind11Extension(
            "c_utils",
            sources=[
                os.path.join(C_SRC_DIR, "bindings.cpp"),
                os.path.join(C_SRC_DIR, "bot_features.cpp"),
                os.path.join(C_SRC_DIR, "logic.cpp"),
                os.path.join(C_SRC_DIR, "utils.cpp"),
            ],
            include_dirs=[C_INCLUDE_DIR],
            cxx_std=17,
        )
    ],
    options={
        "build_ext": {"build_lib": PY_DIR},
    },
)
