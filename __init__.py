# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QgisToUGCS
                                 A QGIS plugin
 A Plugin to create UGCS missions from GPKG layers
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-01-09
        copyright            : (C) 2024 by Vincent Bénet
        email                : vincent.benet@outlook.fr
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
    """Load QgisToUGCS class from file QgisToUGCS.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qgis_to_ugcs import QgisToUGCS
    return QgisToUGCS(iface)