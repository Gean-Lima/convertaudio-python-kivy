from kivy.app import App
from layout import AudioConvertLayout


class AudioConvertApp(App):
    def build(self):
        return AudioConvertLayout()


if __name__ == '__main__':
    AudioConvertApp().run()
