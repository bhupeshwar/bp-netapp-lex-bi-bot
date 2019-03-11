#
# @Author : Bhupeshwar Singh Pathania
# Copyright 2019 UST-global.com, Inc. or its affiliates. All Rights Reserved.
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
import json
import bibot_config as bibot
import bibot_helpers as helpers
import bibot_userexits as userexits

# SELECT statement for JOB_DONE query

"""
JOB_DONE_SELECT = "SELECT count(DL.dl_name) from BA_DL as DL"
JOB_DONE_JOIN = " WHERE DL.status != 'W' "
JOB_DONE_DATE = " AND date_format({}, '%Y-%m-%d')  =  date_format(timestamp'{}', '%Y-%m-%d') "
JOB_DONE_WHERE = " AND LOWER({}) LIKE LOWER('%{}%') "
JOB_DONE_PHRASE = 'job done'
"""

JOB_DONE_SELECT = "SELECT count(dlb.OBJECT_NAME) from FROM ba_dashboard_master_details dmd "
JOB_DONE_JOIN = "JOIN ba_dl_baseline dlb on dmd.BASELINE_ID = dlb.BASELINE_ID JOIN ba_dl_details dld on  dld.BASELINE_ID = dlb.BASELINE_ID WHERE 1=1 "
#JOB_DONE_JOIN = JOB_DONE_JOIN +="  WHERE 1=1 "
JOB_DONE_DATE = " AND date_format({}, '%Y-%m-%d')  =  date_format(timestamp'{}', '%Y-%m-%d')  "
JOB_DONE_WHERE = " AND ( LOWER({}) LIKE LOWER('%{}%') or LOWER(dlb.OBJECT_NAME) LIKE LOWER('%{}%') or LOWER(dmd.TEMPLATE_NAME) LIKE LOWER('%{}%') ) "
#JOB_DONE_OR = " or "
JOB_DONE_GROUPBY = " GROUP BY dld.end_time , dlb.OBJECT_NAME "
JOB_DONE_PHRASE = 'job done'


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    logger.debug('<<BIBot>> Lex event info = ' + json.dumps(event))

    config_error = helpers.get_bibot_config()

    session_attributes = event['sessionAttributes']
    logger.debug('<<BIBot>> lambda_handler: session_attributes = ' + json.dumps(session_attributes))

    if config_error is not None:
        return helpers.close(session_attributes, 'Fulfilled',
            {'contentType': 'PlainText', 'content': config_error})
    else:
        return jobdone_intent_handler(event, session_attributes)


def jobdone_intent_handler(intent_request, session_attributes):
    method_start = time.perf_counter()

    logger.debug('<<BIBot>> jobdone_intent_handler: intent_request = ' + json.dumps(intent_request))
    logger.debug('<<BIBot>> jobdone_intent_handler: session_attributes = ' + json.dumps(session_attributes))

    session_attributes['greetingCount'] = '1'
    session_attributes['resetCount'] = '0'
    session_attributes['finishedCount'] = '0'
    session_attributes['lastIntent'] = 'Jobdone_Intent'

    # Retrieve slot values from the current request
    slot_values = session_attributes.get('slot_values')

    try:
        slot_values = helpers.get_slot_values(slot_values, intent_request)
    except bibot.SlotError as err:
        return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': str(err)})

    logger.debug('<<BIBot>> "jobdone_intent_handler(): slot_values: %s', slot_values)

    # Retrieve "remembered" slot values from session attributes
    slot_values = helpers.get_remembered_slot_values(slot_values, session_attributes)
    logger.debug('<<BIBot>> "jobdone_intent_handler(): slot_values afer get_remembered_slot_values: %s', slot_values)

    # Remember updated slot values
    helpers.remember_slot_values(slot_values, session_attributes)

    # build and execute query
    select_clause = JOB_DONE_SELECT
    where_clause = JOB_DONE_JOIN
    for dimension in bibot.DIMENSIONS:
        slot_key = bibot.DIMENSIONS.get(dimension).get('slot')
        if slot_key == 'dl_date':
            if slot_values[slot_key] is not None:
                value = userexits.pre_process_query_value(slot_key, slot_values[slot_key])
                where_clause += JOB_DONE_DATE.format('DL.end_date',value)
        if slot_values[slot_key] is not None:
            if slot_key != 'dl_date':
                value = userexits.pre_process_query_value(slot_key, slot_values[slot_key])
                where_clause += JOB_DONE_WHERE.format(bibot.DIMENSIONS.get(dimension).get('column'), value)

    query_string = select_clause + where_clause + JOB_DONE_GROUPBY
    """
    response = helpers.execute_athena_query(query_string)

    result = response['ResultSet']['Rows'][1]['Data'][0]
    if result:
        count = result['VarCharValue']
        # build response string
        if count == '0':
            response_string = 'There were no {}'.format(JOB_DONE_PHRASE)
        else:
            response_string = 'Yes, there were {} {}'.format(count, JOB_DONE_PHRASE)

    logger.debug('<<BIBot>> "Count value is: %s' % count)

    """
    response_string = query_string

    # add the English versions of the WHERE clauses
    for dimension in bibot.DIMENSIONS:
        slot_key = bibot.DIMENSIONS[dimension].get('slot')
        logger.debug('<<BIBot>> pre top5_formatter[%s] = %s', slot_key, slot_values.get(slot_key))
        if slot_values.get(slot_key) is not None:
            # the DIMENSION_FORMATTERS perform a post-process functions and then format the output
            if userexits.DIMENSION_FORMATTERS.get(slot_key) is not None:
                output_text = userexits.DIMENSION_FORMATTERS[slot_key]['function'](slot_values.get(slot_key))
                response_string += ' ' + userexits.DIMENSION_FORMATTERS[slot_key]['format'].lower().format(output_text)
                logger.debug('<<BIBot>> dimension_formatter[%s] = %s', slot_key, output_text)

    response_string += '.'

    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})
