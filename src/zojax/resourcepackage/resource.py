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
from zope import interface
from zope.interface import directlyProvides, directlyProvidedBy

from zojax.resource.interfaces import IResource

from utils import traverse, log_exc
from interfaces import IPackageResource, IPackageResourceFactory


class Resource(object):
    interface.implements(IPackageResource)

    def __init__(self, name, path, resource, standalone=False, order=999, **kw):
        if path.startswith('++resource++'):
            self._url = path[12:]
        else:
            self._url = path

        if isinstance(path, basestring):
            path = path.split('/')
            if len(path) > 1 and not path[-1]:
                # Remove trailing slash
                path.pop()

        path.reverse()
        self.name = name
        self.path = path
        self.resource = resource
        self.standalone = standalone
        self.order = order

    def _get_request(self, request):
        # hack
        env = dict(request._orig_env)
        try:
            del env['HTTP_IF_MODIFIED_SINCE']
        except:
            pass

        new_request = request.__class__(
            body_instream=request._body_instream.getCacheStream(),
            environ=env, response=request.response.retry())

        new_request._vh_root = request._vh_root
        new_request._app_server = request._app_server

        new_request.setPublication(request.publication)
        directlyProvides(new_request, directlyProvidedBy(request))
        return new_request

    def render(self, request, compress=True):
        request = self._get_request(request)

        if self.resource:
            return self.resource(request).GET()

        path = self.path

        resource = traverse(path, request)
        if resource is None:
            return u''

        gresource = IResource(resource, None)
        if gresource is not None:
            try:
                return gresource.render(request)
            except Exception, err:
                log_exc(str(err))
                raise
        else:
            return traverse(path, request).GET()

    def __call__(self, request, package):
        return self


class ResourceFactory(object):
    interface.implements(IPackageResourceFactory)

    def __init__(self, factory):
        self.factory = factory

    def __call__(self, *args, **kw):
        return self.factory(*args, **kw)
