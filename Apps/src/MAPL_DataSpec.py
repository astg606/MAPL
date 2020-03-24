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


