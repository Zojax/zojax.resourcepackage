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
import md5

from zope import interface, component
from zope.component import getUtility, getAdapters, getMultiAdapter

from zope.datetime import rfc1123_date
from zope.datetime import weekday_abbr, monthname
from zope.datetime import time as timeFromDateTimeString

from zope.app.component.hooks import getSite
from zope.app.component.interfaces import ISite
from zope.traversing.browser import absoluteURL
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.app.publisher.browser.resource import Resource

from zojax.cacheheaders.interfaces import ICacheStrategy

from interfaces import \
    IPackage, IBoundPackage, IPackageResource, IPackageFactory


class Package(Resource):
    interface.implements(IPackage, IBrowserPublisher)

    type = ''
    content_type = 'text/*'

    def __init__(self, name, order, title):
        self.__name__ = name

        self.order = order
        self.title = title

    def __bind__(self, request):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.request = request
        interface.alsoProvides(clone, IBoundPackage)
        return clone

    def __stringhash__(self):
        return md5.md5(self.render(self.request)).hexdigest()

    def __call__(self):
        return u'%s/++rspkg++%s/%s'%(
            absoluteURL(getSite(), self.request),self.__stringhash__(),self.__name__)

    def resources(self, request):
        resources = []
        for name, resource in getAdapters((request, self), IPackageResource):
            resources.append((resource.order, resource))

        resources.sort()
        return [r for o, r in resources]

    def publishTraverse(self, request, name):
        '''See interface IBrowserPublisher'''
        if name == self.__stringhash__():
            return self

        raise NotFound(None, name)

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        package = self.__bind__(request)
        return getattr(package, request.method), ()

    def render(self, request):
        """ IResource implementation """
        data = ''
        for resource in self.resources(request):
            if not resource.standalone:
                data = data + resource.render(request) + '\n\n'

        return data

    def GET(self):
        request = self.request
        response = request.response
        response.setHeader('Content-Type', self.content_type)
        return self.render(request)

    def HEAD(self):
        request = self.request
        response = request.response
        response.setHeader('Content-Type', self.content_type)
        return ''


class PackageFactory(object):
    """ Stylesheet package factory """
    interface.implements(IPackageFactory)

    def __init__(self, factory):
        self.factory = factory

    def __call__(self, name, order, title):
        return self.factory(name, order, title)


class PackageCache(object):
    component.adapts(IPackage)
    interface.implements(ICacheStrategy)

    def __init__(self, context):
        self.context = context

    def __bind__(self, request):
        self.request = request
        self.response = request.response
        return self

    def isModified(self):
        header = self.request.getHeader('IF_MODIFIED_SINCE', None, True)

        if header is not None:
            return False

        return True

    def setNotModifiedHeaders(self):
        self.response.setHeader('Content-Type', self.context.content_type)

    def setCacheHeaders(self):
        response = self.response

        response.setHeader('Cache-Control', 'public, max-age=31536000')
        response.setHeader('Expires', u"Fri, 01 Jan 2100 01:01:01 GMT")
        response.setHeader('Last-Modified', u"Sat, 01 Jan 2000 01:01:01 GMT")


class Traversable(object):
    interface.implements(ITraversable)
    component.adapts(ISite, interface.Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        return getMultiAdapter(
            (self.context, self.request), interface.Interface)
