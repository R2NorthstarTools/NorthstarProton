#!/bin/bash

dxvk_async_release="1.10.2"
lfx_release="0.1.0"

echo "Cloning wine-tkg-git repository..."
git clone https://github.com/Frogging-Family/wine-tkg-git.git

cp -vf files/proton-tkg.cfg wine-tkg-git/proton-tkg/proton-tkg.cfg
cp -vf files/advanced-customization.cfg wine-tkg-git/proton-tkg/proton-tkg-profiles/advanced-customization.cfg

echo "Building TKG-Proton base"
cd wine-tkg-git/proton-tkg
./proton-tkg.sh

echo "TKG-Proton base built"
echo "The next add the following line to the file that automatically opens:"
echo ""
echo "\"WINEDLLOVERRIDES\": \"wsock32=n,b\","
echo ""
read -p "Press any key when ready"

cd built/*
nano user_settings.py

echo "DLL override added"
cd ..
echo "Downloading DXVK-async..."
wget "https://github.com/Sporif/dxvk-async/releases/download/$dxvk_async_release/dxvk-async-$dxvk_async_release.tar.gz"
echo "Extracting..."
tar -xvf "dxvk-async-$dxvk_async_release.tar.gz"

echo "Installing DXVK-async binaries"
cp -vf dxvk-async-$dxvk_async_release/x32/* proton_tkg*/files/lib/wine/dxvk/
cp -vf dxvk-async-$dxvk_async_release/x64/* proton_tkg*/files/lib64/wine/dxvk/
echo "Cleaning up DXVK-async"
rm -vf "dxvk-async-$dxvk_async_release.tar.gz"
rm -dvrf dxvk-async-$dxvk_async_release

echo "DXVK-async installation finished."
echo "Installing LatencyFleX Wine components."
wget "https://github.com/ishitatsuyuki/LatencyFleX/releases/download/v$lfx_release/latencyflex-v$lfx_release.tar.xz"
tar -xvf "latencyflex-v$lfx_release.tar.xz"

cp -vf latencyflex-v$lfx_release/wine/usr/lib/wine/x86_64-windows/latencyflex_layer.dll proton_tkg*/files/lib64/wine/x86_64-windows/
cp -vf latencyflex-v$lfx_release/wine/usr/lib/wine/x86_64-windows/latencyflex_wine.dll proton_tkg*/files/lib64/wine/x86_64-windows/
cp -vf latencyflex-v$lfx_release/wine/usr/lib/wine/x86_64-unix/latencyflex_layer.so proton_tkg*/files/lib64/wine/x86_64-unix/
cp -vf latencyflex-v$lfx_release/wine/usr/lib/wine/x86_64-windows/latencyflex_layer.dll proton_tkg*/files/share/default_pfx/drive_c/windows/system32/
cp -vf latencyflex-v$lfx_release/wine/usr/lib/wine/x86_64-windows/latencyflex_wine.dll proton_tkg*/files/share/default_pfx/drive_c/windows/system32/

echo "LatencyFleX Wine components installed"
echo "Cleaning up"
rm -vf "latencyflex-v$lfx_release.tar.xz"
rm -dvrf latencyflex-v$lfx_release

echo ""
echo "Northstar-Proton generation is complete. The final step is naming the build."
echo "Be consistent. Four files with a total of five locations must be changed to the same string to update the visual and internal version"
echo "Copy the name to your clipboard. The files will open automatically."
echo ""
read -p "Press any key to continue"

cd proton_tkg*
nano compatibilitytool.vdf
nano version
nano files/version
nano proton
cd ..

echo "Generation complete"
read -p "Press any key to compress to .tar.gz"
version=$(cat proton_tkg*/files/version | cut -f 2 -d ' ')
mv proton_tkg* $version
tar -zcvf $version.tar.gz $version

