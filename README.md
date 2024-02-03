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
- Support for R2Ronin (speedrunning fork of R2Northstar)

## LatencyFleX

Once you have installed the vulkan layer properly, LatencyFlex can be enabled by adding `LFX=1 %command%` to your Titanfall 2 launch options, nothing else is required.

## Building

1. Clone this repo by executing:

```sh
git clone --recurse-submodules https://github.com/R2NorthstarTools/NorthstarProton
```

2. Drop any custom patches into patches/, then open patches/protonprep-valve-staging.sh and add a patch line for them under `#WINE CUSTOM PATCHES` in the same way the others are done.

3. Apply all of the patches in patches/ by running:

```sh
./patches/protonprep-valve-staging.sh &> patchlog.txt
```

in the main NorthstarProton directory. Open `patchlog.txt` and search for "fail" to make sure no patch failures occured. An easy way to do this is like so:

```sh
grep -i fail patchlog.txt
grep -i error patchlog.txt 
```

4. Navigate to the parent directory containing the NorthstarProton folder.

5. Type the following (note: if using docker instead of podman, change to --container-engine=docker):

```sh
mkdir build && cd build
../configure.sh --enable-ccache --build-name=SOME-BUILD-NAME-HERE --container-engine=podman
make redist &> log
```

Build will be placed within the build directory as SOME-BUILD-NAME-HERE.tar.gz.

## Credits

**Jan ([Jan200101](https://github.com/Jan200101))**, for spearheading the overhaul of NorthstarProton and various patches to improve compatability.

**Thomas Crider ([GloriousEggroll](https://github.com/GloriousEggroll))**, for proton-ge-custom.

**Tatsuyuki Ishi ([ishitatsuyuki](https://github.com/ishitatsuyuki))**, for LatencyFleX.

**Etienne Juvigny ([TK-Glitch](https://github.com/Tk-Glitch))**, for the proton-tkg build system.

**Amine Hassane ([Sporif](https://github.com/Sporif))**, for continually maintaining DXVK-async.

**Chris Simons ([simons-public](https://github.com/simons-public))** for Protonfixes, which I have shamelessly butchered into the legacy version of this project.
