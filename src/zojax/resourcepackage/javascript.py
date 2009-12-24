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

from packer import JavascriptPacker
from package import Package
from resource import Resource

packer = JavascriptPacker('save')


class Javascript(Resource):

    def __init__(self, name, path, resource, compression='none', **kw):
        super(Javascript, self).__init__(name, path, resource, **kw)

        self.compression = compression
        self.resource_path = '@@/%s'%(path or name)

    def render(self, request, compress=True):
        content = super(Javascript, self).render(request, compress)

        if compress and self.compression == 'yes':
            content = packer.pack(content)

        url = '%s/%s'%(
            str(getMultiAdapter((getSite(), request), IAbsoluteURL)),
            self.resource_path)

        return '/* %s */\n%s' % (url.encode('utf-8'), content)

    def link(self, request, siteUrl):
        if self.resource:
            return '<script type="text/javascript" src="%s/@@/%s"></script>'%(
                siteUrl, self.name)
        else:
            return '<script type="text/javascript" src="%s/@@/%s"></script>'%(
                siteUrl, self._url)


class JavascriptPackage(Package):
    type = u'javascript'
    content_type = u'text/javascript'

    def link(self, request, siteUrl):
        return '<script type="text/javascript" src="%s"></script>'%self()

    def render(self, request):
        return super(JavascriptPackage, self).render(request)
