#!/usr/bin/env python
#
# Copyright 2012 Jim Lawton. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import logging
import optparse

import gdocs

session = None
commands = {}
aliases = {}

def command(func):
    if not func.__doc__:
        sys.exit("Error: commands must have formatted docstrings!")
    commands[func.func_name] = func
    func_aliases = [alias for alias in aliases.iterkeys() if aliases[alias].func_name == func.func_name]
    if func_aliases:
        func.__doc__ += "Aliases: %s" % ",".join(func_aliases)
    return func

def alias(name):
    def decorator(func):
        if name in commands:
            sys.exit("Error, this alias has the same name as a command!")
        aliases[name] = func
        return func
    return decorator

@command
def help(argv):
    """Print help message.
gdrive help [COMMAND]

If no argument is specified, print a list of commands with a short description of each. If a command is specified, print help on that command.
"""
    if not argv:
        return usage()
    for cmd in commands:
        if cmd == argv[0]:
            print commands[cmd].__doc__.split('\n', 1)[1]
            return
    print >>sys.stderr, "Unknown command '%s'" % argv[0]

def usage():
    "Print usage."
    print "Google Drive command-line interface"
    print
    print "Commands:"
    print
    print "Note: use gdrive help <command> to view usage for a specific command."
    print
    lines = []
    cmdlist = commands.keys()
    cmdlist.sort()
    for cmd in cmdlist:
        lines.append((cmd, commands[cmd].__doc__.splitlines()[0]))
    space = max(len(line[0]) + 3 for line in lines)
    for line in lines:
        print " %-*s%s" % (space, line[0], line[1])
    print

@command
def start(argv):
    """Start GDrive daemon.
gdrive start

Starts the GDrive daemon, gdrived, if it is not already running.

"""
    sys.exit("Not implemented!")

@command
def stop(argv):
    """Stop GDrive daemon.
gdrive stop

Stops the GDrive daemon, gdrived, if it is running.

"""
    sys.exit("Not implemented!")

@command
def userinfo(argv):
    """Print user info.
gdrive userinfo

Prints user information on the currently authenticated Google Drive account..

"""
    print session.getUserData()
    
@command
@alias("ls")
def list(argv):
    """List folder contents.
gdrive list <path>

Lists the contents of the specified path. If no path is specified, then the root folder is assumed.

"""
    if len(argv) == 0:
        root = '/'
    else:
        root = argv[0]
    folders, files = session.readFolder(root)
    for path in folders:
        print path
    for path in files:
        print path, session.getFileSize(path)

@command
@alias("up")
def update(argv):
    """Update a folder.
gdrive update <path>

Update the contents of the specified path, recursively. If no path is specified, then the entire GDrive will be updated.

"""
    if len(argv) == 0:
        root = '/'
    else:
        root = argv[0]
    session.update(root)

def _parseArgs():
    "Parse command-line arguments."
    helpStr = """
%prog [options] 

Utility to access Google Drive.

"""
    parser = optparse.OptionParser(description=helpStr)
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False,                   help='Turn on extra logging')
    parser.add_option('-d', '--debug',   dest='debug',   action='store_true', default=False,                   help='Turn on debug logging')
    (options, args) = parser.parse_args()
    return options


def main(argv):
    "Main function."

    opts = _parseArgs()
    if opts.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    elif opts.verbose:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)

    global session
    session = gdocs.DocsSession()
    if session == None:
        sys.exit("Error, could not create Google Docs session!")

    cmdfound = False
    i = 0
    for i in range(len(argv)):
        if argv[i] in commands or argv[i] in aliases:
            cmdfound = True
            break

    if not cmdfound:
        usage()
        return None

    res = None
    if argv[i] in commands:
        res = commands[argv[i]](argv[i+1:])
    elif argv[i] in aliases:
        res = aliases[argv[i]](argv[i+1:])

    return res


if __name__ == "__main__":
    result = main(sys.argv)
    if result != None:
        sys.exit(result)
