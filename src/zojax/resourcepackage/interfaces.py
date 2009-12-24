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
""" zojax.resourcepackage interfaces

$Id$
"""
from zope import schema, interface


class IPackageResource(interface.Interface):

    order = interface.Attribute('Order')

    name = schema.TextLine(
        title = u'Name',
        required = False)

    path = schema.TextLine(
        title = u'Resource path',
        required = False)

    resource = schema.TextLine(
        title = u'Resource',
        required = False)

    standalone = schema.Bool(
        title = u'Standalone',
        default = False,
        required = True)

    def link(request, siteUrl):
        """ generate resource link """

    def render(request, compress=True):
        """ render resource, return tuple of resource body and modification time """


class IPackageResourceFactory(interface.Interface):
    """ package resource type """

    def __call__(self, *args, **kw):
        """ create resource """


class IPackage(interface.Interface):
    """ resource package """

    def link(request):
        """ generate package link """

    def resources(request):
        """ package resources """

    def __call__():
        """ url for package """

    def GET():
        """ http GET method """

    def HEAD():
        """ http HEAD method """


class IBoundPackage(interface.Interface):
    """ bound package """


class IPackageFactory(interface.Interface):

    def __call__(name, order, title, cache):
        """ package factory """


class ILibrary(interface.Interface):
    """ library of resource packages """

    name = schema.TextLine(
        title = u'Name',
        description = u'Library name',
        required = True)

    require = interface.Attribute('Require')

    packages = interface.Attribute('Packages')

    def render(request):
        """ render includes """
