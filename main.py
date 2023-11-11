from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.togglebutton import ToggleButtonBehavior
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
import csv
import os
import re
import pandas as pd

from kivy.uix.popup import Popup


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


class MyLayout(GridLayout):

    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)
        # drag and drop
        Window.bind(on_drop_file=self._on_file_drop)

        # Layout conf
        self.cols = 1
        self.size_hint_y = 1
        self.inputs_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.5/3)
        self.data_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.5/3,
            height=80)
        self.action_buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.5/3,
            height=100)
        self.scroll_view = ScrollView(size_hint=(1, 0.5), size=(400, 400))

        # global variables
        # espalda {name, number, size}
        self.espaldas = []
        self.excel_path = ''

        # Data
        self.entrada = TextInput(
            multiline=False,
            hint_text="Ingrese el nombre y el número",
            halign="center",
            padding_y=20,
            font_size=38,
            size_hint_y=None,
            height=100)
        self.entrada.bind(on_text_validate=self.agregar_datos)
        self.inputs_layout.add_widget(self.entrada)
        self.add_widget(self.inputs_layout)
        self.small = ToggleButton(text="small", group="tallas")
        self.medium = ToggleButton(text="medium", group="tallas", state='down')
        self.large = ToggleButton(text="large", group="tallas")
        self.data_layout.add_widget(self.small)
        self.data_layout.add_widget(self.medium)
        self.data_layout.add_widget(self.large)
        self.add_widget(self.data_layout)

        # Botones acción
        self.agregar = Button(
            text="Agregar Espalda",
            # rgb(66, 245, 117)
            background_color=(66/255, 245/255, 117/255, 1),
            font_size=18,
            bold=True,)
        self.exportar = Button(
            text="Exportar",
            # rgb(66, 179, 245)
            background_color=(66/255, 179/255, 245/255, 1),
            font_size=18,
            bold=True)
        self.agregar.bind(on_press=self.agregar_datos)
        self.exportar.bind(on_press=self.exportar_csv)
        self.action_buttons_layout.add_widget(self.agregar)
        self.action_buttons_layout.add_widget(self.exportar)
        self.add_widget(self.action_buttons_layout)

        # Showcase
        self.labels_container = GridLayout(
            cols=1,
            size_hint=(1, None),
            height=500,
            spacing=10,)
        self.scroll_view.add_widget(self.labels_container)
        self.add_widget(self.scroll_view)

    def agregar_datos(self, obj):
        espaldas = self.espaldas
        name, number = self.parse_text(self.entrada.text)
        size = ''

        for talla_btn in ToggleButtonBehavior.get_widgets('tallas'):
            if talla_btn.state == 'down':
                size = talla_btn.text.lower()
                break

        espalda = {'name': name, 'number': number, 'size': size}
        espaldas.append(espalda)

        # Showcase
        self.labels_container.add_widget(
            Label(
                text=f"{espalda['name']} {espalda['number']} {espalda['size']}",
                font_size=18,
                size_hint=(1, None),
                height=40,
                outline_color=(1, 1, 1, 1))
        )

        self.reset_inputs()

    def exportar_csv(self, obj):
        # Obtén la ruta al carpeta
        desktop_path = os.path.expanduser("~/Desktop")
        folder_name = "espaldas"
        folder_path = os.path.join(desktop_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        fieldnames = ['Variable1', 'Variable2']
        for talla in ToggleButtonBehavior.get_widgets('tallas'):
            talla_str = talla.text.lower()
            csv_file = os.path.join(folder_path, f'espaldas_{talla_str}.csv')

            current_espaldas = [
                {'Variable1': espalda['name'], 'Variable2': espalda['number']} for espalda in self.espaldas if espalda['size'] == talla_str]
            if len(current_espaldas) == 0:
                continue

            # Escribir los datos en el archivo CSV
            with open(csv_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()  # Escribir las cabeceras
                for espalda in current_espaldas:
                    writer.writerow(espalda)

    def exportar_csv_from_list(self, my_list):
        # Obtén la ruta al escritorio
        desktop_path = os.path.expanduser("~/Desktop")
        folder_name = "espaldas"
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

    def reset_inputs(self):
        self.entrada.text = ""
        self.entrada.focus = True

    def parse_text(self, text):
        """parse_text(str) -> (str, str|int)
        Regresa el nombre y el número en el texto dado.

        Ejemplo:
        >>> parse_text("Paca 12")
        ("Paca", 12)"""
        pattern = re.compile(r'(\b\w+\b)?(?:.*?(\d+))?')
        result_match = pattern.search(text)
        result_group = self.ordenar_tupla(result_match.groups())

        if result_match:
            word = result_group[0].upper(
            ) if result_group[0] != '' else "BORRAR"
            number = result_group[1] if result_group[1] != '' else "BORRAR"

            return word.upper(), number
        else:
            return "borrar", "borrar"

    def ordenar_tupla(self, tupla):
        result = ['', '']
        copia_ = list(tupla)

        # quita nones
        for i in range(len(copia_)):
            if copia_[i] == None:
                copia_[i] = ''

        # convertir si hay numero a numero, y lo guarda en el
        # el indice 1:
        for index in copia_:
            try:
                result[1] = int(index)
                index_num = copia_.index(index)
                palabra = copia_[0] if index_num else copia_[1]
                result[0] = '' if palabra == None else palabra

                return result
            except (ValueError, TypeError):
                continue

        # si llega aqui no hay numeros y los nones son str vacios
        for i in range(len(copia_)):
            if not (copia_[i] == ''):
                result[0] = copia_[i]

        return result

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

    def process_excel(self, path):
        archivo_excel = path
        try:
            datos_excel = pd.read_excel(archivo_excel, sheet_name=0)

            lista_objetos = []
            for index, row in datos_excel.iterrows():
                objeto = {
                    'name': row['name'].upper(),
                    'number': row['number'],
                    'size': row['size']
                }
                lista_objetos.append(objeto)

            return lista_objetos
            print(lista_objetos)

        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")


class GenEspaldasApp(App):
    def build(self):
        return MyLayout()


if __name__ == '__main__':
    GenEspaldasApp().run()
