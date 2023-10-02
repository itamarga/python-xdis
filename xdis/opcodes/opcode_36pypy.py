# (C) Copyright 2019-2021, 2023 by Rocky Bernstein
"""
PYPY 3.6 opcodes

This is a like Python 3.6's opcode.py with some classification
of stack usage and information for formatting instructions.
"""

import sys

import xdis.opcodes.opcode_36 as opcode_36
from xdis.opcodes.base import (
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    name_op,
    nargs_op,
    rm_op,
    update_pj3,
    varargs_op,
)
from xdis.opcodes.format.basic import (
    format_CALL_FUNCTION_pos_name_encoded,
    format_extended_arg,
    format_RAISE_VARARGS_older,
)
from xdis.opcodes.format.extended import (
    extended_format_ATTR,
    extended_format_RAISE_VARARGS_older,
    extended_format_RETURN_VALUE,
)
from xdis.opcodes.opcode_36 import (
    extended_format_MAKE_FUNCTION_36,
    format_MAKE_FUNCTION,
)

version_tuple = (3, 6)
python_implementation = "PyPy"

loc = locals()
init_opdata(loc, opcode_36, version_tuple, is_pypy=True)

## FIXME: DRY common PYPY opcode additions

# Opcodes removed from 3.6.

rm_op(loc, "CALL_FUNCTION_EX", 142)
rm_op(loc, "BUILD_TUPLE_UNPACK_WITH_CALL", 158)

# The following were removed from 3.6 but still in Pypy 3.6
def_op(loc, "MAKE_CLOSURE", 134, 9, 1)  # TOS is number of items to pop
nargs_op(loc, "CALL_FUNCTION_VAR", 140, 9, 1)  # #args + (#kwargs << 8)
nargs_op(loc, "CALL_FUNCTION_KW", 141, 9, 1)  # #args + (#kwargs << 8)
nargs_op(loc, "CALL_FUNCTION_VAR_KW", 142, 9, 1)  # #args + (#kwargs << 8)

# PyPy only
# ----------

name_op(loc, "LOOKUP_METHOD", 201, 1, 2)
nargs_op(loc, "CALL_METHOD", 202, -1, 1)
loc["hasvargs"].append(202)


# Used only in single-mode compilation list-comprehension generators
varargs_op(loc, "BUILD_LIST_FROM_ARG", 203)

# Used only in assert statements
jrel_op(loc, "JUMP_IF_NOT_DEBUG", 204, conditional=True)

# PyPy 3.6.1 (and 2.7.13) start to introduce LOAD_REVDB_VAR

if sys.version_info[:3] >= (3, 6, 1):
    def_op(loc, "LOAD_REVDB_VAR", 205)

opcode_arg_fmt = {
    "EXTENDED_ARG": format_extended_arg,
    "MAKE_CLOSURE": format_MAKE_FUNCTION,
    "MAKE_FUNCTION": format_MAKE_FUNCTION,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
}

opcode_extended_fmt = {
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_CLOSURE": extended_format_MAKE_FUNCTION_36,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION_36,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}

# FIXME remove (fix uncompyle6)
update_pj3(globals(), loc)
finalize_opcodes(loc)
