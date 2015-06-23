"""
The module containing the PyReshaper configuration specification class

This is a configuration specification class, through which the input to
the PyReshaper code is specified.  Currently all types of supported
operations for the PyReshaper are specified with derived dypes of the
Specification class.

Copyright 2015, University Corporation for Atmospheric Research
See the LICENSE.txt file for details
"""

from os import path as ospath
from datetime import datetime

import Nio


#==============================================================================
# create_specifier factory function
#==============================================================================
def create_specifier(**kwargs):
    """
    Factory function for Specifier class objects.  Defined for convenience.

    Keyword Arguments:
        kwargs (dict): Optional arguments to be passed to the newly created
            Specifier object's constructor.

    Returns:
        Specifier: An instantiation of the type of Specifier class desired.
    """
    return Specifier(**kwargs)


#==============================================================================
# split_specifier helper function
#==============================================================================
def split_specifier_on_dates(specifier,
                             date_markers=[],
                             time_name='time'):
    """
    Split a Specifier object into multiple specifiers according to date range

    The *input_file_list* member of the Specifier is divided among N+1 new 
    Specifiers, where N is the length of the *date_markers* parameter.  The
    *output_file_suffix* for each new Specifier is prepended with a string of
    the format:

        "YYYYMMDDTHHMMSSZ-YYYYMMDDTHHMMSSZ" + output_file_suffix

    where each "YYYYMMDDTHHMMSSZ" indicates the year/month/day date and
    hour/minute/second/zone time of the first and last datetimes in the new 
    Specifier's range. All other members of the Specifier are left unchanged.

    Parameters:
        specifier (Specifier): A single Specifier instance detailing one
            Reshaper operation that should be split into multiple (independent)
            operations

    Keyword Arguments:
        date_markers (list): A list of datetime markers that indicate
            date-time ranges and their boundaries.  Each date marker indicates
            an *inclusive* lower bound on the time range.
        time_name (str): The string name of the time variable in the NetCDF
            file

    Returns:
        list: A list of Specifier instantiations
    """

    # Check types
    if not isinstance(specifier, Specifier):
        err_msg = "Specifier argumetn must be of type Specifier"
        raise TypeError(err_msg)
    if type(date_markers) is not tuple or type(date_markers) is not list:
        err_msg = "Date markers must be in a list or tuple"
        raise TypeError(err_msg)
    for date_marker in date_markers:
        if type(date_marker) is not datetime:
            err_msg = "Date markers must be datetime objects"
            raise TypeError(err_msg)

    # Get list of files in input specifier
    input_files = specifier.input_file_list
    beg_dates = [datetime] * len(input_files)
    end_dates = [datetime] * len(input_files)
    for input_file in input_files:
        nio_file = Nio.open_file(input_file)
        time_var = nio_file.variables[time_name]
        time_units = 
        nio_file.close()


#==============================================================================
# Specifier Base Class
#==============================================================================
class Specifier(object):

    """
    Time-slice to Time-series Convertion Specifier

    This class acts as a container for the various input data needed
    by the Reshaper to perform the time-slice to time-series operation.
    """

    def __init__(self,
                 infiles=[],
                 ncfmt='netcdf4c',
                 prefix='tseries.',
                 suffix='.nc',
                 metadata=[],
                 **kwargs):
        """
        Initializes the internal data with optional arguments.

        The time-series output files are named according to the
        convention:

            output_file_name = prefix + variable_name + suffix

        The output_file_name should be a full-path filename.

        Keyword Arguments:
            infiles (list): List of full-path input filenames
            ncfmt (str): String specifying the NetCDF
                data format ('netcdf','netcdf4','netcdf4c')
            prefix (str): String specifying the full-path prefix common
                to all time-series output files
            suffix (str): String specifying the suffix common
                to all time-series output files
            metadata (list): List of variable names specifying the
                variables that should be included in every
                time-series output file
            kwargs (dict): Optional arguments describing the 
                Reshaper run
        """

        # The list of input (time-slice) NetCDF files (absolute paths)
        self.input_file_list = infiles

        # The string specifying the NetCDF file format for output
        self.netcdf_format = ncfmt

        # The common prefix to all output files (following the rule:
        #  prefix + variable_name + suffix)
        self.output_file_prefix = prefix

        # The common suffix to all output files (following the rule:
        #  prefix + variable_name + suffix)
        self.output_file_suffix = suffix

        # List of time-variant variables that should be included in all
        #  output files.
        self.time_variant_metadata = metadata

        # Optional arguments associated with the reshaper operation
        self.options = kwargs

    def validate(self):
        """
        Perform self-validation of internal data
        """

        # Validate types
        self.validate_types()

        # Validate values
        self.validate_values()

    def validate_types(self):
        """
        Method for checking the types of the Specifier data.

        This method is called by the validate() method.
        """

        # Validate the type of the input file list
        if not isinstance(self.input_file_list, list):
            err_msg = "Input file list must be a list"
            raise TypeError(err_msg)

        # Validate that each input file name is a string
        for ifile_name in self.input_file_list:
            if not isinstance(ifile_name, str):
                err_msg = "Input file names must be given as strings"
                raise TypeError(err_msg)

        # Validate the netcdf format string
        if not isinstance(self.netcdf_format, str):
            err_msg = "NetCDF format must be given as a string"
            raise TypeError(err_msg)

        # Validate the output file prefix
        if not isinstance(self.output_file_prefix, str):
            err_msg = "Output file prefix must be given as a string"
            raise TypeError(err_msg)

        # Validate the output file suffix
        if not isinstance(self.output_file_suffix, str):
            err_msg = "Output file suffix must be given as a string"
            raise TypeError(err_msg)

        # Validate the type of the time-variant metadata list
        if not isinstance(self.time_variant_metadata, list):
            err_msg = "Input file list must be a list"
            raise TypeError(err_msg)

        # Validate the type of each time-variant metadata variable name
        for var_name in self.time_variant_metadata:
            if not isinstance(var_name, str):
                err_msg = "Time-variant metadata variable names must be " + \
                          "given as strings"
                raise TypeError(err_msg)

    def validate_values(self):
        """
        Method to validate the values of the Specifier data.

        This method is called by the validate() method.

        We impose the (somewhat arbitrary) rule that the Specifier
        should not validate values what require "cracking" open the
        input files themselves.  Hence, we validate values that can
        be checked without any PyNIO file I/O (including reading the
        header information).

        This method will correct some input if it is safe to do so.
        """

        # Make sure there is at least 1 input file given
        if len(self.input_file_list) == 0:
            err_msg = "There must be at least one input file given."
            raise ValueError(err_msg)

        # Validate that each input file exists and is a regular file
        for ifile_name in self.input_file_list:
            if not ospath.isfile(ifile_name):
                err_msg = "Input file " + str(ifile_name) + \
                          " is not a regular file"
                raise ValueError(err_msg)

        # Validate the value of the netcdf format string
        valid_formats = ['netcdf', 'netcdf4', 'netcdf4c']
        if self.netcdf_format not in valid_formats:
            err_msg = "Output NetCDF file format " \
                + str(self.netcdf_format) \
                + " is not valid"
            raise ValueError(err_msg)

        # Validate the output file directory
        abs_output_prefix = ospath.abspath(self.output_file_prefix)
        abs_output_dir = ospath.dirname(abs_output_prefix)
        if not ospath.isdir(abs_output_dir):
            err_msg = "Output directory " + str(abs_output_dir) + \
                " implied in output prefix " + \
                str(self.output_file_prefix) + " is not valid"
            raise ValueError(err_msg)
        self.output_file_prefix = abs_output_prefix

        # Validate the output file suffix string (should end in .nc)
        if (self.output_file_suffix[-3:] != '.nc'):
            self.output_file_suffix += '.nc'


#==============================================================================
# Command-line Operation
#==============================================================================
if __name__ == '__main__':
    pass