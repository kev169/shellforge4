#! /usr/bin/env python

#############################################################################
##                                                                         ##
## gensflib.py --- SFLib generator                                         ##
##                 see http://secdev.org/projects/sflib.html               ##
##                 for more informations                                   ##
##                                                                         ##
## Copyright (C) 2004  Philippe Biondi <biondi@cartel-securite.fr>         ##
##                                                                         ##
## This program is free software; you can redistribute it and/or modify it ##
## under the terms of the GNU General Public License as published by the   ##
## Free Software Foundation; either version 2, or (at your option) any     ##
## later version.                                                          ##
##                                                                         ##
## This program is distributed in the hope that it will be useful, but     ##
## WITHOUT ANY WARRANTY; without even the implied warranty of              ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU       ##
## General Public License for more details.                                ##
##                                                                         ##
#############################################################################

# $Id$



import getopt,sys,os,time,re

arch = [ ("linux_i386", "Linux/i386"),
         ("linux_amd64", "Linux/amd64"),
         ("linux_alpha", "Linux/Alpha"),
         ("linux_arm", "Linux/ARM"),
         ("linux_m68k", "Linux/Motorla 68000"),
         ("linux_sparc", "Linux/Sparc"),
         ("linux_mips", "Linux/MIPS"),
         ("linux_mipsel", "Linux/MIPSel"),
         ("linux_powerpc", "Linux/PowerPC"),
         ("linux_hppa", "Linux/PA-RISC"),
         ("macos_powerpc", "MacOS/PowerPC"),
         ("freebsd_i386", "FreeBSD/i386"),
         ("openbsd_i386", "OpenBSD/i386"),
         ("solaris_sparc", "Solaris/Sparc"),
         ("hpux_hppa", "HPUX/PA-RISC"),
         ("linux_ia64", "Linux/IA64"),
         ]

verbose=0
def dbg(x):
    if verbose:
        print x

def gen_sflib(source,dest):
    if source:
        source += "/"
    if dest:
        dest += "/"
    dest += "sflib/"

    GPL_header = open(source+"common/GPL_header.h").read()

    def write_header(f,title):
        f.write(GPL_header % title)
        f.write("""
/*
 * Automatically generated by gensflib.py 
 * %s
 */
""" % time.ctime())

    re_sysnr = re.compile(r'^\s*#define\s+__[A-Z]+_([a-z][a-zA-Z0-9_]+)')
    re_sysname = re.compile(r'.*_sfsyscall[0-9]\([A-Za-z0-9_ *]+,\s*([a-zA-Z0-9_]+)')

    # Read prototypes
    sysproto={}
    f = open(source+"common/sysproto.h")
    for l in f.readlines():
        m = re_sysname.match(l)
        if m:
            sysproto[m.groups()[0]] = l
    

    try:
        os.mkdir(dest)
    except OSError:
        pass
    try:
        os.mkdir(dest+"common")
    except OSError:
        pass
    open(dest+"common/sftypes.h","w").write(open(source+"common/sftypes.h").read())
    open(dest+"common/sfsocketcall.h","w").write(open(source+"common/sfsocketcall.h").read())


    for arch_dir,arch_name in arch:
        try:
            os.mkdir(dest+arch_dir)
        except OSError:
            pass

        sysnr = open(source+arch_dir+"/sysnr.h").read()
        syslist = []
        for l in sysnr.splitlines():
            m = re_sysnr.match(l)
            if m:
                syslist.append(m.groups()[0])
		dbg("%s: got %s"%(arch_dir,m.groups()[0]))
        

        # Create sflib.h
        lib = ''
        for s in syslist:
            lib += sysproto.get(s, "// %s\n"%s)
	    dbg("%s: added %s"% (arch_dir, s))

        prologue = ""
        before = ""
        after = ""
        if os.access(source+arch_dir+"/lib.h",os.R_OK):
            before = open(source+arch_dir+"/lib.h").read()
            p = before.find("[INCLUDES]")
            if p >= 0:
                prologue = before[:p]
                before = before[p+11:]
            p = before.find("[SFLIB]")
            if p >= 0:
                after = before[p+7:]
                before = before[:p]


        f = open(dest+arch_dir+"/sflib.h","w")
        write_header(f,"sflib.h --- SFLib syscall library for %s" % arch_name)
        f.write("""
#ifndef SFLIB_H
#define SFLIB_H

""")
        f.write(prologue)
        f.write("""
#include "sfsysnr.h"
#include "sfsyscall.h"
#include "../common/sftypes.h"
        
""")

        f.write(before)
        f.write(lib)
        f.write(after)
        
        f.write("""
#endif /* SFLIB_H */
""")
        f.close()

        # Create sfsysnr.h
        f = open(dest+arch_dir+"/sfsysnr.h","w")
        write_header(f,"sfsysnr.h --- SFLib syscall numbers for %s" % arch_name)
        f.write("""
#ifndef SFSYSNR_H
#define SFSYSNR_H
        
""")
        f.write(sysnr)
        f.write("""
#endif /* SFSYSNR_H */
""")
        f.close()

        # Create sfsyscall
        f = open(dest+arch_dir+"/sfsyscall.h","w")
        write_header(f,"sfsyscall.h --- SFLib syscall macros for %s" % arch_name)
        f.write("""
#ifndef SFSYSCALL_H
#define SFSYSCALL_H
        
""")
        f.write(open(source+arch_dir+"/syscall.h").read())
        f.write("""
#endif /* SFSYSCALL_H */
""")
        f.close()
         







def usage():
    print "Syntax: gensflib.py -d sflib_destination"

def error(x,printusage=0):
    print >>sys.stderr, "Error:%s"%x
    if printusage:
        usage()
    raise SystemExit


source = ""
dest = ""

try:
    opts=getopt.getopt(sys.argv[1:], "s:d:hv")
    for opt,optarg in opts[0]:
        if opt == "-h":
            usage()
            raise SystemExit
        if opt == "-s":
            source = optarg
        if opt == "-v":
            verbose += 1
        if opt == "-d":
            dest = optarg
except getopt.GetoptError,msg:
    error(msg, printusage=1)
#except SystemExit:
#    sys.exit(0);
#except:
#    error("parsing arguments", printusage=1);


gen_sflib(source,dest)
    