#!/usr/bin/python
#!encoding: utf-8

import argparse

# Modify input file by adding, deleting or changing keyword options
# from the command line.
# ---------------------------------------------------------------------


# Command line parser
parser = argparse.ArgumentParser(
    prog="modinp.py",
    description="Modify input file keywords.",
    epilog="For readability, option values should be given as OPTION=VALUE."
)
parser.add_argument(
    "file",
    nargs=1,
    help="input file that will be changed"
)
parser.add_argument(
    "-d", 
    "--delete",
    nargs="+",
    default=[],
    help="keywords to be deleted from the input file"
)
parser.add_argument(
    "-c", 
    "--change", 
    nargs="+",
    default=[],
    action="append",
    help="keyword to be changed, followed by the new options"
)
parser.add_argument(
    "-a", 
    "--add", 
    nargs="+",
    default=[],
    help="keyword to be added, followed by its options"
)
parser.add_argument(
    "-o", 
    "--output", 
    nargs=1,
    default=None,
    help="output name for the modified input"
)

args = parser.parse_args()

file_name = args.file[0]

if args.output is None:
    output_to_screen = True
else:
    output_to_screen = False
    output_name = args.output[0]
    f = open(output_name, "w")
    f.close()

kw_del = [d.upper() for d in args.delete]

# Keywords to be changed
kw_chg_keys = []
kw_chg_dict = {}
for c in args.change:
    upper_c = [x.upper() for x in c]
    key, *value = upper_c
    kw_chg_keys.append(key)
    kw_chg_dict[key] = value

# Keywords to be added
kw_add_keys = []
kw_add_dict = {}
for c in args.add:
    upper_c = [x.upper() for x in c]
    key, *value = upper_c
    kw_add_keys.append(key)
    kw_add_vals[key] = value

found_kw = []

# Process file
with open(file_name) as my_input:
    lines = my_input.readlines()

for line in lines:
    line_up = line.upper()
    first = line_up.split()[0]

    if first == "#":
        new_line = line_up
    elif first in kw_del:
        continue
    elif first in kw_chg_keys:
        options = " ".join(kw_chg_dict[first])
        new_line = first + " " + options + "\n"
    else:
        new_line = line_up

    if not output_to_screen: 
        with open(output_name, "a") as f: f.write(new_line)
    else:
        print(new_line[0:-1])
