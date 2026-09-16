class Playlist:
    def __init__(self):
        self.songs = []

    def add_song(self, name, duration):
        if not isinstance(name, str):
            raise TypeError("Название песни должно быть строкой")
        if not name.strip():
            raise ValueError("Название песни не может быть пустым")
        if not isinstance(duration, (int, float)):
            raise TypeError("Продолжительность должна быть числом")
        if duration < 0:
            raise ValueError("Продолжительность не может быть отрицательной")

        self.songs.append({
            "name": name,
            "duration": duration
        })

    def remove_song(self, name):
        for i in range(len(self.songs)):
            if self.songs[i]["name"] == name:
                del self.songs[i]
                break

    def total_duration(self):
        return sum(song["duration"] for song in self.songs)

    def __len__(self):
        return len(self.songs)

    def __str__(self):
        if not self.songs:
            return "Плейлист пуст"

        result = "Список песен:\n"

        for i in range(len(self.songs)):
            result += f"{i}. {self.songs[i]["name"]} - {self.songs[i]["duration"]} c.\n"
        return result.strip()


playlist = Playlist()

print(playlist)
print("Количество песен:", len(playlist))
print("Общая продолжительность:", playlist.total_duration(), "сек.")
print()

playlist.add_song("Song 0", 354)
playlist.add_song("Song 1", 200)
playlist.add_song("Song 2", 300)

print(playlist)
print("Количество песен:", len(playlist))
print("Общая продолжительность:", playlist.total_duration(), "сек.")
print()

playlist.remove_song("Song 1")
print(playlist)
print("Количество песен:", len(playlist))
print("Общая продолжительность:", playlist.total_duration(), "сек.")
print()

playlist.remove_song("Song 3")
print(playlist)