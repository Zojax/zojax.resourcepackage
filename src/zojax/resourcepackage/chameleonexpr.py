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
from chameleon.core import types
from chameleon.zpt import expressions
from zojax.resourcepackage.library import include


class ResourcepackageExpression(object):

    def __call__(self, expr):
        include(expr)


class ResourcepackageTranslator(expressions.ExpressionTranslator):

    symbol = '_get_zojax_resourcepackage'
    traverse = ResourcepackageExpression()

    def translate(self, string, escape=None):
        value = types.value("%s('%s')" % (self.symbol, string))
        value.symbol_mapping[self.symbol] = self.traverse

        return value
