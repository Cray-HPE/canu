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

Describe 'tests/integration.sh'
  Include tests/integration.sh
    It 'detects canu version prints using docker'
      When call tests/integration.sh -i canu -v latest -a
      The status should equal 0
      The output should include "canu, version "
    End

    It 'detects canu version prints using canud'
      When call tests/integration.sh -i canu -v latest -b
      The status should equal 0
      The output should include "canu, version "
    End

    It 'detects canu validate paddle using docker'
      When call tests/integration.sh -i canu -v latest -c
      The status should equal 0
      # take a sampling of the output expected
      The output should include "09-29==>UNUSED"
      The output should include "4: sw-leaf-003 has the following port usage:"
      The output should include "18==>pdu-x3001-001:bmc:1"
      The output should include "onboard:1==>sw-leaf-bmc-001:27"
    End

    It 'detects canu validate paddle using canud'
      When call tests/integration.sh -i canu -v latest -d
      The status should equal 0
      # take a sampling of the output expected
      The output should include "09-29==>UNUSED"
      The output should include "4: sw-leaf-003 has the following port usage:"
      The output should include "18==>pdu-x3001-001:bmc:1"
      The output should include "onboard:1==>sw-leaf-bmc-001:27"
    End

    It 'detects canu validate shcd tds using docker'
      When call tests/integration.sh -i canu -v latest -e
      The status should equal 0
      # take a sampling of the output expected
      The output should include "6: sw-leaf-bmc-001 connects to 25 nodes: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 18, 17, 19, 20, 21, 22, 18, 1, 0]"
      The output should include "17: lmem001 has the following port usage:"
      The output should include "52==>sw-cdu-001:52"
      The output should include "Cell: P18      Name: SITE"
    End

    It 'detects canu validate shcd tds using canud'
      When call tests/integration.sh -i canu -v latest -f
      The status should equal 0
      # take a sampling of the output expected
      The output should include "6: sw-leaf-bmc-001 connects to 25 nodes: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 18, 17, 19, 20, 21, 22, 18, 1, 0]"
      The output should include "17: lmem001 has the following port usage:"
      The output should include "52==>sw-cdu-001:52"
      The output should include "Cell: P18      Name: SITE"
    End

    It 'detects canu validate shcd full makes a paddle file using docker'
      When call tests/integration.sh -i canu -v latest -g
      The status should equal 0
      Path paddle-file=full_paddle.json
      The path paddle-file should be exist
    End

    It 'detects canu validate shcd full makes a paddle file using canud'
      When call tests/integration.sh -i canu -v latest -j
      The status should equal 0
      Path paddle-file=full_paddle.json
      The path paddle-file should be exist
    End
End

