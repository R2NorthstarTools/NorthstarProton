""" Custom Gamefix for Northstar
"""

from protonfixes import util

def main():

    util.set_environment('WINEDLLOVERRIDES','wsock32=n,b')
    util.protontricks('liberation')
    util.protontricks('d3dcompiler_47')
