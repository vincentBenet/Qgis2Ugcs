import os.path
from qgis.core import QgsProject

from . import ugcs_mission_flight_creation


def main(dialog):
    layers = QgsProject.instance().mapLayers()
    layer_input = dialog.input_layer.currentText()
    layer = layers[layer_input]

    if dialog.input_checkbox.isChecked():
        path_style = os.path.join(os.path.dirname(__file__), "ugcs_mission_flight_creation.qml")
        layer.loadNamedStyle(path_style)

    path_input = layer.source().split("|")[0]
    path_output = dialog.output_path.text()
    print(f"{layer_input = }")
    print(f"{path_input = }")
    print(f"{path_output = }")

    path_template_mission = dialog.template_path.text()

    ugcs_mission_flight_creation.main(
        path_export_mission=path_output,
        path_gpkg=path_input,
        path_template_mission=path_template_mission,
    )

    return path_output, path_input, path_template_mission
