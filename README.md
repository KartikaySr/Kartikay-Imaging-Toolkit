<!-- Modified by Kartikay Srivastava on 2026-11-08. -->
<p align="center"><img src="Documentation/Art/kartikay-banner.svg" alt="Kartikay Imaging Toolkit — Kartikay Srivastava" width="900"></p>

# Kartikay Imaging Toolkit

**A project by Kartikay Srivastava · Project lead and maintainer**

A cross-platform C++ and Python toolkit for scientific image processing,
segmentation, and registration in two, three, and higher dimensions.

This is Kartikay Srivastava's independently branded distribution, derived from
ITK. Original development and third-party contributions are credited in
[CONTRIBUTORS.md](CONTRIBUTORS.md).

## Build from this source

Requires CMake 3.22.1 or newer and a C++17 compiler.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF
cmake --build build --parallel 4
```

For the managed development environment, install Pixi and run:

```sh
pixi install -e cxx
pixi run -e cxx build-release
```

For Python wrapping:

```sh
pixi install -e python
pixi run -e python build-python
```

The source retains `itk`, `ITK`, `find_package(ITK)`, library names, and CMake
options for compatibility. `pip install itk` installs an upstream package;
it does not install this branded source distribution.

## Explore

- [Getting started](GettingStarted.md)
- [Documentation source](Documentation/docs/index.md)
- [API documentation source](Documentation/Doxygen/MainPage.dox)
- [Contributing](CONTRIBUTING.md)
- [Project governance](GOVERNANCE.md)
- [Contributors and upstream acknowledgments](CONTRIBUTORS.md)
- [Branding and distribution notes](BRANDING.md)

## License and attribution

Distributed under [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) and
[third-party licenses](Documentation/docs/licenses.md) for retained notices.
Branding and distribution changes are credited to Kartikay Srivastava;
original source authorship remains credited to its contributors.
