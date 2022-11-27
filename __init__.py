# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DBCellsPlugin
                                 A QGIS plugin
 Plugin to load data from dbcells
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-11-06
        copyright            : (C) 2022 by Nerval Junior
        email                : nerval.junior@discente.ufma.br
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DBCellsPlugin class from file DBCellsPlugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .dbcells_plugin import DBCellsPlugin
    return DBCellsPlugin(iface)
