import pygame as pg

music = {
    'Dungeon' : 'audio/music/Dungeon.mp3',
    'Shop' : 'audio/music/Shop.mp3',
    'Lobby' : 'audio/music/Lobby.mp3',
    'Intro' : 'audio/music/Intro.mp3',
}

sounds = {
    'jump' : 'audio/sounds/cartoon-jump-6462.mp3',
    'explosion' : 'audio/sounds/explosion1.mp3',
    'shoot' : 'audio/sounds/shoot.mp3',
    'clack' : 'audio/sounds/clack.mp3',
    'clonk' : 'audio/sounds/clonk.mp3',
}

class SoundHandler:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 2, 512)
        pg.mixer.init()
        pg.mixer.set_num_channels(64)
        pg.mixer.music.set_volume(.2)
        MUSIC_END = pg.USEREVENT+1
        pg.mixer.music.set_endevent(MUSIC_END)
        
        self.sounds = {sound : pg.mixer.Sound(sounds[sound]) for sound in sounds}
        self.playlists = {}

        self.make_playlist('dungeon', ('Dungeon',))
        self.make_playlist('hub', ('Intro', 'Lobby'))

        self.current_track = None
        self.current_playlist = None
        self.playlist_index = 0

    def make_playlist(self, name, songs):
        self.playlists[name] = [music[song] for song in songs]

    def play_playlist(self, playlist):
        self.playlist_index = 0
        if self.current_track or self.current_playlist: 
            pg.mixer.music.fadeout(1000)
            self.playlist_index = -1
        self.current_playlist = playlist
        pg.mixer.music.load(self.playlists[playlist][self.playlist_index])
        pg.mixer.music.play(fade_ms=1000)

    def update_playlist(self):
        if not self.current_playlist: return
        self.playlist_index += 1
        if self.playlist_index >= len(self.playlists[self.current_playlist]): self.playlist_index = 0
        pg.mixer.music.load(self.playlists[self.current_playlist][self.playlist_index])
        pg.mixer.music.play(fade_ms=1000)

    def play_track(self, song):
        if self.current_track or self.current_playlist: pg.mixer.music.fadeout(1000)
        self.current_playlist = None
        pg.mixer.music.load(music[song])
        pg.mixer.music.play(-1, fade_ms=1000)
        self.current_track = song

    def play_sound(self, sound):
        snd = self.sounds[sound]
        snd.set_volume(0.2)
        snd.play()

    def fast_forward(self):
        pg.mixer.music.pause()
        pg.mixer.music.set_pos(125)
        pg.mixer.music.unpause()