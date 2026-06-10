This folder contains test applications (mostly binaries) which are used for unit testing.

Building Qt test applications
=============================

The Qt backend tests use standalone Qt example applications. Each sample
directory contains the executable and the Qt runtime files required to start it
without a system-wide Qt installation.

Windows
-------

1. Build the required Qt examples from the Qt installation. For CMake-based
   examples:

       cmake -S <example-source> -B <build-dir> -DCMAKE_PREFIX_PATH=<qt-prefix>
       cmake --build <build-dir> --config Release

   For qmake-based examples:

       qmake <example>.pro
       nmake release

2. Copy the resulting executable to the corresponding Qt sample directory under
   apps.

3. Run windeployqt for every executable to copy Qt DLLs, plugins, translations
   and QML modules:

       <qt-prefix>\bin\windeployqt.exe <path-to-executable>

Linux
-----

1. Build the required Qt examples. For CMake-based examples:

       cmake -S <example-source> -B <build-dir> -DCMAKE_PREFIX_PATH=<qt-prefix>
       cmake --build <build-dir> --config Release

   For qmake-based examples:

       qmake <example>.pro
       make

2. Copy each executable to the corresponding Linux Qt sample directory under
   apps.

3. Copy runtime dependencies into the sample directory:

   * lib - Qt libraries and non-Qt shared libraries required by ldd;
   * plugins/platforms/libqxcb.so - the XCB platform plugin;
   * qml - QML modules required by Qt Quick examples.

4. Verify that every executable resolves its dependencies from the sample
   directory:

       LD_LIBRARY_PATH=<sample-dir>/lib ldd <sample-dir>/<executable>
