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
from zope.app.component.hooks import getSite
from zope.traversing.browser.interfaces import IAbsoluteURL

from packer import CSSPacker
from package import Package, PackageFactory
from resource import Resource, ResourceFactory

packers = {'full': CSSPacker('full'),
           'save': CSSPacker('save')}


class Stylesheet(Resource):

    def __init__(self, name, path, resource, media='',
                 rel='stylesheet', compression='full', **kw):
        super(Stylesheet, self).__init__(name, path, resource, **kw)

        self.rel = rel
        self.media = media
        self.compression = compression
        self.resource_path = '@@/%s'%(path or name)

    def render(self, request, compress=False):
        content = super(Stylesheet, self).render(request, compress)

        if compress:
            packer = packers.get(self.compression, None)
            if packer is not None:
                content = packer.pack(content)

        url = '%s/%s'%(
            str(getMultiAdapter((getSite(), request), IAbsoluteURL)),
            self.resource_path)
        content = ' /* %s */\n%s'%(url, content)

        if self.media:
            content = '@media %s { %s}' % (self.media, content)

        return content

    def link(self, request, siteUrl):
        if self.resource:
            return '<link rel="stylesheet" type="text/css" href="%s/@@/%s" />'%(
                siteUrl, self.name)
        else:
            return '<link rel="stylesheet" type="text/css" href="%s/@@/%s" />'%(
                siteUrl, self._url)


class StylesheetPackage(Package):
    type = u'stylesheet'
    content_type = u'text/css'

    def link(self, request, siteUrl):
        return '<link rel="stylesheet" type="text/css" href="%s" />'%self()

    def render(self, request):
        return super(StylesheetPackage, self).render(request)


packageFactory = PackageFactory(StylesheetPackage)
resourceFactory = ResourceFactory(Stylesheet)
