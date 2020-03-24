#!/usr/bin/env python
import argparse
import sys
import os
import csv
import pandas as pd


###############################################################
class MAPL_DataSpec:
    """Declare and manipulate an import/export/internal specs for a 
       MAPL Gridded component"""

    all_options = ['short_name', 'long_name', 'units',
                   'dims', 'vlocation', 'num_subtiles',
                   'refresh_interval', 'averaging_interval', 'halowidth',
                   'precision','default','restart', 'ungridded_dims',
                   'field_type', 'staggering', 'rotation']

    # The following options require quotes in generated code
    stringlike_options = ['short_name', 'long_name', 'units']
    # The following arguments are skipped if value is empty string
    optional_options = ['ungridded_dims']
    # The following arguments must be placed within array brackets.
    arraylike_options = ['ungridded_dims']


    def __init__(self, category, args, indent=3):
        self.category = category
        self.args = args
        self.indent  = indent

    def newline(self):
        return "\n" + " "*self.indent

    def continue_line(self):
        return "&" + self.newline() + "& "

    def emit_specs(self):
        return self.emit_header() + self.emit_args() + self.emit_trailer()

    def get_rank(self):
        ranks = {'MAPL_DimsHorzVert':3, 'MAPL_DimsHorzOnly':2, 'MAPL_DimsVertOnly':1}
        extra_rank = 0 # unless
        if 'ungridded_dims' in self.args:
            ungridded = self.args['ungridded_dims']
            if ungridded:
                extra_dims = ungridded.strip('][').split(',')
                extra_rank = len(extra_dims)
        return ranks[self.args['dims']] + extra_rank
        
    def emit_declare_pointers(self):
        text = self.emit_header()
        type = 'real'
        if 'precision' in self.args:
            kind = self.args['precision']
        else:
            kind = None
        rank = self.get_rank()
        dimension = 'dimension(:' + ',:'*(rank-1) + ')'
        text = text + type
        if kind:
            text = text + '(kind=' + str(kind) + ')'
        text = text +', pointer, ' + dimension + ' :: ' + self.args['short_name'] + ' => null()'
        text = text + self.emit_trailer()
        return text

    def emit_get_pointers(self):
        text = self.emit_header()
        text = text + "call MAPL_GetPointer(" + self.category + ', ' + self.args['short_name'] + ", '" + self.args['short_name'] + "', rc=status); VERIFY_(status)" 
        text = text + self.emit_trailer()
        return text

    def emit_header(self):
        text = self.newline()
        if 'CONDITION' in self.args and self.args['CONDITION']:
            self.indent = self.indent + 3
            text = text + "if (" + self.args['CONDITION']  + ") then" + self.newline() 
        return text

    def emit_args(self):
        self.indent = self.indent + 5
        text = "call MAPL_Add" + self.category.capitalize() + "Spec(gc," + self.continue_line()
        for option in MAPL_DataSpec.all_options:
            text = text + self.emit_arg(option)
        text = text + 'rc=status)' + self.newline()
        self.indent = self.indent - 5
        text = text + 'VERIFY_(status)'
        return text

    def emit_arg(self, option):
        text = ''
        if option in self.args:
            value = self.args[option]
            if option in MAPL_DataSpec.optional_options:
                if self.args[option] == '':
                    return ''
            text = text + option + "="
            if option in MAPL_DataSpec.stringlike_options:
                value = "'" + value + "'"
            elif option in MAPL_DataSpec.arraylike_options:
                value = '[' + value + ']' # convert to Fortran 1D array
            text = text + value + ", " + self.continue_line()
        return text

    def emit_trailer(self):
        if 'CONDITION' in self.args and self.args['CONDITION']:
            self.indent = self.indent - 3
            text = self.newline()
            text = text + "endif" + self.newline()
        else:
            text = self.newline()
        return text





def read_specs(specs_filename):
    
    def csv_record_reader(csv_reader):
        """ Read a csv reader iterator until a blank line is found. """
        prev_row_blank = True
        for row in csv_reader:
            if not (len(row) == 0):
                if row[0].startswith('#'):
                    continue
                yield [cell.strip() for cell in row]
                prev_row_blank = False
            elif not prev_row_blank:
                return

    column_aliases = {
        'NAME'      : 'short_name',
        'LONG NAME' : 'long_name',
        'VLOC'      : 'vlocation',
        'UNITS'     : 'units',
        'DIMS'      : 'dims',
        'UNGRIDDED' : 'ungridded_dims',
        'PREC'      : 'precision',
        'COND'      : 'condition'
    }

    specs = {}
    with open(specs_filename, 'r') as specs_file:
        specs_reader = csv.reader(specs_file, skipinitialspace=True,delimiter='|')
        gen = csv_record_reader(specs_reader)
        schema_version = next(gen)[0]
        print("version: ",schema_version)
        component = next(gen)[0]
        print("component: ",component)
        while True:
            try:
                gen = csv_record_reader(specs_reader)
                category = next(gen)[0].split()[1]
                bare_columns = next(gen)
                bare_columns = [c.strip() for c in bare_columns]
                columns = []
                for c in bare_columns:
                    if c in column_aliases:
                        columns.append(column_aliases[c])
                    else:
                        columns.append(c)
                specs[category] = pd.DataFrame(gen, columns=columns)
            except StopIteration:
                break

    entry_aliases = {'z'    : 'MAPL_DimsVertOnly',
                     'z*'   : 'MAPL_DimsVertOnly',
                     'xy'   : 'MAPL_DimsHorzOnly',
                     'xy*'  : 'MAPL_DimsHorzOnly',
                     'xyz'  : 'MAPL_DimsHorzVert',
                     'xyz*' : 'MAPL_DimsHorzVert',
                     'C'    : 'MAPL_VlocationCenter',
                     'E'    : 'MAPL_VlocationEdge',
                     'N'    : 'MAPL_VlocationNone'
    }

    specs['IMPORT'].replace(entry_aliases,inplace=True)
    specs['EXPORT'].replace(entry_aliases,inplace=True)
    specs['INTERNAL'].replace(entry_aliases,inplace=True)

    return specs



def header():
    """
    Returns a standard warning that can be placed at the top of each
    generated _Fortran_ include file.
    """

    return """
!                          -------------------
!                          W  A  R  N  I  N  G
!                          -------------------
!
!   This code fragment is automatically generated by MAPL_GridCompSpecs_ACG.
!   Please DO NOT edit it. Any modification made in here will be overwritten
!   next time this file is auto-generated. Instead, enter your additions
!   or deletions in the .rc file in the src tree.
!
    """

def open_with_header(filename):
    f = open(filename,'w')
    f.write(header())
    return f



#############################################
# Main program begins here
#############################################


# Process command line arguments
parser = argparse.ArgumentParser(description='Generate import/export/internal specs for MAPL Gridded Component')
parser.add_argument('-i','--input', action='store')
parser.add_argument('--add_specs', action='store', default='Spec.h')
parser.add_argument('--declare_pointers', action='store', default='DeclarePointer.h')
parser.add_argument('--get_pointers', action='store', default='GetPointer.h')
args = parser.parse_args()


# Process blocked CSV input file using pandas
specs = read_specs(args.input)

# open all output files
f_specs = {}
for category in ('IMPORT','EXPORT','INTERNAL'):
    f_specs[category] = open_with_header(category.capitalize()+args.add_specs)
f_declare_pointers = open_with_header(args.declare_pointers)
f_get_pointers = open_with_header(args.get_pointers)


# Generate code from specs (processed above with pandas)
for category in ('IMPORT','EXPORT','INTERNAL'):
    for item in specs[category].to_dict('records'):
        spec = MAPL_DataSpec(category.lower(), item)
        f_specs[category].write(spec.emit_specs())
        f_declare_pointers.write(spec.emit_declare_pointers())
        f_get_pointers.write(spec.emit_get_pointers())

# Close output files
for category, f in f_specs.items():
    f.close()
f_declare_pointers.close()
f_get_pointers.close()



            
            
