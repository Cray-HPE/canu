#!/usr/bin/env sh
# MIT License
#
# (C) Copyright 2022-2025 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

It 'cache generate --help'
  When call canu generate --help
  The lines of stdout should equal 10
  The line 1 of stdout should equal 'Usage: canu generate [OPTIONS] COMMAND [ARGS]...'
End

It 'cache generate network --help'
  When call canu generate network --help
  The lines of stdout should equal 9
  The line 1 of stdout should equal 'Usage: canu generate network [OPTIONS] COMMAND [ARGS]...'
End

It 'cache generate network config --help'
  When call canu generate network config --help
  The lines of stdout should equal 82
  The line 1 of stdout should equal 'Usage: canu generate network config [OPTIONS]'
End

It 'cache generate switch --help'
  When call canu generate switch --help
  The lines of stdout should equal 9
  The line 1 of stdout should equal 'Usage: canu generate switch [OPTIONS] COMMAND [ARGS]...'
End

It 'cache generate switch config --help'
  When call canu generate switch config --help
  The lines of stdout should equal 85
  The line 1 of stdout should equal 'Usage: canu generate switch config [OPTIONS]'
End
