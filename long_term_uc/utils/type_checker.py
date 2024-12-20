import sys
import logging
from typing import Dict

from long_term_uc.common.error_msgs import print_errors_list


# basic checker
def check_str(data_val) -> bool:
    return isinstance(data_val, str)


def check_int(data_val) -> bool:
    return isinstance(data_val, int)


# lists of a given type
def check_list_of_given_type(data_val, needed_type: type) -> bool:
    if isinstance(data_val, list) is False:
        return False
    return all([isinstance(elt, needed_type) for elt in data_val])


def check_list_of_str(data_val) -> bool:
    return check_list_of_given_type(data_val=data_val, needed_type=str)


def check_list_of_int(data_val) -> bool:
    return check_list_of_given_type(data_val=data_val, needed_type=int)


def check_list_of_float(data_val) -> bool:
    return check_list_of_given_type(data_val=data_val, needed_type=float)


def check_none_or_list_of_str(data_val) -> bool:
    if data_val is None:
        return True
    return check_list_of_str(data_val=data_val)


# complex dicts
def check_str_str_dict(data_val) -> bool:
    if isinstance(data_val, dict) is False:
        return False
    keys_and_vals = list(data_val.keys())
    keys_and_vals.extend(data_val.values())
    return all([isinstance(elt, str) for elt in keys_and_vals])


def check_str_list_of_str_dict(data_val) -> bool:
    if isinstance(data_val, dict) is False:
        return False
    keys = list(data_val.keys())
    vals = list(data_val.values())
    return check_list_of_str(data_val=keys) and \
        all([check_list_of_str(data_val=val) for val in vals])


def check_str_list_of_float_dict(data_val) -> bool:
    if isinstance(data_val, dict) is False:
        return False
    keys = list(data_val.keys())
    vals = list(data_val.values())
    return check_list_of_str(data_val=keys) and \
        all([check_list_of_float(data_val=val) for val in vals])


def check_str_dict_dict(data_val) -> bool:
    """
    Check that data_val be of type {str: dict}
    """
    if isinstance(data_val, dict) is False:
        return False
    keys = list(data_val.keys())
    vals = list(data_val.values())
    return check_list_of_str(data_val=keys) and all([isinstance(val, dict) for val in vals])


def check_three_level_str_dict(data_val) -> bool:
    if isinstance(data_val, dict) is False:
        return False
    return all([(isinstance(key, str) and check_str_str_dict(data_val=val)) for key, val in data_val.items()])


def check_str_str_list_of_str_dict(data_val) -> bool:
    if isinstance(data_val, dict) is False:
        return False
    keys = list(data_val.keys())
    vals = list(list(data_val.values()))
    return check_list_of_str(data_val=keys) and \
        all([check_str_list_of_str_dict(data_val=val) for val in vals])


# generic function to apply a given type checker
def apply_data_type_check(data_type: str, data_val) -> bool:
    if data_type not in CHECK_FUNCTIONS:
        logging.error(f"Unknown data type for check {data_type} -> STOP")
        sys.exit(1)
    if CHECK_FUNCTIONS[data_type] is None:
        logging.error(f"Function to check data type {data_type} is None (not defined) -> STOP")
        sys.exit(1)
    return list(map(CHECK_FUNCTIONS[data_type], [data_val]))[0]


# correspondence between types and associated functions (and additional keyword args when applicable) 
# to be applied for type check
CHECK_FUNCTIONS = {"str": check_str,
                   "int": check_int,
                   "list_of_int": check_list_of_int,
                   "list_of_str": check_list_of_str,
                   "none_or_list_of_str": check_none_or_list_of_str,
                   "dict_str_dict": check_str_dict_dict, 
                   "dict_str_list_of_float": check_str_list_of_float_dict,
                   "dict_str_list_of_str": check_str_list_of_str_dict,
                   "dict_str_str": check_str_str_dict,
                   "two_level_dict_str_str_list-of-str": check_str_str_list_of_str_dict,
                   "two_level_dict_str_str_str": check_three_level_str_dict
                   }


def apply_params_type_check(param_obj_dict: dict, types_for_check: Dict[str, str], param_name: str):
    check_errors = []
    for attr_tb_checked, type_for_check in types_for_check.items():
        if attr_tb_checked in param_obj_dict:
            check_result = apply_data_type_check(data_type=type_for_check, data_val=param_obj_dict[attr_tb_checked])
            if check_result is False:
                check_errors.append(attr_tb_checked)
    if len(check_errors) > 0:
        print_errors_list(error_name=f"{param_name} JSON data with erroneous types",
                          errors_list=check_errors)
