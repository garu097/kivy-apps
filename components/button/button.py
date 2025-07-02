from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton


class CButton(MDFlatButton):
	def __init__(self, **kwargs):
		Builder.load_file("components/button/button.kv")
		super().__init__()
		self.text = kwargs.get("text", "Click me!")
		self.font_size = "16sp"

	def on_press(self):
		print(f"{self.text} button pressed")

	def on_release(self):
		print(f"{self.text} button released")
