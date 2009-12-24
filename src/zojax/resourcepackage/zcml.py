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
import time, random, os.path
from zope import schema, interface, component

from zope.component.zcml import handler
from zope.component import getUtility, queryUtility, getGlobalSiteManager
from zope.interface.interface import InterfaceClass

from zope.configuration.fields import Path, Tokens, GlobalObject
from zope.configuration.exceptions import ConfigurationError
from zope.security.checker import CheckerPublic, NamesChecker
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.browserresource.file import FileResourceFactory
from zope.browserresource.metaconfigure import allowed_names
from zope.browserresource.interfaces import IResourceFactoryFactory

from library import Library
from interfaces import ILibrary, IPackage, IPackageFactory
from interfaces import IPackageResource, IPackageResourceFactory


class IResourcePackageDirective(interface.Interface):
    """ resource package """

    name = schema.TextLine(
        title = u'Name',
        required = True)

    type = schema.TextLine(
        title = u'Type',
        required = True)

    title = schema.TextLine(
        title = u'Title',
        required = False)

    order = schema.Int(
        title = u'Order',
        required = False)

    layer = GlobalObject(
        title=u"The layer the resource package should be found in",
        required=False)

    library = schema.TextLine(
        title = u'Library',
        description = u'Define this package as "library".',
        required = True)

    require = Tokens(
        title = u'Require',
        value_type = schema.TextLine(),
        required = False)

IResourcePackageDirective.setTaggedValue('keyword_arguments', True)


class IResourceSubDirective(interface.Interface):
    """ package resource """

    name = schema.TextLine(
        title = u'Name',
        required = False)

    path = schema.TextLine(
        title = u'Path',
        description = u'Resource path.',
        required = True)

    standalone = schema.Bool(
        title = u'Standalone',
        default = False,
        required = False)

# Arbitrary keys and values are allowed to be passed to the Resource.
IResourceSubDirective.setTaggedValue('keyword_arguments', True)


class IResourceIncludeDirective(interface.Interface):
    """ resourceinclude directive """

    name = schema.TextLine(
        title = u'Name',
        required = True)

    library = schema.TextLine(
        title = u'Library',
        required = True)

    type = schema.TextLine(
        title = u'Type',
        required = True)

    path = schema.TextLine(
        title = u'Path',
        description = u'Resource path.',
        required = False)

    file = Path(
        title = u'Filename',
        required = False)

    filetype = schema.TextLine(
        title = u'File resource type',
        required = False)

    layer = GlobalObject(
        title = u"The layer the resource package should be found in",
        required = False)

    require = Tokens(
        title = u'Require',
        value_type = schema.TextLine(),
        required = False)

    standalone = schema.Bool(
        title = u'Standalone',
        default = False,
        required = False)

IResourceIncludeDirective.setTaggedValue('keyword_arguments', True)


class Factory(object):

    def __init__(self, package):
        self.package = package

    def __call__(self, request):
        return self.package.__bind__(request)


class IPackageInfo(interface.Interface):
    """ package information """

class PackageInfo(object):
    interface.implements(IPackageInfo)

    def __init__(self, name, layer, marker, package):
        self.name = name
        self.layer = layer
        self.marker = marker
        self.package = package

    def __call__(self, request, marker):
        return self


_idx = 1
_packages = {}
_libraries = {}

class resourcePackageHandler(object):

    def __init__(self, _context, name, type,
                 title='', order=0, layer=IDefaultBrowserLayer,
                 library=u'default', require=(), **kw):
        self.name = name
        self.type = type
        self.layer = layer
        self.library = library
        self.require = require

        _context.action(
            discriminator = ('zojax:resourcepackage:handler', name, hash(self)),
            callable = package,
            args = (name, type, title, order, layer, library, require))

    def resource(self, _context, path, name='', **kwargs):
        global _idx
        _idx = _idx + 1
        kwargs['order'] = _idx

        if not name:
            name = str(_idx)

        _context.action(
            discriminator = ('zojax:resourcepackage:resource', self.name, self.layer, path, name),
            callable = resource,
            args = (self.layer, self.library, self.type, name, path, kwargs))


def package(name, type, title, order, layer, library, require):
    global _libraries, _packages

    sm = getGlobalSiteManager()

    # create marker interface
    marker = _libraries.get((library, type))
    if marker is None:
        uid = str(random.randint(0, 9999999))
        marker = InterfaceClass('IPackage%s'%uid, (interface.Interface,),
                                __doc__='Package: %s' %name,
                                __module__='zojax.resourcepackage')
        _libraries[(library, type)] = marker

    # check if package already registered
    packageInfo = None
    for (_layer, _library, _type), _packageInfo in _packages.items():
        if _library == library and layer.isOrExtends(_layer) and _type == type:
            packageInfo = _packageInfo
    if packageInfo is not None:
        # register library
        if library:
            lib = sm.queryUtility(ILibrary, name=library)
            if lib is None:
                lib = Library(library)
                handler('registerUtility', lib, ILibrary, library)

            lib.add(name, require)

        return

    # create package
    package = getUtility(IPackageFactory, type)(name, order, title)
    interface.directlyProvides(package, marker)

    factory = Factory(package)

    # register resource
    sm.registerAdapter(factory, (layer, ), interface.Interface, name)
    sm.registerAdapter(factory, (layer, ), IPackage, name)

    # register package info
    packageInfo = PackageInfo(library, layer, marker, package)
    _packages[(layer, library, type)] = packageInfo

    # register library
    if library:
        lib = sm.queryUtility(ILibrary, name=library)
        if lib is None:
            lib = Library(library)
            handler('registerUtility', lib, ILibrary, library)

        lib.add(name, require)


def resource(layer, library, type, name, path, kw):
    sm = getGlobalSiteManager()

    for (_layer, _library, _type), packageInfo in _packages.items():
        if _library == library and layer.isOrExtends(_layer) and _type == type:
            factory = getUtility(IPackageResourceFactory, type)
            resource = factory('', path, None, **kw)
            sm.registerAdapter(
                resource, (layer, packageInfo.marker), IPackageResource, name)
            return

    raise ConfigurationError()


def resourceIncludeHandler(
    _context, name, library, type,
    path=u'', file=u'', filetype='',
    layer=IDefaultBrowserLayer, require=(), standalone=False, **kw):

    if type == 'stylesheet':
        pname = '%s.css'%library
    elif type == 'javascript':
        pname = '%s.js'%library
    else:
        pname = '%s.%s'%(library, type)

    _context.action(
        discriminator = ('zojax:resourcepackage:package', name, library, layer),
        callable = package,
        args = (pname, type, '', 999, layer, library, require))

    if path and file:
        raise ConfigurationError("Can't define path and file at the same time.")

    if not path and not file:
        raise ConfigurationError('path or file are required.')

    _context.action(
        discriminator = ('zojax:resourcepackage:resourceinclude', name, library, layer),
        callable = resourceInclude,
        args = (name, layer, library, type, path, file, filetype, standalone, kw))


def resourceInclude(name, layer, library, type,
                    path, file, filetype, standalone, kw):
    sm = getGlobalSiteManager()

    for (_layer, _library, _type), packageInfo in _packages.items():
        if _library == library and layer.isOrExtends(_layer) and _type == type:
            factory = getUtility(IPackageResourceFactory, type)

            global _idx
            _idx = _idx + 1
            kw['order'] = _idx
            kw['standalone'] = standalone

            resourceFactory = None

            if file:
                if filetype:
                    rfactory = queryUtility(IResourceFactoryFactory, filetype)
                else:
                    filetype = os.path.splitext(os.path.normcase(name))[1][1:]
                    rfactory = queryUtility(IResourceFactoryFactory, filetype)

                if rfactory is None:
                    rfactory = FileResourceFactory

                checker = NamesChecker(allowed_names, CheckerPublic)
                resourceFactory = rfactory(file, checker, name)

                handler('registerAdapter',
                        resourceFactory, (layer,), interface.Interface, name)

            resource = factory(name, path, resourceFactory, **kw)
            sm.registerAdapter(
                resource, (layer, packageInfo.marker), IPackageResource, name)
            return

    raise ConfigurationError()
