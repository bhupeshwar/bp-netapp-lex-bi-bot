#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

ORIGINAL_VALUE = 0
TOP_RESOLUTION = 1

SLOT_CONFIG = {
    'dl_name':       {'type': TOP_RESOLUTION, 'remember': True,  'error': 'I couldn\'t find an DL called "{}".'},
    'month':      {'type': ORIGINAL_VALUE, 'remember': True},
    'dl_date':      {'type': ORIGINAL_VALUE, 'remember': True},
    'job_date':      {'type': ORIGINAL_VALUE, 'remember': True},
    'template_name':         {'type': TOP_RESOLUTION, 'remember': True,  'error': 'I couldn\'t find a template called "{}".'},
    'count':            {'type': ORIGINAL_VALUE, 'remember': True},
    'dimension':        {'type': ORIGINAL_VALUE, 'remember': True}    
}

DIMENSIONS = {
    'dl_name':     {'slot': 'dl_name',  'column': 'dl.dl_name',  'singular': 'dl_name'},
    'month':     {'slot': 'dl_date', 'column': 'd.month',       'singular': 'month'},
    'dl_date':     {'slot': 'dl_date', 'column': 'dl.end_date',       'singular': 'dl_date'},
    'job_date':     {'slot': 'job_date', 'column': 'dl.end_date',       'singular': 'job_date'},
    'template_name':     {'slot': 'template_name',  'column': 'dmd.template_name',  'singular': 'template_name'}
}


class SlotError(Exception):
    pass
