import gdb

# ------------------------------------------------------ type ---------------------------------------------------------
# type
ECMA_TYPE_DIRECT = 0
ECMA_TYPE_STRING = 1
ECMA_TYPE_FLOAT = 2
ECMA_TYPE_OBJECT = 3
ECMA_TYPE_DIRECT_STRING = 5
ECMA_TYPE_ERROR = 7


def type_str(typ):
    if typ == ECMA_TYPE_DIRECT:
        return "DIRECT"
    elif typ == ECMA_TYPE_STRING:
        return "STRING"
    elif typ == ECMA_TYPE_FLOAT:
        return "FLOAT"
    elif typ == ECMA_TYPE_OBJECT:
        return "OBJECT"
    elif typ == ECMA_TYPE_DIRECT_STRING:
        return "DIRECT_STRING"
    elif typ == ECMA_TYPE_ERROR:
        return "ERROR|COLLECTION_CHUNK|SNAPSHOT_OFFSET"
    return "UNKNOWN_TYPE"


# ---------------------------------------------- direct - simple value -------------------------------------------------
# simple value
ECMA_VALUE_EMPTY = 0
ECMA_VALUE_ERROR = 1
ECMA_VALUE_FALSE = 2
ECMA_VALUE_TRUE = 3
ECMA_VALUE_UNDEFINED = 4
ECMA_VALUE_NULL = 5
ECMA_VALUE_ARRAY_HOLE = 6
ECMA_VALUE_NOT_FOUND = 7
ECMA_VALUE_REGISTER_REF = 8


def simple_value_str(value):
    if value == ECMA_VALUE_EMPTY:
        return "EMPTY"
    elif value == ECMA_VALUE_ERROR:
        return "ERROR"
    elif value == ECMA_VALUE_FALSE:  # false
        return "FALSE"
    elif value == ECMA_VALUE_TRUE:  # true
        return "TRUE"
    elif value == ECMA_VALUE_UNDEFINED:
        return "UNDEFINED"
    elif value == ECMA_VALUE_NULL:  # null
        return "NULL"
    elif value == ECMA_VALUE_ARRAY_HOLE:
        return "ARRAY_HOLE"
    elif value == ECMA_VALUE_NOT_FOUND:
        return "NOT_FOUND"
    elif value == ECMA_VALUE_REGISTER_REF:
        return "REGISTER_REF"
    return "UNKNOWN_SIMPLE_VALUE"


# -------------------------------------------------- direct string -----------------------------------------------------
# direct string
ECMA_DIRECT_STRING_PTR = 0
ECMA_DIRECT_STRING_MAGIC = 1
ECMA_DIRECT_STRING_UINT = 2
ECMA_DIRECT_STRING_MAGIC_EX = 3


def direct_string_type_str(typ):
    if typ == ECMA_DIRECT_STRING_PTR:
        return "PTR"
    elif typ == ECMA_DIRECT_STRING_MAGIC:
        return "MAGIC"
    elif typ == ECMA_DIRECT_STRING_UINT:
        return "UINT"
    elif typ == ECMA_DIRECT_STRING_MAGIC_EX:
        return "MAGIC_EX"
    return "UNKNOWN_DIRECT_STRING_TYPE"


def direct_string(ecma_value):
    typ = (ecma_value >> 3) & 0b11
    # if typ == ECMA_DIRECT_STRING_PTR:
    if typ == ECMA_DIRECT_STRING_MAGIC:  # "Math" "true"
        string_id = str(ecma_value >> 5)
        cmd = "(lit_magic_string_id_t)" + string_id
        string = str(gdb.parse_and_eval(cmd))
        return direct_string_type_str(typ) + "\tid:" + string_id + "\tstring:" + string
    elif typ == ECMA_DIRECT_STRING_UINT:  # "1123"
        number = str(ecma_value >> 5)
        return direct_string_type_str(typ) + "\tstring:" + number
    # if typ == ECMA_DIRECT_STRING_MAGIC_EX:
    return direct_string_type_str(typ) + "\tUNKNOWN"


# -------------------------------------------------- ecma_string_t -----------------------------------------------------
# string container
ECMA_STRING_CONTAINER_HEAP_UTF8_STRING = 0
ECMA_STRING_CONTAINER_HEAP_LONG_UTF8_STRING = 1
ECMA_STRING_CONTAINER_UINT32_IN_DESC = 2
ECMA_STRING_CONTAINER_MAGIC_STRING_EX = 3
ECMA_STRING_LITERAL_NUMBER = 4


def string_container_str(container):
    if container == ECMA_STRING_CONTAINER_HEAP_UTF8_STRING:
        return "CONTAINER_HEAP_UTF8_STRING"
    elif container == ECMA_STRING_CONTAINER_HEAP_LONG_UTF8_STRING:
        return "CONTAINER_HEAP_LONG_UTF8_STRING"
    elif container == ECMA_STRING_CONTAINER_UINT32_IN_DESC:
        return "CONTAINER_UINT32_IN_DESC"
    elif container == ECMA_STRING_CONTAINER_MAGIC_STRING_EX:
        return "CONTAINER_MAGIC_STRING_EX"
    elif container == ECMA_STRING_LITERAL_NUMBER:
        return "LITERAL_NUMBER"
    return "UNKNOWN_STRING_CONTAINER"


def ecma_string_t(ecma_string):
    cmd_base = "(*(ecma_string_t*)" + str(ecma_string) + ")"
    print(cmd_base)
    cmd = cmd_base + ".hash"
    _hash = hex(int(gdb.parse_and_eval(cmd)))
    cmd = cmd_base + ".refs_and_container"
    refs_and_container = int(gdb.parse_and_eval(cmd))
    refs = str(refs_and_container >> 4)
    container = refs_and_container & 0b111
    if container == ECMA_STRING_CONTAINER_HEAP_UTF8_STRING:  # "zmj"
        cmd = cmd_base + ".u.utf8_string.size"
        size = str(gdb.parse_and_eval(cmd))
        cmd = cmd_base + ".u.utf8_string.length"
        length = str(gdb.parse_and_eval(cmd))
        cmd = "(char*)((ecma_string_t*)" + str(ecma_string) + "+1)"
        string = str(gdb.parse_and_eval(cmd))
        string = string[string.index('"') + 1:len(string) - 1]
        return "refs:" + refs + \
               "\tcontainer:" + string_container_str(container) + \
               "\thash:" + _hash + \
               "\tsize:" + size + \
               "\tlength:" + length + \
               "\tstring:" + string
    # elif container == ECMA_STRING_CONTAINER_HEAP_LONG_UTF8_STRING:
    # elif container == ECMA_STRING_CONTAINER_UINT32_IN_DESC:
    # elif container == ECMA_STRING_CONTAINER_MAGIC_STRING_EX:
    # elif container == ECMA_STRING_LITERAL_NUMBER:
    return "UNKNOWN_ECMA_STRING"


def ecma_string(ecma_string):
    if ecma_string & 0b111 == ECMA_TYPE_DIRECT_STRING:
        return direct_string(ecma_string)
    return ecma_string_t(ecma_string)


# ------------------------------------------------------ utils --------------------------------------------------------
def get_pointer_cmd(offset):
    return str(offset) + "+((uint32_t)&jerry_global_heap)"


def get_pointer(offset):
    if offset == 0:
        return "NULL"
    cmd = get_pointer_cmd(offset)
    return str(gdb.parse_and_eval(cmd))


def get_pointer_from_ecma_value_cmd(ecma_value):
    return get_pointer_cmd("(" + str(ecma_value) + "&(~0b111))")


def get_pointer_from_ecma_value(ecma_value):
    cmd = get_pointer_from_ecma_value_cmd(ecma_value)
    print(cmd)
    return str(gdb.parse_and_eval(cmd))


# -------------------------------------------------- ecma_object_t ----------------------------------------------------
# type object
ECMA_OBJECT_TYPE_GENERAL = 0
ECMA_OBJECT_TYPE_CLASS = 1
ECMA_OBJECT_TYPE_FUNCTION = 2
ECMA_OBJECT_TYPE_EXTERNAL_FUNCTION = 3
ECMA_OBJECT_TYPE_ARRAY = 4
ECMA_OBJECT_TYPE_BOUND_FUNCTION = 5
ECMA_OBJECT_TYPE_PSEUDO_ARRAY = 6
ECMA_OBJECT_TYPE_ARROW_FUNCTION = 7


def object_type_str(typ):
    if typ == ECMA_OBJECT_TYPE_GENERAL:
        return "GENERAL"
    elif typ == ECMA_OBJECT_TYPE_CLASS:
        return "CLASS"
    elif typ == ECMA_OBJECT_TYPE_FUNCTION:
        return "FUNCTION"
    elif typ == ECMA_OBJECT_TYPE_EXTERNAL_FUNCTION:
        return "EXTERNAL_FUNCTION"
    elif typ == ECMA_OBJECT_TYPE_ARRAY:
        return "ARRAY"
    elif typ == ECMA_OBJECT_TYPE_BOUND_FUNCTION:
        return "BOUND_FUNCTION"
    elif typ == ECMA_OBJECT_TYPE_PSEUDO_ARRAY:
        return "PSEUDO_ARRAY"
    elif typ == ECMA_OBJECT_TYPE_ARROW_FUNCTION:
        return "ARROW_FUNCTION"
    return "UNKNOWN_OBJECT_TYPE"

ECMA_OBJECT_FLAG_BUILT_IN_OR_LEXICAL_ENV = 0x10
ECMA_OBJECT_FLAG_EXTENSIBLE = 0x20

def ecma_object_t(ecma_object):
    cmd_base = "(*(ecma_object_t*)" + str(ecma_object) + ")"
    print(cmd_base)
    cmd = cmd_base + ".type_flags_refs"
    type_flags_refs = int(gdb.parse_and_eval(cmd))
    typ = type_flags_refs & 0b111
    flag = (type_flags_refs >> 4) & 0b11
    refs = str(type_flags_refs >> 6)
    cmd = cmd_base + ".gc_next_cp"
    gc_next_cp = int(gdb.parse_and_eval(cmd))
    cmd = cmd_base + ".property_list_or_bound_object_cp"
    property_list_or_bound_object = int(gdb.parse_and_eval(cmd))
    cmd = cmd_base + ".prototype_or_outer_reference_cp"
    prototype_or_outer_reference = int(gdb.parse_and_eval(cmd))
    return object_type_str(typ) + "\tflag:" + str(flag) + \
           "\trefs:" + refs + \
           "\tnext_gc:" + get_pointer(gc_next_cp) + \
           "\tproperty_list_or_bound_object:" + get_pointer(property_list_or_bound_object) + \
           "\tprototype_or_outer_reference:" + get_pointer(prototype_or_outer_reference)


# --------------------------------------------------- ecma_value_t -----------------------------------------------------
def ecma_value_t(ecma_value):
    typ = ecma_value & 0b111
    if typ == ECMA_TYPE_DIRECT:
        flag = (ecma_value >> 3) & 1
        if flag == 1:  # true false null
            return "DIRECT\t" + "SIMPLE\t" + simple_value_str(ecma_value >> 4)
        else:  # -1123
            cmd = "(ecma_number_t)((int32_t)" + str(ecma_value) + ">>4)"
            print(cmd)
            return "DIRECT\t" + "INTEGER\t" + str(gdb.parse_and_eval(cmd))
    elif typ == ECMA_TYPE_STRING:
        return ecma_string_t(get_pointer_from_ecma_value(ecma_value))
    elif typ == ECMA_TYPE_FLOAT:  # 11.23 1234567890
        cmd = "*(ecma_number_t*)(" + get_pointer_from_ecma_value_cmd(ecma_value) + ")"
        print(cmd)
        return "FLOAT\t" + str(gdb.parse_and_eval(cmd))
    elif typ == ECMA_TYPE_OBJECT:
        return "OBJECT\t" + ecma_object_t(get_pointer_from_ecma_value(ecma_value))
    elif typ == ECMA_TYPE_DIRECT_STRING:
        return "DIRECT_STRING\t" + direct_string(ecma_value)
    # elif typ == ECMA_TYPE_ERROR:
    return "UNKNOWN_ECMA_VALUE"


# ----------------------------------------------------- EcmaPrint ------------------------------------------------------
class EcmaPrint(gdb.Command):
    # help
    """Print ecma_value_t and ecma_string_t

    Usage: ep [v|s|o] variable

    Example:
        (gdb) ep v val -- print ecma_value_t
        (gdb) ep s str -- print ecma_string_t
        (gdb) ep o obj -- print ecma_object_t
    """

    def __init__(self):
        super(self.__class__, self).__init__("ep", gdb.COMMAND_USER)

    def invoke(self, args, from_tty):
        argv = gdb.string_to_argv(args)
        if len(argv) != 2:
            raise gdb.GdbError("Invalid parameter number. See help ep.")
        if argv[0] == "v":
            value = int(gdb.parse_and_eval("(uint32_t)" + argv[1]))
            print(value)
            print(ecma_value_t(value))
            return
        elif argv[0] == "s":
            value = int(gdb.parse_and_eval("(uint32_t)" + argv[1]))
            print(value)
            print(ecma_string(value))
            return
        elif argv[0] == "o":
            value = int(gdb.parse_and_eval("(uint32_t)" + argv[1]))
            print(value)
            print(ecma_object_t(value))
            return

        raise gdb.GdbError("Unsupported parameter. See help ep.")


# https://segmentfault.com/search?q=gdb&type=article&relatedObjectId=1200000000428141
# https://sourceware.org/gdb/download/onlinedocs/gdb/Basic-Python.html#Basic-Python
EcmaPrint()
