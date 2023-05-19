#!/usr/bin/env sh
# MIT License
#
# (C) Copyright 2023 Hewlett Packard Enterprise Development LP
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

It 'cache report --help'
  When call canu report --help
  The lines of stdout should equal 10
  The line 1 of stdout should equal 'Usage: canu report [OPTIONS] COMMAND [ARGS]...'
End

It 'cache report network --help'
  When call canu report network --help
  The lines of stdout should equal 11
  The line 1 of stdout should equal 'Usage: canu report network [OPTIONS] COMMAND [ARGS]...'
End

It 'cache report network cabling --help'
  When call canu report network cabling --help
  The lines of stdout should equal 62
  The line 1 of stdout should equal 'Usage: canu report network cabling [OPTIONS]'
End

It 'cache report network firmware --help'
  When call canu report network firmware --help
  The lines of stdout should equal 37
  The line 1 of stdout should equal 'Usage: canu report network firmware [OPTIONS]'
End

It 'cache report network version --help'
  When call canu report network version --help
  The lines of stdout should equal 18
  The line 1 of stdout should equal 'Usage: canu report network version [OPTIONS]'
End

It 'cache report switch --help'
  When call canu report switch --help
  The lines of stdout should equal 10
  The line 1 of stdout should equal 'Usage: canu report switch [OPTIONS] COMMAND [ARGS]...'
End

It 'cache report switch cabling --help'
  When call canu report switch cabling --help
  The lines of stdout should equal 32
  The line 1 of stdout should equal 'Usage: canu report switch cabling [OPTIONS]'
End

It 'cache report switch firmware --help'
  When call canu report switch firmware --help
  The lines of stdout should equal 22
  The line 1 of stdout should equal 'Usage: canu report switch firmware [OPTIONS]'
End
