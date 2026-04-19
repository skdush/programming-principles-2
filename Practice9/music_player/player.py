import pygame
import os


class MusicPlayer:
    def __init__(self, music_folder):
        pygame.mixer.init()
        self.music_folder = music_folder
        self.playlist = []
        self.track_names = []
        self.current_index = 0
        self.is_playing = False
        self.is_stopped = True

        self._load_playlist()

    def _load_playlist(self):
        if not os.path.exists(self.music_folder):
            return
        for filename in sorted(os.listdir(self.music_folder)):
            if filename.lower().endswith((".mp3", ".wav", ".ogg")):
                self.playlist.append(os.path.join(self.music_folder, filename))
                self.track_names.append(filename)

    def play(self):
        if not self.playlist:
            return
        pygame.mixer.music.load(self.playlist[self.current_index])
        pygame.mixer.music.play()
        self.is_playing = True
        self.is_stopped = False

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_stopped = True

    def next_track(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        if self.is_playing:
            self.play()

    def prev_track(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        if self.is_playing:
            self.play()

    def get_current_track_name(self):
        if not self.track_names:
            return "No tracks found"
        return self.track_names[self.current_index]

    def get_track_count(self):
        return len(self.playlist)

    def get_position(self):
        if self.is_playing:
            return pygame.mixer.music.get_pos() / 1000
        return 0.0

    def update(self):
        if self.is_playing and not pygame.mixer.music.get_busy():
            self.next_track()
