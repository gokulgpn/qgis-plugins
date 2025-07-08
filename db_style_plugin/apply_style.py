from qgis.PyQt.QtWidgets import QAction, QComboBox, QPushButton, QVBoxLayout, QWidget, QLabel
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject, QgsVectorLayer
from qgis.utils import iface
import psycopg2
import tempfile
import os

class DbStylePlugin:
    def __init__(self, iface):
        self.iface = iface
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.action = QAction(QIcon(icon_path), "Apply DB Style", iface.mainWindow())
        self.action.triggered.connect(self.run)

    def initGui(self):
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("DB Styling", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("DB Styling", self.action)

    def run(self):
        self.dialog = QWidget()
        self.dialog.setWindowTitle("Apply Style from DB")

        self.layer_select = QComboBox()
        self.style_select = QComboBox()
        self.apply_button = QPushButton("Apply Style")

        # Labels for clarity
        layer_label = QLabel("Select the input layer to be styled:")
        style_label = QLabel("Select the style source from the database:")

        # Populate input layer dropdown
        self.layer_map = {}
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer):
                name = layer.name()
                self.layer_select.addItem(name)
                self.layer_map[name] = layer

        # Populate styles from DB
        self.styles = self.fetch_styles()
        self.style_map = {}
        for s in self.styles:
            display = f"{s['f_table_name']} → {s['stylename']}"
            self.style_select.addItem(display)
            self.style_map[display] = s

        self.apply_button.clicked.connect(self.apply_style)

        layout = QVBoxLayout()
        layout.addWidget(layer_label)
        layout.addWidget(self.layer_select)
        layout.addWidget(style_label)
        layout.addWidget(self.style_select)
        layout.addWidget(self.apply_button)
        self.dialog.setLayout(layout)
        self.dialog.show()

    def fetch_styles(self):
        try:
            conn = psycopg2.connect(
                dbname='database_name',
                user='username',
                password='your_password',
                host='localhost',
                port='5432'
            )
            cur = conn.cursor()
            cur.execute("""
                SELECT f_table_schema, f_table_name, stylename, styleqml
                FROM public.layer_styles
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()

            return [
                {
                    'f_table_schema': r[0],
                    'f_table_name': r[1],
                    'stylename': r[2],
                    'styleqml': r[3]
                } for r in rows
            ]

        except Exception as e:
            self.iface.messageBar().pushMessage("DB Error", str(e), level=3)
            return []

    def apply_style(self):
        selected_layer_name = self.layer_select.currentText()
        selected_style_text = self.style_select.currentText()

        layer = self.layer_map.get(selected_layer_name)
        style_info = self.style_map.get(selected_style_text)

        if not layer:
            self.iface.messageBar().pushMessage("Error", "Selected layer not found.", level=3)
            return

        if not style_info:
            self.iface.messageBar().pushMessage("Error", "Selected style not found.", level=3)
            return

        try:
            qml_string = style_info['styleqml']
            with tempfile.NamedTemporaryFile(suffix=".qml", delete=False) as f:
                f.write(qml_string.encode('utf-8'))
                temp_path = f.name

            layer.loadNamedStyle(temp_path)
            layer.triggerRepaint()
            self.iface.messageBar().pushMessage("Success", f"Style '{style_info['stylename']}' applied to layer '{selected_layer_name}'.", level=0)
        except Exception as e:
            self.iface.messageBar().pushMessage("Style Error", str(e), level=3)
