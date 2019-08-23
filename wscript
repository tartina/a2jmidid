# !/usr/bin/python3
# encoding: utf-8

import os

from waflib import Logs, Options, Task, Utils

APPNAME='a2jmidid'
VERSION='8'

# these variables are mandatory ('/' are converted automatically)
srcdir = '.'
blddir = 'build'

def options(opt):
    opt.load('compiler_c')
    opt.add_option('--enable-pkg-config-dbus-service-dir', action='store_true', default=False, help='force D-Bus service install dir to be one returned by pkg-config')
    opt.add_option('--disable-dbus', action='store_true', default=False, help="Don't enable D-Bus support even if required dependencies are present")
    opt.add_option('--mandir', type='string', help="Manpage directory [Default: <prefix>/share/man]")

def configure(conf):
    conf.load('compiler_c')

    conf.check_cfg(atleast_pkgconfig_version='1.6.0')

    conf.check_cfg(package='alsa', mandatory=True, uselib_store='ALSA', args=['--cflags', '--libs'])
    conf.check_cfg(package='jack', mandatory=True, atleast_version='0.109.0', uselib_store='JACK', args=['--cflags', '--libs'])

    conf.env['DBUS_ENABLED'] = False
    if not Options.options.disable_dbus:
        if conf.check_cfg(package='dbus-1', mandatory=False, uselib_store='DBUS', args=['--cflags', '--libs']):
            conf.env['DBUS_ENABLED'] = True
            conf.check_cfg(package='dbus-1', mandatory=False, uselib_store='DBUS', variables=['session_bus_services_dir'])

    conf.env['LIB_DL'] = ['dl']
    conf.env['LIB_PTHREAD'] = ['pthread']

    conf.check(header_name='getopt.h', features='c cprogram')

    if conf.env['DBUS_ENABLED']:
        if Options.options.enable_pkg_config_dbus_service_dir:
            conf.env['DBUS_SERVICES_DIR'] = conf.env['DBUS_session_bus_services_dir']
        else:
            conf.env['DBUS_SERVICES_DIR'] = os.path.normpath(conf.env['PREFIX'] + '/share/dbus-1/services')

    if Options.options.mandir:
        conf.env['MANDIR'] = Options.options.mandir
    else:
        conf.env['MANDIR'] = conf.env['PREFIX'] + '/share/man'

    conf.define('A2J_VERSION', VERSION)
    conf.write_config_header('config.h')

    version_msg = "a2jmidid-" + VERSION
    conf.msg('Version', version_msg)

    conf.msg('Install prefix', Options.options.prefix)
    conf.msg('D-Bus support', conf.env['DBUS_ENABLED'])

    if conf.env['DBUS_ENABLED']:
        conf.msg('D-Bus service install directory', conf.env['DBUS_SERVICES_DIR'])
        if conf.env['DBUS_SERVICES_DIR'] != conf.env['DBUS_session_bus_services_dir']:
            conf.msg('WARNING: D-Bus session services will be installed in', conf.env['DBUS_SERVICES_DIR'])
            conf.msg('Use --enable-pkg-config-dbus-service-dir to force pkgconfig directory')

def build(bld):

    # Build gitversion if not found
    if not os.access('gitversion.h', os.R_OK):
        def post_run(self):
            sg = Utils.h_file(self.outputs[0].abspath(self.env))
            #print sg.encode('hex')
            Build.bld.node_sigs[self.env.variant()][self.outputs[0].id] = sg

        script = bld.path.find_resource('gitversion_regenerate.sh')
        script = script.abspath()

        bld(
                rule = '%s ${TGT}' % script,
                name = 'gitversion',
                runnable_status = Task.RUN_ME,
                before = 'c',
                color = 'BLUE',
                post_run = post_run,
                source = ['gitversion_regenerate.sh'],
                target = [bld.path.find_or_declare('gitversion.h')]
        )

    prog = bld(features='c cprogram')

    prog.source = [
        'a2jmidid.c',
        'log.c',
        'port.c',
        'port_thread.c',
        'port_hash.c',
        'paths.c',
        'jack.c',
        'list.c',
        ]

    if bld.env['DBUS_ENABLED']:
        prog.source.append('dbus.c')
        prog.source.append('dbus_iface_introspectable.c')
        prog.source.append('dbus_iface_control.c')
        prog.source.append('sigsegv.c')

    prog.target = 'a2jmidid'
    prog.includes = ['.']
    prog.uselib = 'ALSA JACK DL PTHREAD'
    if bld.env['DBUS_ENABLED']:
        prog.uselib += " DBUS"

    prog = bld(features='c cprogram')
    prog.source = 'a2jmidi_bridge.c'
    prog.target = 'a2jmidi_bridge'
    prog.uselib = 'ALSA JACK'

    prog = bld(features='c cprogram')
    prog.source = 'j2amidi_bridge.c'
    prog.target = 'j2amidi_bridge'
    prog.uselib = 'ALSA JACK'

def dist(ctx):
    # This code blindly assumes it is working in the toplevel source directory.
    if not os.path.exists('gitversion.h'):
        os.system('./gitversion_regenerate.sh gitversion.h')
