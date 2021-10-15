# MIT License
#
# (C) Copyright [2021] Hewlett Packard Enterprise Development LP
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

class HmnRow:
    def __init__(self, row):
        """
        Represents a row of the HMN tab in an SHCD.
        """
        # These are the headers we require from the HMN tab
        # Sometimes there are more (see comments above self.source_name)
        self.required_header = [
            "Source",
            "Rack",
            "Location",
            "Slot",
            "Port",
            "Destination",
            "Rack",
            "Location",
            "Port",
        ]

        # The row as a list instead of a tuple
        self.list = list(row)

        # The row number
        self.row = row[0].row

        # By default, these indicies are 0-8, but in reality, 
        # SHCDs often have other columns or columns we don't use
        # But this class takes the approach of the happy path, assuming
        # we have only the correct columns in place
        # It's up to the user to modify these mappings if necessary
        self.source_name = row[0]

        self.source_rack = row[1]

        self.source_loc = row[2]

        self.source_slot = row[3]

        self.source_port = row[4]

        self.dest = row[5]

        self.dest_rack = row[6]

        self.dest_loc = row[7]

        self.dest_port = row[8]

