from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.button import Button
import csv
import os
import pandas as pd
import subprocess
import platform


class GenEspaldasApp(App):
    def build(self):
        return MyLayout()


class MyLayout(GridLayout):

    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)

        self.excel_path = ''
        self.salida_generador_carpeta = 'salida_del_generador'
        self.salida_illustrator_carpeta = 'salida_de_illustrator'

        self.abrir_carpeta_en_escritorio(self.salida_generador_carpeta)
        self.abrir_carpeta_en_escritorio(self.salida_illustrator_carpeta)

        # drag and drop
        Window.bind(on_drop_file=self._on_file_drop)

        # Layout conf
        self.cols = 1
        self.size_hint_y = 1
        self.drop_ui_layout = BoxLayout(
            size_hint_y=0.75,
            padding=50
        )
        self.action_buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.25
        )

        # Drop inner layout
        self.image = Image(
            source='./assets/drag_and_drop.png',
        )
        self.drop_ui_layout.add_widget(self.image)
        self.add_widget(self.drop_ui_layout)

        # Botones acción
        self.limpiar_salida_button = Button(
            text='Limpiar carpetas',
            background_color=(1, 0, 0, 1),
            font_size=18,
            bold=True,
        )
        self.limpiar_salida_button.bind(on_press=self.callback_empty_folder)
        self.action_buttons_layout.add_widget(self.limpiar_salida_button)
        self.add_widget(self.action_buttons_layout)

    def export_csv_from(self, my_list: list[dict]) -> None:
        # Obtén la ruta al escritorio
        desktop_path = os.path.expanduser("~/Desktop")
        folder_name = self.salida_generador_carpeta
        folder_path = os.path.join(desktop_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        fieldnames = ['Variable1', 'Variable2']

        # Agrupar espaldas por talla
        espaldas_por_talla = {}
        for espalda in my_list:
            talla_str = str(espalda['size'])
            if talla_str not in espaldas_por_talla:
                espaldas_por_talla[talla_str] = []
            espaldas_por_talla[talla_str].append(espalda)

        # Escribir archivos CSV por talla
        for talla_str, current_espaldas in espaldas_por_talla.items():
            csv_file = os.path.join(folder_path, f'{talla_str}.csv')

            # Escribir los datos en el archivo CSV
            with open(csv_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()  # Escribir las cabeceras
                for espalda in current_espaldas:
                    writer.writerow(
                        {'Variable1': espalda['name'], 'Variable2': f'{espalda["number"]:.0f}'})

    def _on_file_drop(self, window, file_path, x, y):
        self.excel_path = file_path.decode('utf-8')
        print('Confirmado')
        self.export_csv_from(self.parse_excel_file(self.excel_path))

    def callback_empty_folder(self, instance):
        os_name = platform.system()
        if os_name == 'Windows':
            desktop_path = os_name.path.join(os_name.path.join(
                os_name.environ['USERPROFILE']), 'Desktop')
        elif os_name == 'Linux' or os_name == 'Darwin':
            desktop_path = os_name.path.join(
                os_name.path.join(os_name.path.expanduser('~')), 'Desktop')
        else:
            print("Sistema operativo no compatible.")
            return

        generator_folder_path = os_name.path.join(
            desktop_path, self.salida_generador_carpeta)
        illustrator_folder_path = os_name.path.join(
            desktop_path, self.salida_illustrator_carpeta)

        self.delete_files_in_folder(generator_folder_path)
        self.delete_files_in_folder(illustrator_folder_path)

    def parse_excel_file(self, path: str) -> list[dict]:
        excel_file_path = path
        col_name_str = 'nombre'
        col_number_str = 'numero'
        col_size_str = 'talla'
        try:
            datos_excel = pd.read_excel(excel_file_path, sheet_name=0)
            data_list = []
            for index, row in datos_excel.iterrows():
                objeto = {
                    'name': row[col_name_str].upper(),
                    'number': row[col_number_str],
                    'size': row[col_size_str]
                }
                data_list.append(objeto)

            return data_list

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    def abrir_carpeta_en_escritorio(self, nombre_carpeta: str):
        sistema_operativo = platform.system()
        if sistema_operativo == 'Windows':
            ruta_escritorio = os.path.join(os.path.join(
                os.environ['USERPROFILE']), 'Desktop')
        elif sistema_operativo == 'Linux' or sistema_operativo == 'Darwin':
            ruta_escritorio = os.path.join(
                os.path.join(os.path.expanduser('~')), 'Desktop')
        else:
            print("Sistema operativo no compatible.")
            return

        ruta_carpeta = os.path.join(ruta_escritorio, nombre_carpeta)

        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)

        subprocess.Popen(['explorer' if sistema_operativo ==
                         'Windows' else 'xdg-open', ruta_carpeta])

    def delete_files_in_folder(self, carpeta: str):
        for archivo in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, archivo)
            try:
                if os.path.isfile(ruta_completa):
                    os.remove(ruta_completa)
            except Exception as e:
                print(f"No se pudo eliminar {ruta_completa}: {e}")



if __name__ == '__main__':
    GenEspaldasApp().run()
