#!/bin/bash

dxvk_async_release="1.10.2" #Use a tagged release here
lfx_release="0.1.0" #Use a tagged release here
nsprtn_rel_name="NorthstarProton-7.13-dev" #Name of the new NorthstarProton build
tkg_protonpy_changeme="7.13-0" #This is the string to replace in the proton python file in the main directory. This is usually <wine-staging version>-0 when using a tagged wine-staging release in files/customization.cfg

echo "Cloning wine-tkg-git repository..."
git clone https://github.com/Frogging-Family/wine-tkg-git.git

cp -vf files/proton-tkg.cfg wine-tkg-git/proton-tkg/proton-tkg.cfg
cp -vf files/advanced-customization.cfg wine-tkg-git/proton-tkg/proton-tkg-profiles/advanced-customization.cfg

echo "Building TKG-Proton base"
cd wine-tkg-git/proton-tkg
./proton-tkg.sh

echo ""
echo "TKG-Proton base built"
echo "If TKG-Proton failed to build, press good ol' ctrl+c to restart."
echo ""

read -p "Otherwise, press any key to add the special sauce :^)"

echo "Renaming directory"
cd built
mv proton_tkg* $nsprtn_rel_name

echo "Installing Protonfixes"
cp -rvf ../../../protonfixes/ $nsprtn_rel_name/

cd $nsprtn_rel_name

echo "Enabling Protonfixes"
sed -i '1s/^/import protonfixes\n/' user_settings.py

echo "Protonfixes installed and enabled."
cd ..
echo "Downloading DXVK-async..."
wget "https://github.com/Sporif/dxvk-async/releases/download/$dxvk_async_release/dxvk-async-$dxvk_async_release.tar.gz"
echo "Extracting..."
tar -xvf "dxvk-async-$dxvk_async_release.tar.gz"

echo "Installing DXVK-async binaries"
cp -vf dxvk-async-$dxvk_async_release/x32/* $nsprtn_rel_name/files/lib/wine/dxvk/
cp -vf dxvk-async-$dxvk_async_release/x64/* $nsprtn_rel_name/files/lib64/wine/dxvk/
echo "Cleaning up DXVK-async"
rm -vf "dxvk-async-$dxvk_async_release.tar.gz"
rm -dvrf dxvk-async-$dxvk_async_release

echo "DXVK-async installation finished."
echo "Installing LatencyFleX Wine components."
wget "https://github.com/ishitatsuyuki/LatencyFleX/releases/download/v$lfx_release/latencyflex-v$lfx_release.tar.xz"
tar -xvf "latencyflex-v$lfx_release.tar.xz"

cp -vf latencyflex-v$lfx_release/wine/usr/lib/wine/x86_64-windows/latencyflex_layer.dll $nsprtn_rel_name/files/lib64/wine/x86_64-windows/
cp -vf latencyflex-v$lfx_release/wine/usr/lib/wine/x86_64-windows/latencyflex_wine.dll $nsprtn_rel_name/files/lib64/wine/x86_64-windows/
cp -vf latencyflex-v$lfx_release/wine/usr/lib/wine/x86_64-unix/latencyflex_layer.so $nsprtn_rel_name/files/lib64/wine/x86_64-unix/
cp -vf latencyflex-v$lfx_release/wine/usr/lib/wine/x86_64-windows/latencyflex_layer.dll $nsprtn_rel_name/files/share/default_pfx/drive_c/windows/system32/
cp -vf latencyflex-v$lfx_release/wine/usr/lib/wine/x86_64-windows/latencyflex_wine.dll $nsprtn_rel_name/files/share/default_pfx/drive_c/windows/system32/

echo "LatencyFleX Wine components installed"
echo "Cleaning up"
rm -vf "latencyflex-v$lfx_release.tar.xz"
rm -dvrf latencyflex-v$lfx_release

echo ""
echo "Northstar-Proton generation is complete. Naming build."
echo ""

cd $nsprtn_rel_name
old_version=$(cat version | cut -f 2 -d ' ')
sed -i "s/$old_version/$nsprtn_rel_name/g" compatibilitytool.vdf
sed -i "s/$old_version/$nsprtn_rel_name/g" version
sed -i "s/$old_version/$nsprtn_rel_name/g" files/version
sed -i "s/$tkg_protonpy_changeme/$nsprtn_rel_name/g" proton
cd ..

echo "Generation complete"
read -p "Press any key to compress to .tar.gz"
tar -zcvf $nsprtn_rel_name.tar.gz $nsprtn_rel_name

