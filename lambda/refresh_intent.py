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

import boto3
import time
import logging
import json
import pprint
import bibot_helpers as helpers
import bibot_userexits as userexits

#
# parameters for Refresh intent
#
REFRESH_QUERY_TEMPLATE = 'SELECT DISTINCT template_name from ba_dashboard_master_details ORDER BY template_name'
REFRESH_QUERY_DL = 'SELECT DISTINCT dl_name from ba_dl ORDER BY dl_name'
REFRESH_SLOT_TEMPLATE = 'template_name'
REFRESH_SLOT_DL = 'dl_name'
REFRESH_INTENT_JOB_DONE = 'Jobdone_Intent'
REFRESH_INTENT_JOB_DONE_TIME = 'Jobdonetime_Intent'
REFRESH_BOT = 'BIBotNetApp'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    logger.debug('<<BIBot>> Lex event info = ' + json.dumps(event))

    session_attributes = event['sessionAttributes']
    logger.debug('<<BIBot>> lambda_handler: session_attributes = ' + json.dumps(session_attributes))

    config_error = helpers.get_bibot_config()
    if config_error is not None:
        return helpers.close(session_attributes, 'Fulfilled',
            {'contentType': 'PlainText', 'content': config_error})
    else:
        return refresh_intent_handler(event, session_attributes)


def refresh_intent_handler(intent_request, session_attributes):
    athena = boto3.client('athena')
    session_attributes['lastIntent'] = None

    # Build and execute query
    logger.debug('<<BIBot>> Athena Query String = ' + REFRESH_QUERY_TEMPLATE)
    logger.debug('<<BIBot>> Athena Query String = ' + REFRESH_QUERY_DL)

    st_values_template = []
    st_values_dl = []
    response_template = helpers.execute_athena_query(REFRESH_QUERY_TEMPLATE)
    response_dl = helpers.execute_athena_query(REFRESH_QUERY_DL)
    logger.debug('<<BIBot>> query response = ' + json.dumps(response_template))
    logger.debug('<<BIBot>> query response = ' + json.dumps(response_dl))

    while len(response_template['ResultSet']['Rows']) > 0:
        for item in response_template['ResultSet']['Rows']:
            st_values_template.append({'value': item['Data'][0]['VarCharValue']})
            logger.debug('<<BIBot>> appending: ' + item['Data'][0]['VarCharValue'])

        try:
            next_token = response_template['NextToken']
            response_template = athena.get_query_results(QueryExecutionId=query_execution_id, NextToken=next_token, MaxResults=100)
            logger.debug('<<BIBot>> additional query response_template = ' + json.dumps(response_template))
        except KeyError:
            break

    while len(response_dl['ResultSet']['Rows']) > 0:
        for item in response_dl['ResultSet']['Rows']:
            st_values_dl.append({'value': item['Data'][0]['VarCharValue']})
            logger.debug('<<BIBot>> appending: ' + item['Data'][0]['VarCharValue'])

        try:
            next_token = response_dl['NextToken']
            response_dl = athena.get_query_results(QueryExecutionId=query_execution_id, NextToken=next_token, MaxResults=100)
            logger.debug('<<BIBot>> additional query response_dl = ' + json.dumps(response_dl))
        except KeyError:
            break

    logger.debug('<<BIBot>> "st_values_template = ' + pprint.pformat(st_values_template))
    logger.debug('<<BIBot>> "st_values_dl = ' + pprint.pformat(st_values_dl))

    lex_models = boto3.client('lex-models')
    response_template = lex_models.get_slot_type(name=REFRESH_SLOT_TEMPLATE, version='$LATEST')
    response_dl = lex_models.get_slot_type(name=REFRESH_SLOT_DL, version='$LATEST')
    logger.debug('<<BIBot>> "boto3 version = ' + boto3.__version__)
    logger.debug('<<BIBot>> "Lex slot template_name = ' + pprint.pformat(response_template, indent=4))
    logger.debug('<<BIBot>> "Lex slot template_name checksum = ' + response_template['checksum'])
    logger.debug('<<BIBot>> "Lex slot template_name valueSelectionStrategy = ' + response_template['valueSelectionStrategy'])

    logger.debug('<<BIBot>> "Lex slot dl_name = ' + pprint.pformat(response_template, indent=4))
    logger.debug('<<BIBot>> "Lex slot dl_name checksum = ' + response_template['checksum'])
    logger.debug('<<BIBot>> "Lex slot dl_name valueSelectionStrategy = ' + response_template['valueSelectionStrategy'])

    try:
        logger.debug('<<BIBot>> "st_values_template = ' + pprint.pformat(st_values_template))
        logger.debug('<<BIBot>> "st_values_dl = ' + pprint.pformat(st_values_dl))

        st_checksum_template = response_template['checksum']
        response_template = lex_models.put_slot_type(name=response_template['name'],
                                            description=response_template['description'],
                                            enumerationValues=st_values_template,
                                            checksum=response_template['checksum'],
                                            valueSelectionStrategy=response_template['valueSelectionStrategy']
                                            )
        st_checksum_dl = response_template['checksum']
        response_dl = lex_models.put_slot_type(name=response_dl['name'],
                                            description=response_dl['description'],
                                            enumerationValues=st_values_dl,
                                            checksum=response_dl['checksum'],
                                            valueSelectionStrategy=response_dl['valueSelectionStrategy']
                                            )
    except KeyError:
        pass

    response_job_done = lex_models.get_intent(name=REFRESH_INTENT_JOB_DONE, version='$LATEST')
    response_job_done_time = lex_models.get_intent(name=REFRESH_INTENT_JOB_DONE_TIME, version='$LATEST')
    logger.debug('<<BIBot>> Lex get-intent = ' + pprint.pformat(response_job_done, indent=4))
    logger.debug('<<BIBot>> Lex get-intent keys = ' + pprint.pformat(response_job_done.keys()))

    logger.debug('<<BIBot>> Lex get-intent = ' + pprint.pformat(response_job_done_time, indent=4))
    logger.debug('<<BIBot>> Lex get-intent keys = ' + pprint.pformat(response_job_done_time.keys()))

    response = lex_models.put_intent(name=response_job_done_time['name'],
                                     description=response_job_done_time['description'],
                                     slots=response_job_done_time['slots'],
                                     sampleUtterances=response_job_done_time['sampleUtterances'],
                                     conclusionStatement=response_job_done_time['conclusionStatement'],
                                     fulfillmentActivity=response_job_done_time['fulfillmentActivity'],
                                     checksum=response_job_done_time['checksum']
                                    )
    response = lex_models.put_intent(name=response_job_done['name'],
                                     description=response_job_done['description'],
                                     slots=response_job_done['slots'],
                                     sampleUtterances=response_job_done['sampleUtterances'],
                                     conclusionStatement=response_job_done['conclusionStatement'],
                                     fulfillmentActivity=response_job_done['fulfillmentActivity'],
                                     checksum=response_job_done['checksum']
                                    )

    response = lex_models.get_bot(name=REFRESH_BOT, versionOrAlias='$LATEST')
    logger.debug('<<BIBot>> Lex bot = ' + pprint.pformat(response, indent=4))

    response = lex_models.put_bot(name=REFRESH_BOT,
                                  description=response['description'],
                                  intents=response['intents'],
                                  clarificationPrompt=response['clarificationPrompt'],
                                  abortStatement=response['abortStatement'],
                                  idleSessionTTLInSeconds=response['idleSessionTTLInSeconds'],
                                  voiceId=response['voiceId'],
                                  processBehavior='SAVE',
                                  locale=response['locale'],
                                  checksum=response['checksum'],
                                  childDirected=response['childDirected']
                                 )

    logger.debug('<<BIBot>> Lex put bot = ' + pprint.pformat(response, indent=4))

    response_string = "I've refreshed the template_name dl_name dimension from the database.  Please rebuild me."
    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})
