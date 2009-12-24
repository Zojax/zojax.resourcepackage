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
from zope import component
from zope.app.component.interfaces import ISite
from zope.app.component.hooks import getSite, setSite
from zope.app.publication.interfaces import IBeforeTraverseEvent

from zojax.resourcepackage import library
from zojax.cacheheaders.interfaces import IAfterCallEvent


@component.adapter(ISite, IBeforeTraverseEvent)
def beginTraverse(site, event):
    includes = library.includes
    includes.site = site
    includes.libraries = []
    includes.sources = []


@component.adapter(IAfterCallEvent)
def afterCallHandler(event):
    includes = library.includes

    if (includes.sources or includes.libraries) and \
            includes.site is not None:
        request = event.request
        response = request.response

        oldSite = getSite()

        setSite(includes.site)

        html = library.renderResourceLinks(request)

        if html:
            body = response.consumeBody()
            pos = body.find('<head>')
            if pos >= 0:
                body = body[:pos+7] + '\n%s\n'%str(html) + body[pos+7:]
            else:
                body = body.replace('<!--resourcepackages-->', str(html), 1)
            response.setResult(body)
        setSite(oldSite)
