from kivymd.theming import ThemeManager

from constant.theme_constant import ThemeLightMode
from utils.singleton import Singleton


class Theme(Singleton):
	def __init__(self):
		self.theme_cls = ThemeManager()
		self.set_theme(ThemeLightMode.LIGHT)

	def _configure_theme(self):
		self.set_theme(ThemeLightMode.LIGHT)
		self.theme_cls.primary_hue = "500"
		self.theme_cls.accent_hue = "500"

		self.theme_cls.theme_style_switch_animation = True
		self.theme_cls.theme_style_switch_animation_duration = 0.8

	def set_theme(self, mode: ThemeLightMode):
		self.theme_cls.theme_style = mode.value
		self.theme_cls.primary_palette = (
			"Red" if mode == ThemeLightMode.LIGHT else "Orange"
		)
		self.theme_cls.accent_palette = (
			"Amber" if mode == ThemeLightMode.LIGHT else "LightBlue"
		)
