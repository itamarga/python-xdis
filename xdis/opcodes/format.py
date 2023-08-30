"""
Routines for formatting opcodes.
"""
from typing import Optional, Tuple


def extended_format_binary_op(
    opc, instructions, fmt_str: str
) -> Tuple[str, Optional[int]]:
    """ """
    i = 1
    # 3.11+ has CACHE instructions
    while instructions[i].opname == "CACHE":
        i += 1
    stack_arg1 = instructions[i]
    arg1 = None
    if stack_arg1.tos_str is not None:
        arg1 = stack_arg1.tos_str
    if arg1 is not None or stack_arg1.opcode in opc.operator_set:
        if arg1 is None:
            arg1 = instructions[1].argrepr
        arg1_start_offset = instructions[1].start_offset
        if arg1_start_offset is not None:
            for i in range(1, len(instructions)):
                if instructions[i].offset == arg1_start_offset:
                    break
        j = i + 1
        # 3.11+ has CACHE instructions
        while instructions[j].opname == "CACHE":
            j += 1
        if (
            instructions[j].opcode in opc.operator_set
            and instructions[i].opcode in opc.operator_set
        ):
            arg2 = (
                instructions[j].tos_str
                if instructions[j].tos_str is not None
                else instructions[j].argrepr
            )
            start_offset = instructions[j].start_offset
            return fmt_str % (arg2, arg1), start_offset
        elif instructions[j].start_offset is not None:
            start_offset = instructions[j].start_offset
            arg2 = (
                instructions[j].tos_str
                if instructions[j].tos_str is not None
                else instructions[j].argrepr
            )
            if arg2 == "":
                arg2 = "..."
            return fmt_str % (arg2, arg1), start_offset
        else:
            return fmt_str % ("...", arg1), None
    return "", None


def extended_format_infix_binary_op(
    opc, instructions, op_str: str
) -> Tuple[str, Optional[int]]:
    """ """
    i = 1
    # 3.11+ has CACHE instructions
    while instructions[i].opname == "CACHE":
        i += 1
    stack_arg1 = instructions[i]
    arg1 = None
    if stack_arg1.tos_str is not None:
        arg1 = stack_arg1.tos_str
    if arg1 is not None or stack_arg1.opcode in opc.operator_set:
        if arg1 is None:
            arg1 = instructions[1].argrepr
        else:
            arg1 = f"({arg1})"
        arg1_start_offset = instructions[1].start_offset
        if arg1_start_offset is not None:
            for i in range(1, len(instructions)):
                if instructions[i].offset == arg1_start_offset:
                    break
        j = i + 1
        # 3.11+ has CACHE instructions
        while instructions[j].opname == "CACHE":
            j += 1
        if (
            instructions[j].opcode in opc.operator_set
            and instructions[i].opcode in opc.operator_set
        ):
            arg2 = (
                instructions[j].tos_str
                if instructions[j].tos_str is not None
                else instructions[j].argrepr
            )
            start_offset = instructions[j].start_offset
            return f"{arg2}{op_str}{arg1}", start_offset
        elif instructions[j].start_offset is not None:
            start_offset = instructions[j].start_offset
            arg2 = (
                instructions[j].tos_str
                if instructions[j].tos_str is not None
                else instructions[j].argrepr
            )
            if arg2 == "":
                arg2 = "..."
            else:
                arg2 = f"({arg2})"
            return f"{arg2}{op_str}{arg1}", start_offset
        else:
            return f"...{op_str}{arg1}", None
    return "", None


def extended_format_store_op(opc, instructions: list) -> Tuple[str, Optional[int]]:
    inst = instructions[0]
    prev_inst = instructions[1]
    start_offset = prev_inst.offset
    if prev_inst.opname == "IMPORT_NAME":
        return f"{inst.argval} = import_module({inst.argval})", start_offset
    elif prev_inst.opname == "IMPORT_FROM":
        return f"{inst.argval} = import_module({prev_inst.argval})", start_offset
    elif prev_inst.opcode in opc.operator_set:
        if prev_inst.tos_str is None:
            return "", start_offset

        argval = prev_inst.argval
        if prev_inst.opname == "LOAD_CONST":
            argval = safe_repr(argval)
        argval = prev_inst.tos_str if prev_inst.tos_str is not None else argval
        start_offset = prev_inst.start_offset
        if prev_inst.opname.startswith("INPLACE_"):
            # Inplace operators show their own assign
            return argval, start_offset
        return f"{inst.argval} = {argval}", start_offset

    return "", start_offset


def extended_format_unary_op(
    opc, instructions, fmt_str: str
) -> Tuple[str, Optional[int]]:
    stack_arg = instructions[1]
    start_offset = instructions[1].start_offset
    if stack_arg.tos_str is not None:
        return fmt_str % stack_arg.tos_str, start_offset
    if stack_arg.opcode in opc.operator_set:
        return fmt_str % stack_arg.argrepr, start_offset
    return "", None


def extended_format_ATTR(opc, instructions) -> Optional[Tuple[str, int]]:
    if instructions[1].opcode in opc.NAME_OPS | opc.CONST_OPS | opc.LOCAL_OPS:
        return (
            "%s.%s" % (instructions[1].argrepr, instructions[0].argrepr),
            instructions[1].offset,
        )


def extended_format_BINARY_ADD(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " + ")


def extended_format_BINARY_AND(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " & ")


def extended_format_BINARY_FLOOR_DIVIDE(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " // ")


def extended_format_BINARY_LSHIFT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " << ")


def extended_format_BINARY_MODULO(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " %% ")


def extended_format_BINARY_MULTIPLY(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " * ")


def extended_format_BINARY_OR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " | ")


def extended_format_BINARY_POWER(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " ** ")


def extended_format_BINARY_RSHIFT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " >> ")


def extended_format_BINARY_SUBSCR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_binary_op(
        opc,
        instructions,
        "%s[%s]",
    )


def extended_format_BINARY_SUBTRACT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " - ")


def extended_format_BINARY_TRUE_DIVIDE(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " / ")


def extended_format_BINARY_XOR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " ^ ")


def extended_format_COMPARE_OP(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(
        opc,
        instructions,
        f" {instructions[0].argval} ",
    )


def extended_format_CALL_FUNCTION(opc, instructions) -> Tuple[str, Optional[int]]:
    """CALL_FUNCTION pre 3.6.
    Look in `instructions` to see if we can find a method name.  If not we'll
    return None.
    """
    # From opcode description: argc indicates the total number of positional
    # and keyword arguments.  Sometimes the function name is in the stack arg
    # positions back.
    call_function_inst = instructions[0]
    call_opname = call_function_inst.opname
    assert call_opname in (
        "CALL_FUNCTION",
        "CALL_FUNCTION_KW",
        "CALL_FUNCTION_VAR",
        "CALL_FUNCTION_VAR_KW",
    )
    argc = call_function_inst.arg
    (
        name_default,
        pos_args,
    ) = divmod(argc, 256)
    function_pos = pos_args + name_default * 2 + 1
    if call_opname in ("CALL_FUNCTION_VAR", "CALL_FUNCTION_KW"):
        function_pos += 1
    elif call_opname == "CALL_FUNCTION_VAR_KW":
        function_pos += 2
    assert len(instructions) >= function_pos + 1
    i = -1
    for i, inst in enumerate(instructions[1:]):
        if i + 1 == function_pos:
            i += 1
            break
        if inst.is_jump_target:
            i += 1
            break
        # Make sure we are in the same basic block
        # and ... ?
        opcode = inst.opcode
        if inst.optype in ("nargs", "vargs"):
            break
        if inst.opname == "LOAD_ATTR" or inst.optype != "name":
            function_pos += (opc.oppop[opcode] - opc.oppush[opcode]) + 1
        if inst.opname in ("CALL_FUNCTION", "CALL_FUNCTION_KW", "CALL_FUNCTION_VAR"):
            break
        pass

    s = ""
    start_offset = None
    if i == function_pos:
        opname = instructions[function_pos].opname
        if opname in (
            "LOAD_CONST",
            "LOAD_GLOBAL",
            "LOAD_ATTR",
            "LOAD_NAME",
        ):
            if not (
                opname == "LOAD_CONST"
                and isinstance(instructions[function_pos].argval, (int, str))
            ):
                s, start_offset = resolved_attrs(instructions[function_pos:])
                s += ": "
            start_offset = call_function_inst.offset
    s += format_CALL_FUNCTION_pos_name_encoded(call_function_inst.arg)
    return s, start_offset


def extended_format_IMPORT_NAME(opc, instructions) -> Tuple[str, Optional[int]]:
    inst = instructions[0]
    start_offset = inst.start_offset
    return f"import_module({inst.argval})", start_offset


def extended_format_INPLACE_ADD(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " += ")


def extended_format_INPLACE_AND(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " &= ")


def extended_format_INPLACE_FLOOR_DIVIDE(
    opc, instructions
) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " //= ")


def extended_format_INPLACE_LSHIFT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " <<= ")


def extended_format_INPLACE_MODULO(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " %%= ")


def extended_format_INPLACE_MULTIPLY(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " *= ")


def extended_format_INPLACE_OR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " |= ")


def extended_format_INPLACE_POWER(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " **= ")


def extended_format_INPLACE_TRUE_DIVIDE(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " /= ")


def extended_format_INPLACE_RSHIFT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " >>= ")


def extended_format_INPLACE_SUBTRACT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " -= ")


def extended_format_INPLACE_XOR(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(opc, instructions, " ^= ")


def extended_format_IS_OP(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_infix_binary_op(
        opc,
        instructions,
        f"%s {format_IS_OP(instructions[0].arg)} %s",
    )


# Can combine with extended_format_MAKE_FUNCTION_36?
def extended_format_MAKE_FUNCTION_10_27(opc, instructions) -> Tuple[str, int]:
    """
    instructions[0] should be a "MAKE_FUNCTION" or "MAKE_CLOSURE" instruction. TOS
    should have the function or closure name.

    This code works for Python versions up to and including 2.7.
    Python docs for MAKE_FUNCTION and MAKE_CLOSURE the was changed in 33, but testing
    shows that the change was really made in Python 3.0 or so.
    """
    # From opcode description: argc indicates the total number of positional
    # and keyword arguments.  Sometimes the function name is in the stack arg
    # positions back.
    assert len(instructions) >= 2
    inst = instructions[0]
    assert inst.opname in ("MAKE_FUNCTION", "MAKE_CLOSURE")
    s = ""
    name_inst = instructions[1]
    code_inst = instructions[2]
    start_offset = code_inst.offset
    if code_inst.opname == "LOAD_CONST" and hasattr(code_inst.argval, "co_name"):
        s += f"make_function({short_code_repr(name_inst.argval)}"
        return s, start_offset
    return s, start_offset


def extended_format_RAISE_VARARGS_older(opc, instructions) -> Tuple[Optional[str], int]:
    raise_inst = instructions[0]
    assert raise_inst.opname == "RAISE_VARARGS"
    argc = raise_inst.argval
    start_offset = raise_inst.start_offset
    if argc == 0:
        return "reraise", start_offset
    elif argc == 1:
        exception_name_inst = instructions[1]
        start_offset = exception_name_inst.start_offset
        exception_name = (
            exception_name_inst.tos_str
            if exception_name_inst.tos_str
            else exception_name_inst.argrepr
        )
        if exception_name is not None:
            return f"raise {exception_name}()", start_offset
    return format_RAISE_VARARGS_older(raise_inst.argval), start_offset


def extended_format_RETURN_VALUE(opc, instructions: list) -> Tuple[str, Optional[int]]:
    return extended_format_unary_op(opc, instructions, "return %s")


def extended_format_UNARY_INVERT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_unary_op(opc, instructions, "~(%s)")


def extended_format_UNARY_NEGATIVE(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_unary_op(opc, instructions, "-(%s)")


def extended_format_UNARY_NOT(opc, instructions) -> Tuple[str, Optional[int]]:
    return extended_format_unary_op(opc, instructions, "not (%s)")


def format_extended_arg(arg):
    return str(arg * (1 << 16))


def format_CALL_FUNCTION_pos_name_encoded(argc):
    """Encoded positional and named args. Used to
    up to about 3.6 where wordcodes are used and
    a different encoding occurs. Pypy36 though
    sticks to this encoded version though."""
    name_default, pos_args = divmod(argc, 256)
    return "%d positional, %d named" % (pos_args, name_default)


def format_IS_OP(arg: int) -> str:
    return "is" if arg == 0 else "is not"


def format_MAKE_FUNCTION_10_27(argc: int) -> str:
    """
    ``argc`` is the operand  of a  "MAKE_FUNCTION" or "MAKE_CLOSURE" instruction.

    This code works for Python versions up to and including 2.7.
    Python docs for MAKE_FUNCTION and MAKE_CLOSURE the was changed in 33, but testing
    shows that the change was really made in Python 3.0 or so.
    """
    return f"{argc} default parameters"


# Up until 3.7
def format_RAISE_VARARGS_older(argc):
    assert 0 <= argc <= 3
    if argc == 0:
        return "reraise"
    elif argc == 1:
        return "exception"
    elif argc == 2:
        return "exception, parameter"
    elif argc == 3:
        return "exception, parameter, traceback"


def resolved_attrs(instructions: list) -> Tuple[str, int]:
    """ """
    # we can probably speed up using the "tos_str" field.
    resolved = []
    start_offset = 0
    for inst in instructions:
        name = inst.argrepr
        if name:
            if name[0] == "'" and name[-1] == "'":
                name = name[1:-1]
        else:
            name = ""
        resolved.append(name)
        if inst.opname != "LOAD_ATTR":
            start_offset = inst.offset
            break
    return ".".join(reversed(resolved)), start_offset


def safe_repr(obj, max_len: int = 20) -> str:
    """
    String repr with length at most ``max_len``
    """
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if len(result) > max_len:
        return result[:max_len] + "..."
    return result


def short_code_repr(code) -> str:
    """
    A shortened string representation of a code object
    """
    return f"<code object {code.co_name}>"


# fmt: off
opcode_arg_fmt_base = opcode_arg_fmt34 = {
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_KW": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_VAR_KW": format_CALL_FUNCTION_pos_name_encoded,
    "EXTENDED_ARG": format_extended_arg,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

# The below are roughly Python 3.3 based. Python 3.11 removes some of these.
opcode_extended_fmt_base = {
    "BINARY_ADD":            extended_format_BINARY_ADD,
    "BINARY_AND":            extended_format_BINARY_AND,
    "BINARY_FLOOR_DIVIDE":   extended_format_BINARY_FLOOR_DIVIDE,
    "BINARY_MODULO":         extended_format_BINARY_MODULO,
    "BINARY_MULTIPLY":       extended_format_BINARY_MULTIPLY,
    "BINARY_RSHIFT":         extended_format_BINARY_RSHIFT,
    "BINARY_SUBSCR":         extended_format_BINARY_SUBSCR,
    "BINARY_SUBTRACT":       extended_format_BINARY_SUBTRACT,
    "BINARY_TRUE_DIVIDE":    extended_format_BINARY_TRUE_DIVIDE,
    "BINARY_LSHIFT":         extended_format_BINARY_LSHIFT,
    "BINARY_OR":             extended_format_BINARY_OR,
    "BINARY_POWER":          extended_format_BINARY_POWER,
    "BINARY_XOR":            extended_format_BINARY_XOR,
    "COMPARE_OP":            extended_format_COMPARE_OP,
    "IMPORT_NAME":           extended_format_IMPORT_NAME,
    "INPLACE_ADD":           extended_format_INPLACE_ADD,
    "INPLACE_AND":           extended_format_INPLACE_AND,
    "INPLACE_FLOOR_DIVIDE":  extended_format_INPLACE_FLOOR_DIVIDE,
    "INPLACE_LSHIFT":        extended_format_INPLACE_LSHIFT,
    "INPLACE_MODULO":        extended_format_INPLACE_MODULO,
    "INPLACE_MULTIPLY":      extended_format_INPLACE_MULTIPLY,
    "INPLACE_OR":            extended_format_INPLACE_OR,
    "INPLACE_POWER":         extended_format_INPLACE_POWER,
    "INPLACE_RSHIFT":        extended_format_INPLACE_RSHIFT,
    "INPLACE_SUBTRACT":      extended_format_INPLACE_SUBTRACT,
    "INPLACE_TRUE_DIVIDE":   extended_format_INPLACE_TRUE_DIVIDE,
    "INPLACE_XOR":           extended_format_INPLACE_XOR,
    "IS_OP":                 extended_format_IS_OP,
    "LOAD_ATTR":             extended_format_ATTR,
    "RAISE_VARARGS":         extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE":          extended_format_RETURN_VALUE,
    "STORE_ATTR":            extended_format_ATTR,
    "STORE_FAST":            extended_format_store_op,
    "STORE_NAME":            extended_format_store_op,
    "UNARY_INVERT":          extended_format_UNARY_INVERT,
    "UNARY_NEGATIVE":        extended_format_UNARY_NEGATIVE,
    "UNARY_NOT":             extended_format_UNARY_NOT,
}
# fmt: on
