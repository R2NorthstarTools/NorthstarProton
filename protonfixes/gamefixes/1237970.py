""" Custom Gamefix for Northstar
"""
#pylint: disable=C0103

from protonfixes import util

def main():
    """
    """
    
    #installs d3dcompiler_47 to make EA App render the GUI
    util.set_environment('WINEDLLOVERRIDES','wsock32=n,b')
    util.protontricks('d3dcompiler_47')
    util.protontricks('liberation')
