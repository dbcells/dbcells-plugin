# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DBCellsPlugin
                                 A QGIS plugin
 Plugin to load data from dbcells
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-11-06
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Nerval Junior
        email                : nerval.junior@discente.ufma.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import *
from osgeo import ogr
import os
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .dbcells_plugin_dialog import DBCellsPluginDialog
import os.path

  
from qgis.core import (  Qgis,  QgsMultiPolygon,)
from qgis.utils import *


plugin_dir = os.path.dirname(__file__)

try:
    import pip
except:
    execfile(os.path.join(plugin_dir, get_pip.py))
    import pip
    # just in case the included version is old
    pip.main(['install','--upgrade','pip'])


from simpot import serialize_to_rdf_file, RdfsClass, BNamespace

from rdflib import Namespace, Literal,RDF
from rdflib.namespace import DC, FOAF


CELL = Namespace("http://purl.org/ontology/dbcells/cells#")
GEO = Namespace ("http://www.opengis.net/ont/geosparql#")


class Cell ():
    
    asWkt = GEO.asWKT
    resolution = CELL.resolution
    
    @RdfsClass(CELL.Cell,"http://www.dbcells.org/epsg4326/")
    @BNamespace('geo', GEO)
    @BNamespace('cells', CELL)
    def __init__(self, dict):
        self.id = dict["id"]
        if ('asWkt' in dict):
            self.asWkt = Literal(dict["asWkt"])
          
class DBCellsPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DBCellsPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&DBCels Plugin')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DBCellsPlugin', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/dbcells_plugin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Add Layer from DBCells'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&DBCels Plugin'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = DBCellsPluginDialog()

        self.dlg.buttonSPARQL.clicked.connect(self.inputFile)
        
        self.dlg.buttonBox.accepted.connect(self.saveFile)
        self.dlg.buttonBox.rejected.connect(self.close)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def inputFile (self):
        self.file_name=str(QFileDialog.getOpenFileName(caption="Defining input file", filter="Terse RDF Triple Language(*.ttl)")[0])
        self.dlg.lineSPARQL.setText(self.file_name)
        self.abrirSPARQL()
        
        
        
    def abrirSPARQL(self):
                # abrir um arquivo dado na interface
        with open(self.file_name, 'r') as file:
            data = file.read().replace('\n', ' ').upper()
            tokens = data.split(" ")
            start = tokens.index('SELECT') + 1
            end = tokens.index('WHERE')
            self.attributes = tokens[start:end] #identificar os atributos
            print (self.attributes)
            for i in self.attributes:
                self.dlg.comboID.addItem(i.replace("?",""))
             
        with open(self.file_name, 'r') as file:
            data = file.read().replace('\n', ' ').upper()
            tokens = data.split(" ")
            start = tokens.index('SELECT') + 1
            end = tokens.index('WHERE')
            self.attributes = tokens[start:end] #identificar os atributos
            print (self.attributes)
            for i in self.attributes:
               self.dlg.colGeometria.addItem(i.replace("?",""))
        
           
        
    def saveFile(self):
        layer = self.iface.activeLayer()

        if self.dlg.buscaCamada.text():
            features = layer.selectedFeatures() 
        else:
            features = layer.getFeatures()

        cells = []
        for feature in features:
            pol = QgsMultiPolygon()
            pol.fromWkt (feature.geometry().asWkt())
            cell = {
                "id": str(feature[self.dlg.comboID.currentText()])
            }
            if self.dlg.colGeometria.currentText():
                features = layer.selectedFeatures() 
                pol = QgsMultiPolygon()
                pol.fromWkt (feature.geometry().asWkt())
                cell['asWkt'] = pol.polygonN(0).asWkt()

            cells.append (cell)
            print (cell)
        fileName = self.dlg.buscaCamada.text()
        self.iface.messageBar().pushMessage(
            "Success", "Input file written at " + fileName,
            level=Qgis.Success, duration=3
        )

        serialize_to_rdf_file(cells, Cell, fileName)
            
    def close(self):
        self.dlg.setVisible(False)   
  

              