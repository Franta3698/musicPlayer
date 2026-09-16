import pygame
import threading
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QListWidget
from PyQt6.QtCore import QTimer
from PyQt6.uic import loadUi
import sys
import os
from mutagen import mp3
from mutagen.mp3 import MP3
pygame.init()
pygame.mixer.init()
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
ROUNDINGERROR = 1


SONG_END_EVENT = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(SONG_END_EVENT)

class MainUI(QMainWindow):
    def __init__(self):
            super(MainUI, self).__init__()
            loadUi("player.ui", self)


            self.folder = ""
            self.mp3_que = []
            self.paused = False
            self.playing = 0
            self.que_lenght = 0
            self.volume = 1
            self.timer = QTimer()
            self.audioLength = 1
            self.offset = 0
            self.position = 0
            self.timeElapsed = 0

            self.ChooseFolder_button.clicked.connect(self.select_folder)
            self.PauseUnpause_button.clicked.connect(self.pause_unpause)
            self.GoFront_button.clicked.connect(self.next)
            self.GoBack_button.clicked.connect(self.back)
            self.Songs_widget.itemClicked.connect(self.song_clicked)
            self.Volume_slider.valueChanged.connect(self.changed_volume)
            self.SongScrubber_slider.sliderReleased.connect(self.change_time)
            self.timer.timeout.connect(self.update_time)
            self.timer.start(1000)

    def reset(self):
        self.timeElapsed = 0
        self.offset = 0

    def timer_setup(self):
        self.CurrentMusic_label.setText(self.mp3_que[self.playing % self.que_lenght])
        self.audioLength = MP3(self.folder + "/" + self.mp3_que[self.playing % self.que_lenght]).info.length
        self.SongLength_label.setText(f"{int(self.audioLength // 60)}:{(int(self.audioLength % 60)):02d}")
        self.SongScrubber_slider.setMaximum(int(self.audioLength))
    def select_folder(self):
        self.playing = 0
        self.Songs_widget.clear()
        pygame.mixer.music.stop()
        self.folder = QFileDialog.getExistingDirectory(self, "Vyber složku")
        if not os.path.isdir(self.folder):
            return
        self.CurrentFolder_label.setText("Vybraná složka: " + ((self.folder.split("/"))[-1]))
        self.mp3_que = sorted([file for file in os.listdir(self.folder) if file.endswith(".mp3")],key=lambda file: file[:2])
        self.que_lenght = len(self.mp3_que)

        for song in self.mp3_que:
            self.Songs_widget.addItem(song)

        pygame.mixer.music.load(self.folder + "/" + self.mp3_que[self.playing])
        self.Songs_widget.setCurrentRow(self.playing % self.que_lenght)
        pygame.mixer.music.play()
        pygame.mixer.music.pause()
        self.timer_setup()
        self.reset()
        self.paused = True

    def pause_unpause(self):
        if self.paused:
            pygame.mixer.music.unpause()
            self.timer.start(1000)
            self.paused = False
        else:

            pygame.mixer.music.pause()
            self.timer.stop()
            self.paused = True

    def next(self):
        self.playing += 1
        pygame.mixer.music.load(self.folder + "/" + self.mp3_que[self.playing % self.que_lenght])
        self.Songs_widget.setCurrentRow(self.playing % self.que_lenght)
        pygame.mixer.music.play()
        self.timer_setup()
        self.reset()
        self.paused = False
    
    def back(self):
        self.playing -= 1
        pygame.mixer.music.load(self.folder + "/" + self.mp3_que[self.playing % self.que_lenght])
        self.Songs_widget.setCurrentRow(self.playing % self.que_lenght)
        pygame.mixer.music.play()
        self.timer_setup()
        self.reset()
        self.paused = False
    def song_clicked(self, item):
        self.playing = self.mp3_que.index(item.text())
        self.timer_setup()
        pygame.mixer.music.load(self.folder + "/" + item.text())
        pygame.mixer.music.play()
        self.reset()
        self.paused = False
        pass
    def changed_volume(self):
        self.volume = self.Volume_slider.value()
        pygame.mixer.music.set_volume((self.volume / 100) ** 2)

    def update_time(self):
        self.timeElapsed += 1
        self.position = (pygame.mixer.music.get_pos() / 1000) + self.offset
        minutes = int(self.position // 60)
        seconds = int(self.position % 60)
        self.CurrentSongTime_label.setText(f"{minutes}:{seconds:02d}")
        self.SongScrubber_slider.setValue(int(self.position))
        if (self.position) >= self.audioLength:
            self.next()


    def change_time(self):

        self.offset = self.SongScrubber_slider.value()

        if (self.offset < self.timeElapsed):
            pygame.mixer.music.play(start=self.offset)
            
        pygame.mixer.music.set_pos((self.offset))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()