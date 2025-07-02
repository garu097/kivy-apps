from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from components.button.button import CButton
from config.theme import Theme


class MainApp(MDApp):
	def build(self):
		self.my_theme = Theme.instance()
		self.theme_cls = self.my_theme.theme_cls

		screen = MDScreen()
		button = CButton(text="Click Me")
		screen.add_widget(button)
		return screen


if __name__ == "__main__":
	theme = Theme()
	MainApp().run()
