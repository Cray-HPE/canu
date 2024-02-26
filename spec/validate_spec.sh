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

It 'validate --help'
  When call canu validate --help
  The lines of stdout should equal 14
  The line 1 of stdout should equal 'Usage: canu validate [OPTIONS] COMMAND [ARGS]...'
End

It 'validate network --help'
  When call canu validate network --help
  The lines of stdout should equal 10
  The line 1 of stdout should equal 'Usage: canu validate network [OPTIONS] COMMAND [ARGS]...'
End

It 'validate network bgp --help'
  When call canu validate network bgp --help
  The lines of stdout should equal 28
  The line 1 of stdout should equal 'Usage: canu validate network bgp [OPTIONS]'
End

It 'validate network cabling --help'
  When call canu validate network cabling --help
  The lines of stdout should equal 28
  The line 1 of stdout should equal 'Usage: canu validate network cabling [OPTIONS]'
End

It 'validate paddle --help'
  When call canu validate paddle --help
  The lines of stdout should equal 15
  The line 1 of stdout should equal 'Usage: canu validate paddle [OPTIONS]'
End

It 'validate paddle-cabling --help'
  When call canu validate paddle-cabling --help
  The lines of stdout should equal 28
  The line 1 of stdout should equal 'Usage: canu validate paddle-cabling [OPTIONS]'
End

It 'validate shcd --help'
  When call canu validate shcd --help
  The lines of stdout should equal 33
  The line 1 of stdout should equal 'Usage: canu validate shcd [OPTIONS]'
End

It 'validate shcd-cabling --help'
  When call canu validate shcd-cabling --help
  The lines of stdout should equal 34
  The line 1 of stdout should equal 'Usage: canu validate shcd-cabling [OPTIONS]'
End

It 'validate switch --help'
  When call canu validate switch --help
  The lines of stdout should equal 9
  The line 1 of stdout should equal 'Usage: canu validate switch [OPTIONS] COMMAND [ARGS]...'
End

It 'validate switch config --help'
  When call canu validate switch config --help
  The lines of stdout should equal 47
  The line 1 of stdout should equal 'Usage: canu validate switch config [OPTIONS]'
End
