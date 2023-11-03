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


class MyLayout(GridLayout):

    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)
        # Layout conf
        self.cols = 1
        self.data_layout = BoxLayout(
            orientation='horizontal')

        # global variables
        # espalda {name, number, size}
        self.espaldas = []

        # Data
        self.nombre = TextInput(multiline=False, hint_text="Nombre")
        self.numero = TextInput(multiline=False, hint_text="Numero")
        self.nombre.bind(on_text_validate=self.cambiar_enfoque)
        self.numero.bind(on_text_validate=self.cambiar_enfoque)
        self.small = ToggleButton(text="small", group="tallas")
        self.medium = ToggleButton(text="medium", group="tallas", state='down')
        self.large = ToggleButton(text="large", group="tallas")
        self.add_widget(self.nombre)
        self.add_widget(self.numero)
        self.data_layout.add_widget(self.small)
        self.data_layout.add_widget(self.medium)
        self.data_layout.add_widget(self.large)
        self.add_widget(self.data_layout)

        # Botones accion
        self.agregar = Button(text="Agregar Espalda")
        self.exportar = Button(text="Exportar")
        self.agregar.bind(on_press=self.agregar_datos)
        self.exportar.bind(on_press=self.exportar_csv)
        self.add_widget(self.agregar)
        self.add_widget(self.exportar)

        # Showcase
        self.labels_container = BoxLayout(
            orientation='vertical', size_hint=(1, 0.5))
        self.add_widget(self.labels_container)

    def agregar_datos(self, obj):
        espaldas = self.espaldas
        name = self.nombre.text.upper()
        number = self.numero.text
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

        fieldnames = ['name', 'number']
        for talla in ToggleButtonBehavior.get_widgets('tallas'):
            talla_str = talla.text.lower()
            csv_file = os.path.join(folder_path, f'espaldas_{talla_str}.csv')

            current_espaldas = [
                {'name': espalda['name'], 'number': espalda['number']} for espalda in self.espaldas if espalda['size'] == talla_str]
            if len(current_espaldas) == 0:
                continue

            # Escribir los datos en el archivo CSV
            with open(csv_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()  # Escribir las cabeceras
                for espalda in current_espaldas:
                    writer.writerow(espalda)

    def reset_inputs(self):
        self.nombre.text = ""
        self.numero.text = ""

    def cambiar_enfoque(self, instance):
        if instance == self.nombre:
            self.numero.focus = True
        elif instance == self.numero:
            self.nombre.focus = True


class GenEspaldasApp(App):
    def build(self):
        return MyLayout()


if __name__ == '__main__':
    GenEspaldasApp().run()
