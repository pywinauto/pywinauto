pushd pywinauto\windows\injected\backends\dotnet

mkdir build32
cmake  -G "Visual Studio 14 2015" -A Win32 -B .\build32
cmake --build build32 --target install --config Release

mkdir build64
cmake  -G "Visual Studio 14 2015" -A x64 -B .\build64
cmake --build build64 --target install --config Release

popd