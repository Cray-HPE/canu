#!/usr/bin/env python3
"""
This script is designed to automate the process of adding new subrack devices to
a misformated SHCD file.  It is under-developed, but could be expanded to handle
more complex patterns with a little bit of love.
"""
import csv
import re
import argparse
from collections import Counter

def check_pattern(row: dict[str, str]) -> bool:
    """
    Check if the 'Subrack' column matches the pattern 'L', 'R', 'l', or 'r'.
    This column is in the HMN tab and usualy has a blank header.  During the
    copy/paste process, the blank column should be renamed to 'Subrack'.

    Args:
        row (dict): A dictionary representing a row in the CSV file

    Returns:
        bool: True if the pattern matches, False otherwise
    """
    # Define a regex pattern to match 'L', 'R', 'l', or 'r'
    # this may need to be expanded to include other patterns depending upon
    # the SHCD as they are all non-standard
    pattern = re.compile(r'[LlRr]')
    # Check if the intermediate 'Subrack' column matches the pattern
    return bool(pattern.search(row['Subrack']))

def extract_numeric_value(s: str) -> int:
    """
    This function extracts the numeric part from a string and converts it to an 
    integer.

    Args:
        s (str): A string containing a numeric part
    
    Returns:
        int: The numeric part extracted from the string
    """
    # Extract the numeric part from the string and convert it to an integer
    return int(re.search(r'\d+', s).group())

def find_lowest_values(rows, field) -> str:
    """
    Find the lowest numeric value in the specified field from a list of rows.

    Args:
        rows (list): A list of dictionaries representing rows in the CSV file
        field (str): The field to extract numeric values from

    Returns:
        str: The lowest value in the specified field
    """
    # Extract numeric values from the specified field and find the minimum
    return min(rows, key=lambda row: extract_numeric_value(row[field]))[field]

def rename_duplicate_columns(fieldnames):
    """
    Rename duplicate columns in the CSV file by appending a number to the column
    name.  Because the SHCD is non-standard, it is common to have duplicates.
    For example, the HMN tab has source and destination information, but they
    use the same header name.  If you try to edit a row in code, it puts the
    value in every column with a matching header, so when the code runs, it
    renames them so they are unique and data can be added to the right places.
    """
    counts = Counter(fieldnames)
    new_fieldnames = []
    seen = {}
    for name in fieldnames:
        # if the header is not unique, create a new header
        if counts[name] > 1:
            if name not in seen:
                seen[name] = 0
            seen[name] += 1
            new_fieldname = f"{name}_{seen[name]}"
        else:
            new_fieldname = name
        new_fieldnames.append(new_fieldname)
    return new_fieldnames

def modify_and_insert_rows(input_file, output_file) -> None:
    """
    This loops through each row, looks for patterns, and adds new subracks.
    It creates a new parent device if it finds four consecutive matches and will
    increment the device name.  It also sets the 'Subrack' column to the new
    device's name.
    
    This is currently designed to match dense 4 node blades, so adjustments may 
    need to be configured for 2-node blades or other patterns.  This was an 
    ad-hoc script to automate a painful process, so it is not very flexible ATM.

    Args:
        input_file (str): The path to the input CSV file
        output_file (str): The path to the output CSV file

    Returns:
        None
    """
    with open(input_file, mode='r', newline='', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile, delimiter=',')
        original_fieldnames = next(reader)
        fieldnames = rename_duplicate_columns(original_fieldnames)
        
        # Open the output file in write mode to write the headers
        with open(output_file, mode='w', newline='', encoding='utf-8-sig') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=',')
            writer.writeheader()  # Write the header once

            # start the counters
            consecutive_matches = 0
            subrack_counter = 1
            matched_rows = []

            # loop through each row in the input file
            for row_number, row in enumerate(reader, start=1):
                row_dict = dict(zip(fieldnames, row))
                # Check if the pattern matches
                if check_pattern(row_dict):
                    # Increment the counter if the pattern matches
                    consecutive_matches += 1
                    # Append the matched row to the list
                    matched_rows.append(row_dict)
                    # once four consecutive matches are found, create a new parent device
                    # change this to 2 for 2-node blades or other patterns
                    if consecutive_matches == 4:
                        # Generate the incremented string
                        subrack_string = f"SubRack-{subrack_counter:03d}-CMC"
                        subrack_counter += 1
                        # Find the lowest values in Rack_1 and Location_1 fields
                        # the new parent device needs a u in the location column
                        lowest_rack_1 = find_lowest_values(matched_rows, 'Rack_1')
                        lowest_location_1 = find_lowest_values(matched_rows, 'Location_1')
                        print(f"Lowest Rack_1: {lowest_rack_1}, Lowest Location_1: {lowest_location_1}")
                        # Update the Parent column for the four matched rows
                        for matched_row in matched_rows:
                            matched_row['Parent'] = subrack_string
                            writer.writerow(matched_row)
                            print(f"Updated {matched_row['Source']} with new Parent: {subrack_string}")
                        # Add a new row after four consecutive matches are found
                        # without the rename_duplicate_columns, the values would be written to the wrong columns
                        new_row = {"Source": subrack_string, 
                                   "Rack_1": lowest_rack_1, 
                                   "Location_1": lowest_location_1,
                                   "Destination": "NONE", 
                                   "Rack_2": "NONE", 
                                   "Location_2": "NONE",
                                   "-": "-",
                                   "Port_2": "0",} 
                        writer.writerow(new_row)
                        print(f"Added new parent device: {new_row}")
                        consecutive_matches = 0  # Reset the counter
                        matched_rows = []  # Clear the matched rows list
                else:
                    consecutive_matches = 0  # Reset the counter if the pattern does not match
                    matched_rows = []  # Clear the matched rows list
                    # Write the current row to the output file
                    writer.writerow(row_dict)

# Usage
if __name__ == "__main__":
    # attempt to provide a quick help to anyone attempting to use the script
    parser = argparse.ArgumentParser(description="Adds missing subracks devices to the HMN data if reasonably formatted with four consecutive entries with 'L' or 'R' in the blank 'Subrack' column and a '-' in the other blank column.")
    parser.add_argument("input_file", help="Path to the input CSV file (copy from HMN tab, rename blank column to 'Subrack')")
    parser.add_argument("output_file", help="Path to the output CSV file (Paste > Paste Special... > Values back into the SHCD)")
    args = parser.parse_args()

    modify_and_insert_rows(args.input_file, args.output_file)
