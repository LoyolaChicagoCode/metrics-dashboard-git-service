# -*- coding: utf-8 -*-
#
# Copyright 2010-2014 The pygit2 contributors
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# In addition to the permissions in the GNU General Public License,
# the authors give you unlimited permission to link the compiled
# version of this file into combinations with other programs,
# and to distribute those combinations without any restriction
# coming from the use of this file.  (The General Public License
# restrictions do apply in other respects; for example, they cover
# modification of the file, and distribution when not linked into
# a combined executable.)
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

# Import from the future
from __future__ import absolute_import

# Import from the Standard Library
import inspect
import codecs
from os import path, getenv

# Import from cffi
from cffi import FFI



ffi = FFI()


dir_path = path.dirname(path.abspath(inspect.getfile(inspect.currentframe())))

decl_path = path.join(dir_path, 'decl.h')
with codecs.open(decl_path, 'r', 'utf-8') as header:
    ffi.cdef(header.read())

# if LIBGIT2 exists, set build and link against that version
libgit2_path = getenv('LIBGIT2')
if not libgit2_path:
    libgit2_path = '/usr/local'

include_dirs = [path.join(libgit2_path, 'include')]
library_dirs = [path.join(libgit2_path, 'lib')]

C = ffi.verify("#include <git2.h>", libraries=["git2"],
               include_dirs=include_dirs, library_dirs=library_dirs)
