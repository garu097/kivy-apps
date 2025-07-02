# 📝 Platform-specific Notes

## ✅ Android
- `Buildozer` reads from `buildozer.spec`, not `requirements.txt`, but you copy these names into:

```ini
requirements = python3,kivy,kivymd,pillow,pygments,docutils
```

## ✅ iOS
- Use [kivy-ios](https://github.com/kivy/kivy-ios) to build the app:

```bash
python3 -m pip install kivy-ios
toolchain create <your-app-name> <path-to-your-app>
toolchain build kivy kivymd pillow
toolchain install <your-app-name>
```

> Note: iOS supports fewer libraries than Android. Avoid using libraries such as `opencv`, `scipy`, `pyaudio` unless you are sure they have been built for `kivy-ios`.