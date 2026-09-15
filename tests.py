import os
import pygame


pygame.init()
pygame.mixer.init()


folder = input("Vyberte si složku: ")

mp3_que = [file for file in sorted(os.listdir((folder))) if file.endswith(".mp3")]

