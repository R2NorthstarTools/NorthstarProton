""" Utilities to make gamefixes easier
"""

import configparser
import os
import sys
import re
import shutil
import signal
import tarfile
import zipfile
import subprocess
import urllib.request
import functools
from .logger import log
from .steamhelper import install_app
from . import config

try:
    import __main__ as protonmain
except ImportError:
    log.warn('Unable to hook into Proton main script environment')

# pylint: disable=unreachable

def which(appname):
    """ Returns the full path of an executable in $PATH
    """

    for path in os.environ['PATH'].split(os.pathsep):
        fullpath = os.path.join(path, appname)
        if os.path.exists(fullpath) and os.access(fullpath, os.X_OK):
            return fullpath
    log.warn(str(appname) + 'not found in $PATH')
    return None


def protondir():
    """ Returns the path to proton
    """

    proton_dir = os.path.dirname(sys.argv[0])
    return proton_dir


def protonprefix():
    """ Returns the wineprefix used by proton
    """

    return os.path.join(
        os.environ['STEAM_COMPAT_DATA_PATH'],
        'pfx/')


def protonnameversion():
    """ Returns the version of proton from sys.argv[0]
    """

    version = re.search('Proton ([0-9]*\\.[0-9]*)', sys.argv[0])
    if version:
        return version.group(1)
    log.warn('Proton version not parsed from command line')
    return None


def protontimeversion():
    """ Returns the version timestamp of proton from the `version` file
    """

    fullpath = os.path.join(protondir(), 'version')
    try:
        with open(fullpath, 'r') as version:
            for timestamp in version.readlines():
                return int(timestamp.strip())
    except OSError:
        log.warn('Proton version file not found in: ' + fullpath)
        return 0
    log.warn('Proton version not parsed from file: ' + fullpath)
    return 0


def protonversion(timestamp=False):
    """ Returns the version of proton
    """

    if timestamp:
        return protontimeversion()
    return protonnameversion()

def once(func=None, retry=None):
    """ Decorator to use on functions which should only run once in a prefix.
    Error handling:
    By default, when an exception occurs in the decorated function, the
    function is not run again. To change that behavior, set retry to True.
    In that case, when an exception occurs during the decorated function,
    the function will be run again the next time the game is started, until
    the function is run successfully.
    Implementation:
    Uses a file (one per function) in PROTONPREFIX/drive_c/protonfixes/run/
    to track if a function has already been run in this prefix.
    """
    if func is None:
        return functools.partial(once, retry=retry)
    retry = retry if retry else False

    #pylint: disable=missing-docstring
    def wrapper(*args, **kwargs):
        func_id = func.__module__ + "." + func.__name__
        prefix = protonprefix()
        directory = os.path.join(prefix, "drive_c/protonfixes/run/")
        file = os.path.join(directory, func_id)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if os.path.exists(file):
            return

        exception = None
        try:
            func(*args, **kwargs)
        except Exception as exc: #pylint: disable=broad-except
            if retry:
                raise exc
            exception = exc

        open(file, 'a').close()

        if exception:
            raise exception #pylint: disable=raising-bad-type

        return
    return wrapper


def _killhanging():
    """ Kills processes that hang when installing winetricks
    """

    # avoiding an external library as proc should be available on linux
    log.debug('Killing hanging wine processes')
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    badexes = ['mscorsvw.exe']
    for pid in pids:
        try:
            with open(os.path.join('/proc', pid, 'cmdline'), 'rb') as proc_cmd:
                cmdline = proc_cmd.read()
                for exe in badexes:
                    if exe in cmdline.decode():
                        os.kill(int(pid), signal.SIGKILL)
        except IOError:
            continue

def _del_syswow64():
    """ Deletes the syswow64 folder
    """

    try:
        shutil.rmtree(os.path.join(protonprefix(), 'drive_c/windows/syswow64'))
    except FileNotFoundError:
        log.warn('The syswow64 folder was not found')

def _mk_syswow64():
    """ Makes the syswow64 folder
    """

    try:
        os.makedirs(os.path.join(protonprefix(), 'drive_c/windows/syswow64'))
    except FileExistsError:
        log.warn('The syswow64 folder already exists')


def _forceinstalled(verb):
    """ Records verb into the winetricks.log.forced file
    """
    forced_log = os.path.join(protonprefix(), 'winetricks.log.forced')
    with open(forced_log, 'a') as forcedlog:
        forcedlog.write(verb + '\n')


def _checkinstalled(verb, logfile='winetricks.log'):
    """ Returns True if the winetricks verb is found in the winetricks log
    """

    if not isinstance(verb, str):
        return False

    winetricks_log = os.path.join(protonprefix(), logfile)

    # Check for 'verb=param' verb types
    if len(verb.split('=')) > 1:
        wt_verb = verb.split('=')[0] + '='
        wt_verb_param = verb.split('=')[1]
        wt_is_set = False
        try:
            with open(winetricks_log, 'r') as tricklog:
                for xline in tricklog.readlines():
                    if re.findall(r'^' + wt_verb, xline.strip()):
                        wt_is_set = bool(xline.strip() == wt_verb + wt_verb_param)
            return wt_is_set
        except OSError:
            return False
    # Check for regular verbs
    try:
        with open(winetricks_log, 'r') as tricklog:
            if verb in reversed([x.strip() for x in tricklog.readlines()]):
                return True
    except OSError:
        return False
    return False


def checkinstalled(verb):
    """ Returns True if the winetricks verb is found in the winetricks log
        or in the 'winetricks.log.forced' file
    """

    log.info('Checking if winetricks ' + verb + ' is installed')
    if _checkinstalled(verb, 'winetricks.log.forced'):
        return True
    return _checkinstalled(verb)


def is_custom_verb(verb):
    """ Returns path to custom winetricks verb, if found
    """

    verb_name = verb + '.verb'
    verb_dir = 'verbs'

    # check local custom verbs
    verbpath = os.path.expanduser('~/.config/protonfixes/localfixes/' + verb_dir)
    if os.path.isfile(os.path.join(verbpath, verb_name)):
        log.debug('Using local custom winetricks verb from: ' + verbpath)
        return os.path.join(verbpath, verb_name)

    # check custom verbs
    verbpath = os.path.join(os.path.dirname(__file__), 'gamefixes', verb_dir)
    if os.path.isfile(os.path.join(verbpath, verb_name)):
        log.debug('Using custom winetricks verb from: ' + verbpath)
        return os.path.join(verbpath, verb_name)

    return False


def protontricks(verb):
    """ Runs winetricks if available
    """

    if not checkinstalled(verb):
        log.info('Installing winetricks ' + verb)
        env = dict(protonmain.g_session.env)
        env['WINEPREFIX'] = protonprefix()
        env['WINE'] = protonmain.g_proton.wine_bin
        env['WINELOADER'] = protonmain.g_proton.wine_bin
        env['WINESERVER'] = protonmain.g_proton.wineserver_bin
        env['WINETRICKS_LATEST_VERSION_CHECK'] = 'disabled'
        env['LD_PRELOAD'] = ''
        
        winetricks_bin = os.path.abspath(__file__).replace('util.py','winetricks')
        winetricks_cmd = [winetricks_bin, '--unattended'] + verb.split(' ')

        # check is verb a custom winetricks verb
        custom_verb = is_custom_verb(verb)
        if custom_verb:
            winetricks_cmd = [winetricks_bin, '--unattended', custom_verb]

        if winetricks_bin is None:
            log.warn('No winetricks was found in $PATH')

        if winetricks_bin is not None:

            log.debug('Using winetricks command: ' + str(winetricks_cmd))

            # make sure proton waits for winetricks to finish
            for idx, arg in enumerate(sys.argv):
                if 'waitforexitandrun' not in arg:
                    sys.argv[idx] = arg.replace('run', 'waitforexitandrun')
                    log.debug(str(sys.argv))

            log.info('Using winetricks verb ' + verb)
            subprocess.call([env['WINESERVER'], '-w'], env=env)
            process = subprocess.Popen(winetricks_cmd, env=env)
            process.wait()
            _killhanging()

            # Check if verb recorded to winetricks log
            if not checkinstalled(verb):
                log.warn('Not recorded as installed: winetricks ' + verb + ', forcing!')
                _forceinstalled(verb)

            log.info('Winetricks complete')
            return True

    return False

def protontricks_proton_5(verb):
    """ Game installation path
    """
    if not checkinstalled(verb):
        try:
            shutil.rmtree(protonprefix())
        except FileNotFoundError:
            log.warn('The protonprefix folder was not found')

        log.info('Folder Proton 5.0' + str(os.path.join(os.environ['STEAM_COMPAT_DATA_PATH'],'..','..','common','Proton 5.0')))
        env = dict(protonmain.g_session.env)
        env['WINEPREFIX'] = protonprefix()
        env['WINE'] = os.path.join(os.environ['STEAM_COMPAT_DATA_PATH'],'..','..','common','Proton 5.0','dist','bin','wine')
        env['WINELOADER'] = os.path.join(os.environ['STEAM_COMPAT_DATA_PATH'],'..','..','common','Proton 5.0','dist','bin','wine')
        env['WINESERVER'] = os.path.join(os.environ['STEAM_COMPAT_DATA_PATH'],'..','..','common','Proton 5.0','dist','bin','wineserver')
        env['WINEPATH'] = os.path.join(os.environ['STEAM_COMPAT_DATA_PATH'],'..','..','common','Proton 5.0','dist','bin','wine64')
        env['WINETRICKS_LATEST_VERSION_CHECK'] = 'disabled'
        env['LD_PRELOAD'] = ''
        winetricks_bin = os.path.abspath(__file__).replace('util.py','winetricks')
        winetricks_cmd = [winetricks_bin, '--unattended', '--force'] + verb.split(' ')
        

        process = subprocess.Popen(winetricks_cmd, env=env)
        process.wait()

def regedit_add(folder,name=None,type=None,value=None,arch=None):
    """ Add regedit keys
    """

    env = dict(protonmain.g_session.env)
    env['WINEPREFIX'] = protonprefix()
    env['WINE'] = protonmain.g_proton.wine_bin
    env['WINELOADER'] = protonmain.g_proton.wine_bin
    env['WINESERVER'] = protonmain.g_proton.wineserver_bin
    
    if name is not None and type is not None and value is not None:

        # Flag for if we want to force writing to the 64-bit registry sector
        if arch is not None:
            regedit_cmd = ['wine', 'reg' , 'add', folder, '/f', '/v', name, '/t', type, '/d', value, '/reg:64']
        else:
            regedit_cmd = ['wine', 'reg' , 'add', folder, '/f', '/v', name, '/t', type, '/d', value]

        log.info('Adding key: ' + folder)

    else:

        # Flag for if we want to force writing to the 64-bit registry sector
        # We use name here because without the other flags we can't use the arch flag
        if name is not None:
            regedit_cmd = ['wine', 'reg' , 'add', folder, '/f', '/reg:64']
        else:
            regedit_cmd = ['wine', 'reg' , 'add', folder, '/f']

        log.info('Adding key: ' + folder)

    process = subprocess.Popen(regedit_cmd, env=env)
    process.wait()

def replace_command(orig_str, repl_str):
    """ Make a commandline replacement in sys.argv
    """

    log.info('Changing ' + orig_str + ' to ' + repl_str)
    for idx, arg in enumerate(sys.argv):
        if orig_str in arg:
            sys.argv[idx] = arg.replace(orig_str, repl_str)

def append_argument(argument):
    """ Append an argument to sys.argv
    """

    log.info('Adding argument ' + argument)
    sys.argv.append(argument)
    log.debug('New commandline: ' + str(sys.argv))

def set_environment(envvar, value):
    """ Add or override an environment value
    """

    log.info('Adding env: ' + envvar + '=' + value)
    os.environ[envvar] = value
    protonmain.g_session.env[envvar] = value

def del_environment(envvar):
    """ Remove an environment variable
    """

    log.info('Removing env: ' + envvar)
    if envvar in os.environ:
        del os.environ[envvar]
    if envvar in protonmain.g_session.env:
        del protonmain.g_session.env[envvar]

def get_game_install_path():
    """ Game installation path
    """

    log.debug('Detected path to game: ' + os.environ['PWD'])
    # only for `waitforexitandrun` command
    return os.environ['PWD']

def winedll_override(dll, dtype):
    """ Add WINE dll override
    """

    log.info('Overriding ' + dll + '.dll = ' + dtype)
    protonmain.g_session.dlloverrides[dll] = dtype

def disable_nvapi():
    """ Disable WINE nv* dlls
    """

    log.info('Disabling NvAPI')
    winedll_override('nvapi', '')
    winedll_override('nvapi64', '')
    winedll_override('nvcuda', '')
    winedll_override('nvcuvid', '')
    winedll_override('nvencodeapi', '')
    winedll_override('nvencodeapi64', '')

def disable_dxvk():  # pylint: disable=missing-docstring
    set_environment('PROTON_USE_WINED3D', '1')

def enable_dxvk_async():  # pylint: disable=missing-docstring
    set_environment('DXVK_ASYNC', '1')

def disable_esync():  # pylint: disable=missing-docstring
    set_environment('PROTON_NO_ESYNC', '1')

def disable_fsync(): # pylint: disable=missing-docstring
    set_environment('PROTON_NO_FSYNC', '1')

def force_lgadd(): # pylint: disable=missing-docstring
    set_environment('PROTON_FORCE_LARGE_ADDRESS_AWARE', '1')

def use_seccomp(): # pylint: disable=missing-docstring
    set_environment('PROTON_USE_SECCOMP', '1')

@once
def disable_uplay_overlay():
    """Disables the UPlay in-game overlay.
    Creates or appends the UPlay settings.yml file
    with the correct setting to disable the overlay.
    UPlay will overwrite settings.yml on launch, but keep
    this setting.
    """
    config_dir = os.path.join(
        protonprefix(),
        'drive_c/users/steamuser/Local Settings/Application Data/Ubisoft Game Launcher/'
    )

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    config_file = os.path.join(config_dir, 'settings.yml')

    if not os.path.isdir(config_dir):
        log.warn(
            'Could not disable UPlay overlay: "'
            + config_dir
            + '" does not exist or is not a directory.'
        )
        return

    if not os.path.isfile(config_file):
        f = open(config_file,"w+")
        f.write("\noverlay:\n  enabled: false\n  forceunhookgame: false\n  fps_enabled: false\n  warning_enabled: false\n")
        f.close
        log.info('Disabled UPlay overlay')
    else:
        try:
            with open(config_file, 'a+') as file:
                file.write("\noverlay:\n  enabled: false\n  forceunhookgame: false\n  fps_enabled: false\n  warning_enabled: false\n")
            log.info('Disabled UPlay overlay')
            return
        except OSError as err:
            log.warn('Could not disable UPlay overlay: ' + err.strerror)

def create_dosbox_conf(conf_file, conf_dict):
    """Create DOSBox configuration file.

    DOSBox accepts multiple configuration files passed with -conf
    option;, each subsequent one overwrites settings defined in
    previous files.
    """
    if os.access(conf_file, os.F_OK):
        return
    conf = configparser.ConfigParser()
    conf.read_dict(conf_dict)
    with open(conf_file, 'w') as file:
        conf.write(file)


def _get_config_full_path(cfile, base_path):
    """ Find game's config file
    """

    # Start from 'user'/'game' directories or absolute path
    if base_path == 'user':
        cfg_path = os.path.join(protonprefix(), 'drive_c/users/steamuser/My Documents', cfile)
    else:
        if base_path == 'game':
            cfg_path = os.path.join(get_game_install_path(), cfile)
        else:
            cfg_path = cfile

    if os.path.exists(cfg_path) and os.access(cfg_path, os.F_OK):
        log.debug('Found config file: ' + cfg_path)
        return cfg_path

    log.warn('Config file not found: ' + cfg_path)
    return False

def create_backup_config(cfg_path):
    """ Create backup config file
    """

    # Backup
    if not os.path.exists(cfg_path + '.protonfixes.bak'):
        log.info('Creating backup for config file')
        shutil.copyfile(cfg_path, cfg_path + '.protonfixes.bak')

def set_ini_options(ini_opts, cfile, encoding, base_path='user'):
    """ Edit game's INI config file
    """
    cfg_path = _get_config_full_path(cfile, base_path)
    if not cfg_path:
        return False

    create_backup_config(cfg_path)

    # set options
    conf = configparser.ConfigParser(empty_lines_in_values=True, allow_no_value=True, strict=False)
    conf.optionxform = str

    conf.read(cfg_path,encoding)

    log.info('Addinging INI options into '+cfile+':\n'+ str(ini_opts))
    conf.read_string(ini_opts)

    with open(cfg_path, 'w') as configfile:
        conf.write(configfile)
    return True

def set_xml_options(base_attibutte, xml_line, cfile, base_path='user'):
    """ Edit game's XML config file
    """
    xml_path = _get_config_full_path(cfile, base_path)
    if not xml_path:
        return False

    create_backup_config(xml_path)

    # set options

    base_size = os.path.getsize(xml_path)
    backup_size = os.path.getsize(xml_path + '.protonfixes.bak')

    if base_size == backup_size:
        ConfigFile = open(xml_path, 'r')
        contents = ConfigFile.readlines()
        LINENUM=0
        for line in contents:
            LINENUM+=1
            if base_attibutte in line:
                log.info('Addinging XML options into '+cfile+':\n'+ str(xml_line))
                contents.insert(LINENUM, xml_line + "\n")
        ConfigFile.close()
        ConfigFile = open(xml_path, 'w')
        for eachitem in contents:
            ConfigFile.write(eachitem)
        ConfigFile.close()
        log.info("Config Patch Applied! \n")

def get_resolution():
    """ Returns screen res width, height
    """

    with open('/sys/class/graphics/fb0/virtual_size', 'r') as res:
        screenx, screeny = map(int, res.read().strip('\n').split(','))

        return(screenx,screeny)

def read_dxvk_conf(cfp):
    """ Add fake [DEFAULT] section to dxvk.conf
    """
    yield '['+ configparser.ConfigParser().default_section +']'
    yield from cfp


def set_dxvk_option(opt, val, cfile='/tmp/protonfixes_dxvk.conf'):
    """ Create custom DXVK config file

    See https://github.com/doitsujin/dxvk/wiki/Configuration for details
    """
    conf = configparser.ConfigParser()
    conf.optionxform = str
    section = conf.default_section
    dxvk_conf = os.path.join(get_game_install_path(), 'dxvk.conf')

    conf.read(cfile)

    if not conf.has_option(section, 'session') or conf.getint(section, 'session') != os.getpid():
        log.info('Creating new DXVK config')
        set_environment('DXVK_CONFIG_FILE', cfile)

        conf = configparser.ConfigParser()
        conf.optionxform = str
        conf.set(section, 'session', str(os.getpid()))

        if os.access(dxvk_conf, os.F_OK):
            conf.read_file(read_dxvk_conf(open(dxvk_conf)))
        log.debug(conf.items(section))

    # set option
    log.info('Addinging DXVK option: '+ str(opt) + ' = ' + str(val))
    conf.set(section, opt, str(val))

    with open(cfile, 'w') as configfile:
        conf.write(configfile)

def install_eac_runtime():
    """ Install Proton Easyanticheat Runtime
    """
    install_app(1826330)

def install_battleye_runtime():
    """ Install Proton BattlEye Runtime
    """
    install_app(1161040)

def install_all_from_tgz(url, path=os.getcwd()):
    """ Install all files from a downloaded tar.gz
    """
 
    cache_dir = config.cache_dir
    tgz_file_name = os.path.basename(url)
    tgz_file_path = os.path.join(cache_dir, tgz_file_name)

    if tgz_file_name not in os.listdir(cache_dir):
        log.info('Downloading ' + tgz_file_name)
        urllib.request.urlretrieve(url, tgz_file_path)
    
    with tarfile.open(tgz_file_path, 'r:gz') as tgz_obj:
        log.info('Extracting ' + tgz_file_name + ' to ' + path)
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tgz_obj, path)
    
def install_from_zip(url, filename, path=os.getcwd()):
    """ Install a file from a downloaded zip
    """

    if filename in os.listdir(path):
        log.info('File ' + filename + ' found in ' + path)
        return

    cache_dir = config.cache_dir
    zip_file_name = os.path.basename(url)
    zip_file_path = os.path.join(cache_dir, zip_file_name)

    if zip_file_name not in os.listdir(cache_dir):
        log.info('Downloading ' + filename + ' to ' + zip_file_path)
        urllib.request.urlretrieve(url, zip_file_path)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_obj:
        log.info('Extracting ' + filename + ' to ' + path)
        zip_obj.extract(filename, path=path)
