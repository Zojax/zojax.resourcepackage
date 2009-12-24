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
from threading import local
from zope import interface
from zope.site.hooks import getSite
from zope.traversing.browser import absoluteURL
from zope.component import queryUtility, queryAdapter

from interfaces import IPackage, ILibrary


class IncludesInfo(local):
    site = None
    libraries = []
    sources = []

includes = IncludesInfo()


class Library(object):
    interface.implements(ILibrary)

    def __init__(self, name):
        self.name = name
        self.require = []
        self.packages = []

    def add(self, package, require):
        if package not in self.packages:
            self.packages.append(package)

        for req in require:
            if req not in self.require:
                self.require.append(req)

    def render(self, request):
        result = []
        siteUrl = absoluteURL(getSite(), request)
        for package in self.packages:
            package = queryAdapter(request, IPackage, name=package)
            if package is not None:
                extra = []
                hasResources = False
                for resource in package.resources(request):
                    if resource.standalone:
                        extra.append(resource.link(request, siteUrl))
                    else:
                        hasResources = True

                if hasResources:
                    result.append(package.link(request, siteUrl))

                result.extend(extra)

        return '\n' + '\n'.join(result)


def include(library):
    includes.libraries.append(library)


def includeInplaceSource(source, required=()):
    for lib in required:
        includes.libraries.append(lib)
    includes.sources.append(source)


def processLibrary(library, ids, objects):
    if library in ids:
        return

    lib = queryUtility(ILibrary, name=library)
    if lib is not None:
        for require in lib.require:
            processLibrary(require, ids, objects)

        if library in ids:
            #possible reqursion
            return

        ids.append(library)
        objects[library] = lib


def renderResourceLinks(request, clear=True):
    global includes

    libIds = []
    libObjects = {}

    for library in includes.libraries:
        processLibrary(library, libIds, libObjects)

    result = u'\n'.join([libObjects[libId].render(request) for libId in libIds])
    if includes.sources:
        result = '%s\n%s'%(result, '\n'.join(includes.sources))

    if clear:
        includes.libraries = []
        includes.sources = []

    return result
