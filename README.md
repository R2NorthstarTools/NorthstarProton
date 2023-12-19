# NorthstarProton
A Proton build based on GloriousEggroll's proton-ge-custom that serves as an official, stable, and supported runner for playing Titanfall 2 + Northstar on Linux and SteamDeck.

https://r2northstar.gitbook.io/r2northstar-wiki/installing-northstar/steamdeck-and-linux/installing-on-steamdeck-and-linux

## IMPORTANT

- This is a custom build of Proton, and is *not* affiliated with Valve's Proton.
- The use of this Proton build, or any Proton build, outside of Steam is universally unsupported.
- Report any issues with *this* Proton build to *this* repo -OR- make a ticket on the Northstar Discord [invite link](https://discord.com/invite/northstar). Do not take them to upstream wine, Valve, or GE.
- Do not use this Proton runner for any games other than TF|2 / Northstar

## What's new (vs. legacy NorthstarProton)
- Valve wine base instead of wine-staging
- Soft fork of proton-ge-custom instead of using Proton-TKG build system
- No longer requires a minimum system `glibc` version

## LatencyFleX

Once you have installed the vulkan layer properly, LatencyFlex can be enabled by adding `LFX=1 %command%` to your Titanfall 2 launch options, nothing else is required.

## (2) If you have an issue that happens with my proton-GE build, provided FROM this repository, that does -not- happen on Valve's proton, please DO NOT open a bug report on Valve's bug tracker. Instead, contact me on Discord about the issue:

https://discord.gg/6y3BdzC

## (3)  Please note, this is a custom build of proton, and is -not- affiliated with Valve's proton.
## (4) Please also note I do not provide the flatpak of proton-GE, and I do not provide the AUR version of proton-GE. I will not assist with those.
## (5) The only version of proton-GE that I provide and will assist with builds of is the one provided within this repository, using the build system documented here.
## (6) I cannot validate the accuracy or functionality of other builds that have not been built using the build system included here.

## Table of contents

- [Overview](#overview)
	- [Notes](#notes)
- [Installation](#installation)
	- [Native](#native)
	- [Flatpak](#flatpak)
		- [Flathub](#flathub)
		- [Manual](#manual)
- [Building](#building)
- [Enabling](#enabling)
- [Modification](#modification)
- [Credits](#credits)
	- [TKG (Etienne Juvigny)](#tkg-etienne-juvigny)
	- [Guy1524 (Derek Lesho)](#guy1524-derek-lesho)
	- [Joshie (Joshua Ashton)](#joshie-joshua-ashton)
	- [doitsujin/ドイツ人 (Philip Rebohle)](#doitsujinドイツ人-philip-rebohle)
	- [HansKristian/themaister (Hans-Kristian Arntzen)](#hanskristianthemaister-hans-kristian-arntzen)
	- [flibitijibibo (Ethan Lee)](#flibitijibibo-ethan-lee)
	- [simmons-public (Chris Simmons)](#simmons-public-chris-simmons)
	- [Sporif (Amine Hassane)](#sporif-amine-hassane)
	- [wine-staging maintainers](#wine-staging-maintainers)
	- [Reporters](#reporters)
	- [Patrons](#patrons)
- [Donations](#donations)
- [Tested Games](#tested-games)

## Overview

This is my build of Proton with the most recent bleeding-edge Proton Experimental WINE.

Things it contains that Valve's Proton does not:

- Additional media foundation patches for better video playback support
- AMD FSR patches added directly to fullscreen hack that can be toggled with WINE_FULLSCREEN_FSR=1
- FSR Fake resolution patch details [here](https://github.com/GloriousEggroll/proton-ge-custom/pull/52)
- Nvidia CUDA support for PhysX and NVAPI
- Raw input mouse support
- 'protonfixes' system -- this is an automated system that applies per-game fixes (such as winetricks, envvars, EAC workarounds, overrides, etc).
- Various upstream WINE patches backported
- Various wine-staging patches applied as they become needed

## Notes

- Warframe is problematic with VSync. Turn it off or on in game, do not set to `Auto`
- Warframe needs a set a frame limit in game. Unlimited framerate can cause slowdowns
- Warframe on NVIDIA: you may need to disable GPU Particles in game otherwise the game can freeze randomly. On AMD they work fine

Full patches can be viewed in [protonprep-valve-staging.sh](patches/protonprep-valve-staging.sh).

## Installation

PLEASE NOTE: There are prerequisites for using this version of proton:

1. You must have the proper Vulkan drivers/packages installed on your system. VKD3D on AMD requires Mesa 22.0.0 or higher for the VK_KHR_dynamic_rendering extension. Check [here ](https://github.com/lutris/docs/blob/master/InstallingDrivers.md) for general driver installation guidance.

### Manual

#### Via [`asdf`, the version manager](https://asdf-vm.com/)

There is an unofficial [plugin for installing and managing ProtonGE versions](https://github.com/augustobmoura/asdf-protonge)
with [`asdf` (the universal version manager)](https://asdf-vm.com/), it follows
the same process as the manual installation but makes it a lot easier. Managing
versions by removing and updating to newer versions also becomes easier.

To install by it first [install `asdf`](https://asdf-vm.com/guide/getting-started.html),
and then proceed to add the ProtonGE plugin and install the version you want.
``` bash
asfd plugin add protonge

# Or install a version from a tag (Eg.: GE-Proton8-25)
asdf install protonge latest
```

It's also possible to use the asdf plugin in Flatpak installations, by
customizing the target `compatibilitytools.d` path. For more settings check the
[plugin's official documentation](https://github.com/augustobmoura/asdf-protonge)

After every install you need to restart Steam, and [enable proton-ge-custom](#enabling).

#### Native

This section is for those that use the native version of Steam.

1. Download a release from the [Releases](https://github.com/GloriousEggroll/proton-ge-custom/releases) page.
2. Create a `~/.steam/root/compatibilitytools.d` directory if it does not exist.
3. Extract the release tarball into `~/.steam/root/compatibilitytools.d/`.
   * `tar -xf GE-ProtonVERSION.tar.gz -C ~/.steam/root/compatibilitytools.d/`
4. Restart Steam.
5. [Enable proton-ge-custom](#enabling).
  
    
*Terminal example based on Latest Release*
```bash
# make temp working directory
mkdir /tmp/proton-ge-custom
cd /tmp/proton-ge-custom

# download  tarball
curl -sLOJ "$(curl -s https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest | grep browser_download_url | cut -d\" -f4 | grep .tar.gz)"

# download checksum
curl -sLOJ "$(curl -s https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest | grep browser_download_url | cut -d\" -f4 | grep .sha512sum)"

# check tarball with checksum
sha512sum -c ./*.sha512sum
# if result is ok, continue

# make steam directory if it does not exist
mkdir -p ~/.steam/root/compatibilitytools.d

# extract proton tarball to steam directory
tar -xf GE-Proton*.tar.gz -C ~/.steam/root/compatibilitytools.d/
echo "All done :)"
```

The shell code above can be run as a script by pasting the commands in a file and adding the following to the top of the file:
```bash
#!/bin/bash
set -euo pipefail
```

Save the file and make the script runnable by adding the executable bit:
```bash
chmod +x file.sh
```

#### Flatpak

This section is for those that use the Steam flatpak.

##### Flathub

[The unofficial build provided by Flathub](https://github.com/flathub/com.valvesoftware.Steam.CompatibilityTool.Proton-GE) isn't supported by GloriousEggroll nor Valve and wasn't tested with all possible games and cases. It can behave differently from upstream builds. Use at your own risk.

1. [Add the Flathub repository](https://flatpak.org/setup/).
2. Run:
	```bash
	flatpak install com.valvesoftware.Steam.CompatibilityTool.Proton-GE
	```
3. [Enable proton-ge-custom](#enabling).

##### Manual

1. Download a release from the [Releases](https://github.com/GloriousEggroll/proton-ge-custom/releases) page.
2. Create a `~/.var/app/com.valvesoftware.Steam/data/Steam/compatibilitytools.d/` directory if it does not exist.
3. Extract the release tarball into `~/.var/app/com.valvesoftware.Steam/data/Steam/compatibilitytools.d/`.
   * `tar -xf GE-ProtonVERSION.tar.gz -C ~/.var/app/com.valvesoftware.Steam/data/Steam/compatibilitytools.d/`
4. Restart Steam.
5. [Enable proton-ge-custom](#enabling).

#### Snap

This section is for those that use the Steam [snap](https://snapcraft.io/steam).

This unofficial build isn't supported by GloriousEggroll nor Valve and wasn't tested with all possible games and cases. It can behave differently from upstream builds. Use at your own risk.

##### Manual

1. Download a release from the [Releases](https://github.com/GloriousEggroll/proton-ge-custom/releases) page.
2. Create a `~/snap/steam/common/.steam/steam/compatibilitytools.d/` directory if it does not exist.
3. Extract the release tarball into `~/snap/steam/common/.steam/steam/compatibilitytools.d/`.
   * `tar -xf GE-ProtonVERSION.tar.gz -C ~/snap/steam/common/.steam/steam/compatibilitytools.d/`
4. Restart Steam.
5. [Enable proton-ge-custom](#enabling).

## Building

1. Clone this repo by executing:

```sh
git clone --recurse-submodules http://github.com/gloriouseggroll/proton-ge-custom
```

2. Drop any custom patches into patches/, then open patches/protonprep-valve-staging.sh and add a patch line for them under `#WINE CUSTOM PATCHES` in the same way the others are done.

3. Apply all of the patches in patches/ by running:

```sh
./patches/protonprep-valve-staging.sh &> patchlog.txt
```

in the main proton-ge-custom directory. Open `patchlog.txt` and search for "fail" to make sure no patch failures occured. An easy way to do this is like so:

```sh
grep -i fail patchlog.txt
grep -i error patchlog.txt 
```

4. Navigate to the parent directory containing the proton-ge-custom folder.

5. Type the following (note: if using docker instead of podman, change to --container-engine=docker):

```sh
mkdir build && cd build
../configure.sh --enable-ccache --build-name=SOME-BUILD-NAME-HERE --container-engine=podman
make redist &> log
```

Build will be placed within the build directory as SOME-BUILD-NAME-HERE.tar.gz.

## Credits

**Jan ([Jan200101](https://github.com/Jan200101))**, for spearheading the overhaul of NorthstarProton.

**Thomas Crider ([GloriousEggroll](https://github.com/GloriousEggroll))**, for proton-ge-custom.

**Tatsuyuki Ishi ([ishitatsuyuki](https://github.com/ishitatsuyuki))**, for LatencyFleX.

**Etienne Juvigny ([TK-Glitch](https://github.com/Tk-Glitch))**, for the proton-tkg build system.

**Amine Hassane ([Sporif](https://github.com/Sporif))**, for continually maintaining DXVK-async.

**Chris Simons ([simons-public](https://github.com/simons-public))** for Protonfixes, which I have shamelessly butchered into the legacy version of this project.
