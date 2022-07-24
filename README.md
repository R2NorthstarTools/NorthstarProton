# NorthstarProton
A Proton build based on TKG's proton-tkg build system to run the Northstar client on Linux and SteamDeck, along with some enhancements out-of-the-box.

Officially supported runner for playing TF|2 + Northstar through Steam on Linux and SteamDeck.

https://r2northstar.gitbook.io/r2northstar-wiki/using-northstar/playing-on-linux

## IMPORTANT

- This is a custom build of Proton, and is *not* affiliated with Valve's Proton.
- The use of this Proton build, or any Proton build, outside of Steam is universally unsupported.
- Report any issues with *this* Proton build to *this* repo. Do not take them to upstream wine, Valve, or TKG.
- Do not use this Proton runner for any games other than TF|2 / Northstar
- Currently, builds are done on Arch Linux with `glibc 2.33-6`. At the moment, we track whatever is on SteamOS/SteamDeck.

## Features
- Latest DXVK release patched with DXVK-async.
- DXVK-async enabled by default, no launch options required.
- `wsock32.dll` as a DLL override by default to enable Northstar, no launch options required.
- LatencyFleX wine components to reduce setup. Users need to set up the vulkan layer and add `LFX=1` to enable.
- Allows for Northstar to run on SteamDeck.

## Usage

### Prerequisites
- `glibc 2.33` or higher.
- Titanfall 2 on Steam.

### Manual Installation
1) Download the latest release from the [Releases](https://github.com/cyrv6737/NorthstarProton/releases/tag/latest) page.
2) Extract downloaded release archive to the appropriate directory. 
   * [Native and SteamDeck] `~/.steam/root/compatibilitytools.d`.
   * [Flatpak] `~/.var/app/com.valvesoftware.Steam/data/Steam/compatibilitytools.d/`.
   * Create directory if it does not exist.
3) Restart Steam.

### Enabling

1) Right click Titanfall 2 in your Steam Library
2) Click `Properties`
3) Click the `Compatibility` tab.
4) Tick `Force the use of a specific Steam Play compatibility tool`.
5) Select the installed version of NorthstarProton.

![image](https://user-images.githubusercontent.com/68307100/180291602-a45af9e5-c969-4194-993c-c60ed5ac00e4.png)


### Options

#### LatencyFleX

Once you have installed the vulkan layer properly, LatencyFlex can be enabled by adding `LFX=1 %command%` to your Titanfall 2 Launch Options.

#### DXVK-async

DXVK-async is automatically enabled by default. If you wish to disable it, add `DXVK_ASYNC=0 %command%` to your Titanfall 2 Launch Options.

## Building

This section is for the sake of documentation. Users are not recommended to make their own builds, however nothing is stopping you.

### Requirements:

- A clean and stable building environment that does *not* have Steam installed and has the appropriate glibc version. We are currently targetting whatever SteamOS 3.0 has.
- All depdencies installed. For this an Arch-based environment is recommended. See the proton-tkg PKGBUILD for a complete list of dependencies.

```shell
git clone https://github.com/cyrv6737/NorthstarProton.git
cd NorthstarProton
./generate.sh
```

## Why?

- Northstar does not run on any Proton build that is based on Valve's wine base. As such, this build is made with upstream wine-staging.
  - GE-Proton has moved to Valve's wine base for a while now, the only Proton-GE builds that work are pretty old and have been found to be pretty inconsistent.
  - TKG-Proton builds based on wine-staging run Northstar great, however they do not run on SteamDeck since the precompiled builds are done on bleeding-edge glibc.
- Northstar requires `wsock32.dll` to be overridden, this is automatically done via Protonfixes to provide a better end-user experience. A PR has not been made to upstream Protonfixes since Titanfall 2 does not need this override and there may be complications with using it.
- Northstar has native support for LatencyFleX built directly into the client. LFX wine components have been added to this build to significantly cut down on setup steps.
- As with all Respawn games, Titanfall 2 has a *ton* of stuttering until you generate all the shaders. Granted, it's not nearly as bad as Apex, but having DXVK-async enabled out of the gate is a huge improvement.


## Credits

**Etienne Juvigny ([TK-Glitch](https://github.com/Tk-Glitch))**, for his constant work on the proton-tkg build system.

**Tatsuyuki Ishi ([ishitatsuyuki](https://github.com/ishitatsuyuki))**, for LatencyFleX.

**Amine Hassane ([Sporif](https://github.com/Sporif))**, for continually maintaining DXVK-async.

**Chris Simons ([simons-public](https://github.com/simons-public))** for Protonfixes, which I have shamelessly butchered into this project.

