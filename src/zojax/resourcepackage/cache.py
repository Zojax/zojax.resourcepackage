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
from zojax.cache.tag import SiteTag
from zojax.cache.view import cache

from package import Package, PackageCache
from stylesheet import StylesheetPackage
from javascript import JavascriptPackage

ResourcePackageTag = SiteTag('resourcepackage')
StylesResourcePackageTag = SiteTag('resourcepackage:css')


def updateResourcePackageTag(context, event):
    ResourcePackageTag.update()


def updateStylesResourcePackageTag(context, event):
    StylesResourcePackageTag.update()


def PackageId(instance):
    return u'resourcepackage:%s'%instance.__name__


def PackageCacheId(instance):
    return u'resourcepackage:%s:etag'%instance.__name__


Package.__hash__ = cache(PackageCacheId, ResourcePackageTag)(Package.__hash__)

JavascriptPackage.render = cache(
    PackageId, ResourcePackageTag)(JavascriptPackage.render)

StylesheetPackage.render = cache(
    PackageId, ResourcePackageTag, StylesResourcePackageTag)(
    StylesheetPackage.render)
