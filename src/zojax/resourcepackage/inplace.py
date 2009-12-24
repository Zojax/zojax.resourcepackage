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
from zope.component import getMultiAdapter
from zope.site.hooks import getSite
from zope.traversing.browser.interfaces import IAbsoluteURL

from package import Package
from resource import Resource


class Inplace(Resource):

    def link(self, request, siteUrl):
        return self.render(request)


class InplacePackage(Package):
    type = u'inplace'
    content_type = u'text/plain'

    def link(self, request, siteUrl):
        return self.render(request)
