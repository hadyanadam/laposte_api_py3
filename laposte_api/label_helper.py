# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author David BEAL <david.beal@akretion.com>
#
##############################################################################

from datetime import datetime

from .exception_helper import (InvalidMissingField,  # InvalidDate,
                               InvalidSize, InvalidType, InvalidValueNotInList)

# from . exception_helper import (
#     InvalidSize,
#     InvalidType,
#     InvalidValueNotInList,
#     InvalidMissingField,
#     #InvalidDate,
# )


class AbstractLabel(object):

    def check_model(self, datas, model, model_name=''):
        """
        Keys description in model
        - fields with 'required' key :
            * not required are fill with '' if they are not given
            * required doesn't accept '' value
        - 'type' key : if you provide a type, this type is check first before
                                                                    other keys
        - 'date' key : accepted type for date : str or datetime
                                                        (convert one to other)
        - 'min_size' and 'max_size' : this is used for str or unicode
        - 'min_number' and 'max_number' : this is used for int or float
        keys examples:
        model = {
            'my_field':     {'max_size': 35, 'required': True},
            'my_date':      {'date': '%d/%m/%Y'},
            "weight":       {'max_number': 50, 'type': float},
        }

        Carefull cases considered in this script (search each 'case' string
        in source code below):
            Case 1/ key in model with not in datas :
                    => no check but with a default value '' (only for display)
            Case 2/ key in datas but with a False value (string with no value :
                empty or Null value according to database) :
                    => no check but with a default value ''
            Case 3/ data == 0.0 or 0 which is considered like False but is not :
                    => check but convert in string
        """
        if model_name:
            model_name = '(model: ' + model_name + ')'
        for field, definition in model.items():
            #check type before all other checks if requested in model
            if 'type' in definition and field in datas:
                self.check_type(field, [definition['type']], datas[field])
            to_check = self.must_be_checked(datas, field)
            for key, val in definition.items():
                if to_check:
                    data = datas[field]
                    size = self.evaluate_size_according_to_type(data)
                    if key == 'max_size':
                        self.check_type(field, [str], data)
                        if size > val:
                            raise InvalidSize(
                                "Max size for field '%s' is "
                                "%s :  %s given\nCurrent field value : %s"
                                % (field, val, size, data))
                    elif key == 'min_size':
                        self.check_type(field, [str], data)
                        if size < val:
                            raise InvalidSize(
                                "Min size for field '%s' is "
                                "%s :  %s given\nCurrent field value : %s"
                                % (field, val, size, data))
                    elif key == 'min_number':
                        self.check_type(field, [int, float], data)
                        if size < val:
                            raise InvalidSize(
                                "Min number for field '%s' is "
                                "%s :  %s given" % (field, val, size))
                    elif key == 'max_number':
                        self.check_type(field, [int, float], data)
                        if size > val:
                            raise InvalidSize(
                                "Max number for field '%s' is "
                                "%s :  %s given" % (field, val, size))
                    elif key == 'in' and data not in val:
                        raise InvalidValueNotInList(
                            "field '%s' with value '%s' must belong "
                            "to this list %s"
                            % (field, data, val))
                    elif key == 'date':
                        self.check_type(field, [str, datetime], data)
                        if isinstance(data, datetime):
                            try:
                                datas[field] = datetime.strftime(data, val)
                            except:
                                raise InvalidType(
                                    "The date '%s' must be in the format '%s'"
                                    % (data, val))
                        elif isinstance(data, str):
                            try:
                                datas[field] = \
                                    datetime.strptime(data, val).strftime(val)
                            except:
                                raise InvalidType(
                                    "The date '%s' must be in the format '%s'"
                                    % (data, val))
                    elif key == 'numeric':
                        #TODO : to end
                        self.check_type(field, [int, float], data)
                        datas[field] = val % data
                    data = ''
                else:
                    if key == 'required' and val is True:
                        raise InvalidMissingField(
                            "Required field '%s' is missing %s"
                            % (field, model_name))
                    else:
                        # must have an empty value to be called
                        # in python template (mako, jinja2, etc)
                        if field not in datas:
                            #case 1/
                            datas[field] = ''
                        elif type(datas[field]) == bool:
                            #case 2/
                            datas[field] = ''
            # case 3/
            if type(datas[field]) in [int, float]:
                datas[field] = str(datas[field])
        return datas

    def must_be_checked(self, datas, field):
        res = True
        if field in datas:
            if type(datas[field]) in [str, bool]:
                if datas[field] is False:
                    res = False
        else:
            res = False
        return res

    def evaluate_size_according_to_type(self, data):
        "Used to simplify the code in check_model()"
        res = ''
        if type(data) in [str]:
            res = len(data)
        elif type(data) in [int, float]:
            res = data
        return res

    def check_type(self, field, types, data):
        if type(data) not in types:
            string_types = "' or '".join([elm.__name__ for elm in types])
            raise InvalidType(
                "'%s' field must be in '%s' type : '%s' given"
                % (field, string_types, type(data).__name__))
        return True
