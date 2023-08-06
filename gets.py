import ast
def get_last_song():
    with open("plays.txt", "r", encoding="utf-8") as f:
        lines = f.read()
        song_ids = lines.split("\n")
        appender = song_ids[-2]
        f.close()

    new_appender = ast.literal_eval(appender)
    return new_appender

def get_now_playing():
    with open("now.txt", "r", encoding="utf-8") as f:
        lines = f.read()
        song_ids = lines.split("\n")
        sng = song_ids[-1]
        f.close()
    return sng