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
""" test setup

$Id$
"""
__docformat__ = "reStructuredText"

import doctest, unittest
from zope import component, interface
from zope.app.testing import setup, placelesssetup
from zope.traversing import testing
from zope.traversing.interfaces import ITraversable
from zope.traversing.namespace import view
from zope.browserresource.file import FileResource, FileResourceFactory
from zope.browserresource.interfaces import IResourceFactoryFactory
from z3c.zrtresource import zrtresource
from z3c.zrtresource.interfaces import IZRTCommandFactory
from zojax.cssregistry.registry import CSSRegistry
from zojax.cssregistry import zcml, command, property, interfaces
from zojax.resourcepackage import javascript, stylesheet, inplace, package
from zojax.resourcepackage.interfaces import \
    IPackageFactory, IPackageResourceFactory


def setUp(test):
    placelesssetup.setUp(test)

    component.provideUtility(
        FileResourceFactory, IResourceFactoryFactory)
    component.provideUtility(
        FileResourceFactory, IResourceFactoryFactory, name='file')
    component.provideUtility(
        zrtresource.ZRTFileResourceFactory, IResourceFactoryFactory, name='zrt')
    component.provideUtility(
        command.cssregistry_factory, IZRTCommandFactory, 'cssregistry')

    registry = CSSRegistry()
    registry['fontColor']= property.Property('fontColor', '#11111111')
    registry['fontFamily']= property.Property('fontFamily', 'Verdana')

    component.provideAdapter(
        zcml.Factory(registry),
        (interfaces.ICSSRegistryLayer, interfaces.ICSSRegistryLayer,
         interface.Interface), interfaces.ICSSRegistry, '')

    sm = component.getSiteManager()
    sm.registerUtility(
        inplace.InplacePackage, IPackageFactory, name='inplace')
    sm.registerUtility(
        inplace.Inplace, IPackageResourceFactory, name='inplace')
    sm.registerUtility(
        javascript.JavascriptPackage, IPackageFactory, name='javascript')
    sm.registerUtility(
        javascript.Javascript, IPackageResourceFactory, name='javascript')
    sm.registerUtility(
        stylesheet.StylesheetPackage, IPackageFactory, name='stylesheet')
    sm.registerUtility(
        stylesheet.Stylesheet, IPackageResourceFactory, name='stylesheet')
    sm.registerAdapter(package.PackageCache)
    component.provideAdapter(view, (None, None), ITraversable, name="view")
    setup.setUpTestAsModule(test, 'zojax.resourcepackage.TESTS')


def tearDown(test):
    placelesssetup.tearDown(test)
    setup.tearDownTestAsModule(test)


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'tests.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocFileSuite(
                'resourcedirectory.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
         ))
