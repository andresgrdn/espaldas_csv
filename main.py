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
        self.limpiar_salida_button.bind(on_press=self.callback_limpiar_carpeta)
        self.action_buttons_layout.add_widget(self.limpiar_salida_button)
        self.add_widget(self.action_buttons_layout)

    def exportar_csv_from_list(self, my_list: list[dict]) -> None:
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

        # Escribir archivos CSV por cada talla
        for talla_str, current_espaldas in espaldas_por_talla.items():
            csv_file = os.path.join(folder_path, f'espaldas_{talla_str}.csv')

            # Escribir los datos en el archivo CSV
            with open(csv_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()  # Escribir las cabeceras
                for espalda in current_espaldas:
                    writer.writerow(
                        {'Variable1': espalda['name'], 'Variable2': f'{espalda["number"]:.0f}'})

    def _on_file_drop(self, window, file_path, x, y):
        self.excel_path = file_path.decode('utf-8')
        self.confirm_popup = ConfirmPopup(
            title='Confirmación',
            message=f'¿Procesar archivo {self.excel_path}?',
            callback_yes=self.callback_yes,
            callback_no=self.callback_no,
        )
        self.confirm_popup.open()

    def callback_yes(self, instance):
        print('Confirmado')
        self.exportar_csv_from_list(self.process_excel(self.excel_path))
        self.confirm_popup.dismiss()

    def callback_no(self, instance):
        print('Cancelado')

    def callback_limpiar_carpeta(self, instance):
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

        ruta_carpeta_generada = os.path.join(
            ruta_escritorio, self.salida_generador_carpeta)
        ruta_carpeta_illustrator = os.path.join(
            ruta_escritorio, self.salida_illustrator_carpeta)

        self.borrar_archivos_en_carpeta(ruta_carpeta_generada)
        self.borrar_archivos_en_carpeta(ruta_carpeta_illustrator)

    def process_excel(self, path: str) -> list[dict]:
        archivo_excel = path
        col_name_str = 'nombre'
        col_number_str = 'numero'
        col_size_str = 'talla'
        try:
            datos_excel = pd.read_excel(archivo_excel, sheet_name=0)
            lista_objetos = []
            for index, row in datos_excel.iterrows():
                objeto = {
                    'name': row[col_name_str].upper(),
                    'number': row[col_number_str],
                    'size': row[col_size_str]
                }
                lista_objetos.append(objeto)

            return lista_objetos

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

    def borrar_archivos_en_carpeta(self, carpeta: str):
        for archivo in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, archivo)
            try:
                if os.path.isfile(ruta_completa):
                    os.remove(ruta_completa)
            except Exception as e:
                print(f"No se pudo eliminar {ruta_completa}: {e}")


class ConfirmPopup(Popup):
    def __init__(self, title, message, callback_yes, callback_no, **kwargs):
        super(ConfirmPopup, self).__init__(**kwargs)
        self.title = title
        self.content = BoxLayout(orientation='vertical')
        self.size_hint_y = None
        self.height = 180
        self.content.add_widget(Button(
            text=message,
            size_hint_y=None,
            height=40))
        self.content.add_widget(Button(
            text='Sí',
            on_press=callback_yes,
            size_hint_y=None,
            height=40))
        self.content.add_widget(Button(
            text='No',
            on_press=callback_no,
            size_hint_y=None,
            height=40))


if __name__ == '__main__':
    GenEspaldasApp().run()
