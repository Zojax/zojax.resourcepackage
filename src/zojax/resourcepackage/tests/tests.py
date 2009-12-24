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
from zope import component
from zope.app.testing import setup, placelesssetup
from zope.traversing import testing
from zope.traversing.interfaces import ITraversable
from zope.traversing.namespace import view
from zope.app.publisher.browser.fileresource import FileResource
from zojax.resource import fileresource
from zojax.resource.interfaces import IResourceFactoryType
from zojax.resourcepackage import javascript, stylesheet, inplace


def setUp(test):
    placelesssetup.setUp(test)

    component.provideUtility(
        fileresource.filefactory, IResourceFactoryType)

    component.provideUtility(inplace.packageFactory, name='inplace')
    component.provideUtility(inplace.resourceFactory, name='inplace')
    component.provideUtility(javascript.packageFactory, name='javascript')
    component.provideUtility(javascript.resourceFactory, name='javascript')
    component.provideUtility(stylesheet.packageFactory, name='stylesheet')
    component.provideUtility(stylesheet.resourceFactory, name='stylesheet')
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
         ))
