#
# @Author : Bhupeshwar Singh Pathania
# Copyright 2019  UST-global.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import time
import logging

#
# See additional configuration parameters at bottom
#

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# adjust dimension values as necessary prior to inserting into where clause
def pre_process_query_value(key, value):
    logger.debug('<<BIBot>> pre_process_query_value(%s, %s)', key, value)
    value = value.replace("'", "''")    # don't allow any 's in WHERE clause
    if key == 'event_month':
        value = value[0:3]

    logger.debug('<<BIBot>> pre_process_query_value() - returning key=%s, value=%s', key, value)

    return value


# adjust slot values as necessary after reading from intent slots
def post_process_slot_value(key, value):
    logger.debug('<<BIBot>> post_process_slot_value() - returning key=%s, value=%s', key, value)
    return value


def post_process_dimension_output(key, value):
    logger.debug('<<BIBot>> post_process_dimension_output(%s, %s)', key, value)
    if key == 'months':
        value = get_month_name(value)
    logger.debug('<<BIBot>> post_process_dimension_output() - returning key=%s, value=%s', key, value)
    return value


#
# user exit functions for pre- and post-processors
#

def get_month_name(value):
    if not isinstance(value, str): return value
    month_name = MONTH_NAMES.get(value.upper()[0:3])
    return month_name if month_name else value.title()


DIMENSION_FORMATTERS = {
    'dl_name':  {'format': 'For {}',              'function': str.title},
    'sequence_name':  {'format': 'For {}',              'function': str.title},
    'clone_name':  {'format': 'For {}',              'function': str.title},
    'job_date':  {'format': 'On {}',              'function': str.title},
    'dl_date':  {'format': 'On {}',              'function': str.title},
    'event_month': {'format': 'In the month of {}',  'function': get_month_name},
    'template_name':    {'format': 'For {}',              'function': str.title}
}

MONTH_NAMES = {
    "JAN": "January",
    "FEB": "February",
    "MAR": "March",
    "APR": "April",
    "MAY": "May",
    "JUN": "June",
    "JUL": "July",
    "AUG": "August",
    "SEP": "September",
    "OCT": "October",
    "NOV": "November",
    "DEC": "December"
}
