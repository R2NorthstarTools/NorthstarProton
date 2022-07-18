# NorthstarProton
A Proton build based on TKG's proton-tkg build system to run the Northstar client with minimal end-user interaction. Users can switch between running Northstar and running vanilla Titanfall 2 simply by switching proton builds between this one and official Valve proton.

**Please report any issues on this repo, do not take them to upstream wine or TKG's github.**

**DO NOT USE THIS PROTON RUNNER FOR ANY GAMES OTHER THAN TF|2 + NORTHSTAR**

glibc 2.33 is a hard minimum requirement for the time being.

## Features
- Latest DXVK release patched with DXVK-async.
- DXVK-async enabled by default, no launch options required.
- `wsock32.dll` as a DLL override by default to enable Northstar, no launch options required.
- LatencyFleX wine components to reduce setup. Users need to set up the vulkan layer and add `LFX=1` to enable.
- Works on some SteamDecks, still in testing.

