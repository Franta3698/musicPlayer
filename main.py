import pygame
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QListWidget
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.uic import loadUi
import sys
import os
import random
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
pygame.init()
pygame.mixer.init()
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

class MainUI(QMainWindow):
    def __init__(self):
            super(MainUI, self).__init__()
            loadUi("player.ui", self)


            self.folder = ""
            self.mp3_que = []
            self.paused = True
            self.playing = 0
            self.que_lenght = 0
            self.volume = 1
            self.timer = QTimer()
            self.audioLength = 1
            self.offset = 0
            self.timeElapsed = 0
            self.minutes = 0
            self.seconds = 0
            self.slider_is_pressed = False
            self.looping = False
            self.random = False
            self.randomQue = {}
            self.seed = 0

            self.Volume_slider.setValue(100)

            self.PauseUnpause_button.setFixedSize(48, 48)
            self.PauseUnpause_button.setIcon(QIcon("icons/PlayIcon.svg"))
            self.PauseUnpause_button.setIconSize( self.PauseUnpause_button.size())

            self.PauseUnpause_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 0px;
                    background: transparent;
                }
            """)

            self.ChooseFolder_button.clicked.connect(self.select_folder)
            self.PauseUnpause_button.clicked.connect(self.pause_unpause)
            self.GoFront_button.clicked.connect(self.next)
            self.GoBack_button.clicked.connect(self.back)
            self.Songs_widget.itemClicked.connect(self.song_clicked)
            self.Volume_slider.valueChanged.connect(self.changed_volume)
            self.SongScrubber_slider.sliderReleased.connect(self.change_time)
            self.timer.timeout.connect(self.update_time)
            self.SongScrubber_slider.sliderPressed.connect(self.slider_pressed)
            self.SongScrubber_slider.sliderReleased.connect(self.slider_released)
            self.SongScrubber_slider.sliderMoved.connect(self.slider_moved)
            self.Loop_button.clicked.connect(self.loop)
            self.Random_button.clicked.connect(self.set_random_que)

    def set_random_que(self):
        if self.random:
            self.random = False
            self.randomQue.clear()
        else:
            self.random = True
            for i, song in enumerate(self.mp3_que):
                cislo = random.randint(0, (len(self.mp3_que)-1))
                while cislo in self.randomQue.keys():
                    cislo = (cislo + 1) % len(self.mp3_que)
                self.randomQue[cislo] = song



    def loop(self):
        if self.looping:
            self.looping = False
        else:
            self.looping = True


    def change_pause_button(self):
        if self.paused:
            self.PauseUnpause_button.setIcon(QIcon("icons/PlayIcon.svg"))
        else:
            self.PauseUnpause_button.setIcon(QIcon("icons/PauseIcon.svg"))
        self.PauseUnpause_button.setIconSize(self.PauseUnpause_button.size())
    def slider_moved(self, value):
        self.CurrentSongTime_label.setText(f"{value //60 }:{(value % 60):02d}")
    def slider_pressed(self):
        self.slider_is_pressed = True
    def slider_released(self):
        self.slider_is_pressed = False

    def set_time_info(self):

        self.minutes = int(self.timeElapsed // 60)
        self.seconds = int(self.timeElapsed % 60)
        if self.slider_is_pressed:
            return
        self.CurrentSongTime_label.setText(f"{self.minutes}:{self.seconds:02d}")
        self.SongScrubber_slider.setValue(self.timeElapsed)

    def reset(self):
        self.timeElapsed = 0
        self.offset = 0
        self.timer.start(1000)

    def timer_setup(self):
        if self.looping is False:

            if self.random:
                self.CurrentMusic_label.setText(self.randomQue[self.playing % self.que_lenght])
                if (self.randomQue[self.playing % self.que_lenght]).endswith(".wav"):
                    self.audioLength = WAVE(self.folder + "/" + self.randomQue[self.playing % self.que_lenght]).info.length
                self.audioLength = MP3(self.folder + "/" + self.randomQue[self.playing % self.que_lenght]).info.length
            else:
                self.CurrentMusic_label.setText(self.mp3_que[self.playing % self.que_lenght])
                if (self.mp3_que[self.playing % self.que_lenght]).endswith(".wav"):
                    self.audioLength = WAVE(self.folder + "/" + self.mp3_que[self.playing % self.que_lenght]).info.length
                self.audioLength = MP3(self.folder + "/" + self.mp3_que[self.playing % self.que_lenght]).info.length
        
        
        self.SongLength_label.setText(f"{int(self.audioLength // 60)}:{(int(self.audioLength % 60)):02d}")
        self.SongScrubber_slider.setMaximum(int(self.audioLength))


    def changeSong(self):
        if self.random:
             if self.looping:
                pygame.mixer.music.load(self.folder + "/" + self.mp3_que[self.Songs_widget.currentRow()])
             else:
                pygame.mixer.music.load(self.folder + "/" + self.randomQue[self.playing % self.que_lenght])     
                for i, song in enumerate(self.mp3_que):
                    if song == self.randomQue[self.playing % self.que_lenght]:
                        index = i
                self.Songs_widget.setCurrentRow(index)

                        
        else:
            if self.looping:
                pygame.mixer.music.load(self.folder + "/" + self.mp3_que[self.Songs_widget.currentRow()]) 
            else:
                pygame.mixer.music.load(self.folder + "/" + self.mp3_que[self.playing % self.que_lenght])     
                self.Songs_widget.setCurrentRow(self.playing % self.que_lenght)

        pygame.mixer.music.play()
        self.timer_setup()
        self.reset()
        self.set_time_info()
        self.paused = False
        self.change_pause_button()

    def select_folder(self):
        self.playing = 0
        self.Songs_widget.clear()
        pygame.mixer.music.stop()
        self.folder = QFileDialog.getExistingDirectory(self, "Vyber složku")
        if not os.path.isdir(self.folder):
            return
        self.CurrentFolder_label.setText("Vybraná složka: " + ((self.folder.split("/"))[-1]))
        self.mp3_que = sorted(
            [file for file in os.listdir(self.folder)
            if file.lower().endswith((".mp3", ".wav"))],
            key=lambda file: file[:2]
        )
        self.que_lenght = len(self.mp3_que)

        if self.que_lenght < 1:
            return

        for song in self.mp3_que:
            self.Songs_widget.addItem(song)

        pygame.mixer.music.load(self.folder + "/" + self.mp3_que[self.playing])
        self.Songs_widget.setCurrentRow(self.playing % self.que_lenght)
        pygame.mixer.music.play()
        pygame.mixer.music.pause()
        self.paused = True
        self.timer.stop()
        self.timer_setup()
        self.SongScrubber_slider.setValue(0)
        self.CurrentSongTime_label.setText(f"00:00")
        self.timeElapsed = 0
        self.offset = 0


    def pause_unpause(self):
        if not os.path.isdir(self.folder):
            return
        if self.paused:
            pygame.mixer.music.unpause()
            self.timer.start(1000)
            self.paused = False
        else:
            pygame.mixer.music.pause()
            self.timer.stop()
            self.paused = True
        self.change_pause_button()

    def next(self):
        if self.looping is False:
            self.playing += 1
        self.changeSong()


    
    def back(self):
        
        self.playing -= 1
        self.changeSong()
       

    def song_clicked(self, item):
        self.playing = self.mp3_que.index(item.text())
        self.CurrentMusic_label.setText(self.mp3_que[self.playing % self.que_lenght])
        if (self.mp3_que[self.playing % self.que_lenght]).endswith(".wav"):
            self.audioLength = WAVE(self.folder + "/" + self.mp3_que[self.playing % self.que_lenght]).info.length
        self.audioLength = MP3(self.folder + "/" + self.mp3_que[self.playing % self.que_lenght]).info.length
        self.SongLength_label.setText(f"{int(self.audioLength // 60)}:{(int(self.audioLength % 60)):02d}")
        self.SongScrubber_slider.setMaximum(int(self.audioLength))        
        pygame.mixer.music.load(self.folder + "/" + item.text())
        pygame.mixer.music.play()
        self.reset()
        self.set_time_info()
        self.paused = False
        self.change_pause_button()
        
    def changed_volume(self):
        self.volume = self.Volume_slider.value()
        pygame.mixer.music.set_volume((self.volume / 100) ** 2)

    def update_time(self):
        self.timeElapsed += 1
        self.set_time_info()
        if self.audioLength - self.timeElapsed < 1:
            self.next()

    def change_time(self):
        self.timeElapsed = self.SongScrubber_slider.value()
        self.set_time_info()
        if self.paused:
            pygame.mixer.music.play(start=self.SongScrubber_slider.value())
            pygame.mixer.music.pause()
            return
        pygame.mixer.music.play(start=self.SongScrubber_slider.value())
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()