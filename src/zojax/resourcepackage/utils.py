##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
import logging, sys
from zope.component import queryAdapter


def traverse(path, request):
    orig_path = path

    path = list(path)
    name = path.pop()

    resource = queryAdapter(request, name=name)
    if resource is None:
        return None

    while path:
        name = path.pop()
        resource = resource.get(name)

    return resource


def log_exc(msg='', subsystem='zojax.resourcepakcage'):
    log = logging.getLogger(subsystem)
    log.log(logging.ERROR, msg, exc_info=sys.exc_info())
