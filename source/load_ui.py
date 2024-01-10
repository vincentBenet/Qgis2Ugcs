import os.path
from pathlib import Path

from qgis.core import QgsProject
from qgis.core import QgsRasterLayer
from PyQt5.QtWidgets import QFileDialog


def text_edit_template(dialog):
    version = dialog.ugcs_version.currentText()
    path_template = os.path.join(
        os.path.dirname(__file__),
        f"template_ugcs_mission_{version}.json"
    )
    dialog.template_path.setText(path_template)


def buttons(dialog):
    dialog.output_button.clicked.connect(
        lambda: dialog.output_path.setText(
            QFileDialog.getSaveFileName(filter='*.json')[0]))
    dialog.template_button.clicked.connect(
        lambda: dialog.output_path.setText(
            QFileDialog.getSaveFileName(filter='*.json')[0])
    )


def combo_boxs(dialog):
    dialog.input_layer.clear()
    layers = QgsProject.instance().mapLayers()
    for layer_key, layer in layers.items():
        if isinstance(layer, QgsRasterLayer):  # Raster
            continue
        elif layer.wkbType() == 1:  # Point
            continue
        elif layer.wkbType() == 2:  # Line
            dialog.input_layer.addItem(layer_key)
        elif layer.wkbType() == 3:  # Polygon
            continue
        elif layer.wkbType() == 100:  # No Geometry
            continue
        else:  # Custom Geometry
            continue

    dialog.ugcs_version.clear()
    start = "template_ugcs_mission_"
    end = ".json"
    [
        dialog.ugcs_version.addItem(file[len(start):-len(end)])
        for file in sorted(os.listdir(os.path.dirname(__file__)))
        if file.startswith(start) and file.endswith(end)
    ]
    dialog.ugcs_version.currentTextChanged.connect(lambda: text_edit_template(dialog))


def text_edit(dialog):
    dialog.output_path.setText(os.path.join(
        Path.home(),
        "mission.json"
    ))
    text_edit_template(dialog)




def main(dialog):
    buttons(dialog)
    combo_boxs(dialog)
    text_edit(dialog)
