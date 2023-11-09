from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.togglebutton import ToggleButtonBehavior
from kivy.uix.button import Button
import csv
import os
import re


class MyLayout(GridLayout):

    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)
        # Layout conf
        self.cols = 1
        self.inputs_layout = BoxLayout(orientation='horizontal')
        self.data_layout = BoxLayout(
            orientation='horizontal')
        self.action_buttons_layout = BoxLayout(orientation='horizontal')

        # global variables
        # espalda {name, number, size}
        self.espaldas = []

        # Data
        self.entrada = TextInput(
            multiline=False, hint_text="Ingrese el nombre y el número")
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
        self.agregar = Button(text="Agregar Espalda")
        self.exportar = Button(text="Exportar")
        self.agregar.bind(on_press=self.agregar_datos)
        self.exportar.bind(on_press=self.exportar_csv)
        self.action_buttons_layout.add_widget(self.agregar)
        self.action_buttons_layout.add_widget(self.exportar)
        self.add_widget(self.action_buttons_layout)

        # Showcase
        self.labels_container = BoxLayout(
            orientation='vertical', size_hint=(1, 0.5))
        self.add_widget(self.labels_container)

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
            Label(text=f"{espalda['name']} {espalda['number']} {espalda['size']}"))

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


class GenEspaldasApp(App):
    def build(self):
        return MyLayout()


if __name__ == '__main__':
    GenEspaldasApp().run()
