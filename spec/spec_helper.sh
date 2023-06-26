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

# shellcheck shell=sh

# Defining variables and functions here will affect all specfiles.
# Change shell options inside a function may cause different behavior,
# so it is better to set them here.
# set -eu

# This callback function will be invoked only once before loading specfiles.
spec_helper_precheck() {
  # Available functions: info, warn, error, abort, setenv, unsetenv
  # Available variables: VERSION, SHELL_TYPE, SHELL_VERSION
  : minimum_version "0.28.1"
}

# This callback function will be invoked after a specfile has been loaded.
spec_helper_loaded() {
  :
}

# This callback function will be invoked after core modules has been loaded.
spec_helper_configure() {
  # Available functions: import, before_each, after_each, before_all, after_all
  : import 'support/custom_matcher'
}

# Custom matcher used to find a string inside of a text containing ANSI escape codes.
# https://github.com/shellspec/shellspec/issues/278
match_colored_text() {
	# Source: https://unix.stackexchange.com/a/18979/348102
	sanitized_text="$(echo "${match_colored_text:?}" | perl -e '
		while (<>) {
			s/ \e[ #%()*+\-.\/]. |
				\r | # Remove extra carriage returns also
				(?:\e\[|\x9b) [ -?]* [@-~] | # CSI ... Cmd
				(?:\e\]|\x9d) .*? (?:\e\\|[\a\x9c]) | # OSC ... (ST|BEL)
				(?:\e[P^_]|[\x90\x9e\x9f]) .*? (?:\e\\|\x9c) | # (DCS|PM|APC) ... ST
				\e.|[\x80-\x9f] //xg;
				1 while s/[^\b][\b]//g;  # remove all non-backspace followed by backspace
			print;
		}
	')"
	echo "${sanitized_text}" | grep -q "$1"
}

# Custom matcher used to find a string inside of a text containing ANSI escape codes.
match_rich_text() {
	if [ -z "${1}" ]; then
		printf "ERROR: You cannot pass an empty string!\n" >&2;
		return 1;
	fi
	
	# shellcheck disable=SC2059
	rich_search_term="$(printf "$1")"
	match="$(echo "${match_rich_text:-}" | perl -ne "print if /\Q${rich_search_term}/")"

	[ -n "${match}" ]
}
