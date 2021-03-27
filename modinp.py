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
    epilog="When applies, option values should be given as OPTION=VALUE."
)
parser.add_argument(
    "files",
    nargs="+",
    help="input files that will be changed."
)
parser.add_argument(
    "-d", 
    "--delete",
    nargs="+",
    default=[],
    help="keywords to be deleted from the input file."
)
parser.add_argument(
    "-c", 
    "--change", 
    nargs="+",
    default=[],
    help="keyword to be changed, followed by the new options"
)
parser.add_argument(
    "-a", 
    "--add", 
    nargs="+",
    default=[],
    help="keyword to be added, followed by its options."
)
parser.add_argument(
    "-o", 
    "--outputs", 
    nargs="+",
    default=[],
    help="output names for the modified inputs."
)


# Get arguments and check if they are consistent
args = parser.parse_args()

file_names = args.files
output_names = args.outputs

nfiles = len(file_names)
noutputs = len(output_names)

if noutputs > 0:
    assert(nfiles == noutputs), "Number of input/output files are not the same"
    output_to_screen = False
else:
    output_to_screen = True

# Prepare lists of keywords
kw_delete = [d.upper() for d in args.delete]
kw_change = [c.upper() for c in args.change]
kw_add = [a.upper() for a in args.add]
    
for i in range(nfiles):
    with open(args.files[i]) as my_input:
        for line in my_input.readlines():
            line_up = line.upper()
            first = line_up.split()[0]

            if first == "#":
                new_line = line_up
            elif first in kw_del:
                continue
            elif first == kw_chg[0]:
                kw = kw_change[0]
                new_line = " ".join(kw_chg)
                new_line +="\n"
            else:
                new_line = line_up

            if not output_to_screen: 
                with open(outputs[i], "a") as f: f.write(new_line)
            else:
                print(new_line[0:-1])
