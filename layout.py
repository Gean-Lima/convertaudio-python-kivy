from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from pydub import AudioSegment
from pygame import mixer
import os

mixer.init()


def popupAlert(text):
    popup = Popup(title='Alert',
                  content=Label(text=text),
                  size_hint=(None, None),
                  size=(400, 120))
    popup.open()


class AudioConvertLayout(BoxLayout):
    def __init__(self, **kwargs):
        self.filterFormatsAudio = [
            '*.mp3',
            '*.ogg',
            '*.wav',
            '*.webm',
            '*.raw'
        ]
        self.homePath = os.path.expanduser('~')
        self.audioProperties = None
        self.optionCovertFormatTo = 'mp3'
        self.clockTimeSong = None
        super(AudioConvertLayout, self).__init__(**kwargs)

        self.dropdownFormats = DropDown()
        for ext in self.filterFormatsAudio:
            itemButton = Button(text=ext.replace('*.', ''), size_hint_y=None, height=44)
            itemButton.bind(on_release=lambda btn: self.setOptionConvertFormat(btn.text))
            self.dropdownFormats.add_widget(itemButton)
        self.ids.button_dropdown.bind(on_release=self.dropdownFormats.open)
        self.dropdownFormats.bind(on_select=lambda instance, x: setattr(self.ids.button_dropdown, 'text', x))

    def selectFile(self, args):
        if len(args[0].selection) > 0:
            self.setAudioProperties(args[0].selection[0])
            self.fillLabelWithSelectedAudio()
        else:
            self.audioProperties = None

    def setAudioProperties(self, path_audio):
        if not self.audioProperties is None:
            self.stopAudio()

        extension = os.path.splitext(path_audio)[1].replace('.', '')
        self.audioProperties = {
            'filename': path_audio,
            'audiosegment': AudioSegment.from_file(path_audio, format=extension),
            'format': extension,
            'playing': False
        }

    def fillLabelWithSelectedAudio(self):
        if not self.audioProperties:
            self.ids.label_selected.text = 'Nothing selected'
        else:
            self.ids.label_selected.text = f"File: {os.path.basename(self.audioProperties['filename'])}"
            self.setTimeSong()

    def setTimeSong(self):
        minutes = int(self.audioProperties['audiosegment'].duration_seconds // 60)
        seconds = int(self.audioProperties['audiosegment'].duration_seconds % 60)
        self.ids.time_song.text = '{:0>2}:{:0>2}'.format(minutes, seconds)

    def setOptionConvertFormat(self, format):
        self.optionCovertFormatTo = format
        self.dropdownFormats.select(format)

    def convert(self):
        if self.audioProperties is None:
            popupAlert('Select a file or folder')
        elif self.optionCovertFormatTo == '':
            popupAlert('Select conversion format to')
        elif self.audioProperties['format'] == self.optionCovertFormatTo:
            popupAlert('Conversion options cannot be the same')
        else:
            if self.audioProperties['playing'] and mixer.music.get_busy():
                self.ctrlAudio()
            newFileName = self.audioProperties['filename'].replace(self.audioProperties['format'],
                                                                   self.optionCovertFormatTo)
            self.audioProperties['audiosegment'].export(newFileName, format=self.optionCovertFormatTo)
            self.ids.file_chooser._update_files()
            popupAlert('Audio converted')

    def setTimeWhileMusicIsPlaying(self, dt):
        if not mixer.music.get_busy():
            self.clockTimeSong.cancel()
            self.ids.progressbar_song.value = 100
            self.ids.button_ctrl_audio.text = 'Play'
            self.audioProperties['playing'] = False
            return False
        minutes = int(mixer.music.get_pos() // 60000)
        seconds = int((mixer.music.get_pos() % 60000) // 1000)
        self.ids.time_song_while_is_playing.text = '{:0>2}:{:0>2}'.format(minutes, seconds)

        timeSongInMilliseconds = self.audioProperties['audiosegment'].duration_seconds * 1000
        percentage = int(100 * mixer.music.get_pos() / timeSongInMilliseconds)
        self.ids.progressbar_song.value = percentage

    def ctrlAudio(self):
        if not self.audioProperties is None:
            if self.audioProperties['playing']:
                if mixer.music.get_busy():
                    mixer.music.pause()
                    self.ids.button_ctrl_audio.text = 'Play'
                    self.clockTimeSong.cancel()
                else:
                    mixer.music.unpause()
                    self.ids.button_ctrl_audio.text = 'Pause'
                    self.clockTimeSong()
            else:
                mixer.music.load(self.audioProperties['filename'])
                mixer.music.play()
                self.clockTimeSong = Clock.schedule_interval(self.setTimeWhileMusicIsPlaying, 0)
                self.audioProperties['playing'] = True
                self.ids.button_ctrl_audio.text = 'Pause'

    def stopAudio(self):
        if not self.clockTimeSong is None:
            self.clockTimeSong.cancel()
        mixer.music.stop()
        self.ids.button_ctrl_audio.text = 'Play'
        self.ids.progressbar_song.value = 0
        self.ids.time_song_while_is_playing.text = '00:00'
