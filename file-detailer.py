import os
from ffmpeg import FFmpeg
from ffprobe import FFProbe

EPISODES_DIR = "."
SUBTITLES_DIR = "."
EPISODE_EXT = "mkv"
SUBTITLE_EXT = "srt"

current_folder = os.path.dirname(os.path.abspath(__file__))

def get_japanese_audio_track_index(file):
    """Get the index of the Japanese audio track in the file."""
    metadata = FFProbe(file)
    audio_streams = metadata.streams.filter(stream_type='audio')
    for stream in audio_streams:
        if 'language' in stream.tags and stream.tags['language'] == 'jpn':
            return stream.index
    return None


def get_current_default_audio_indexes(file):
    pass


def get_all_audio_indexes(file):
    pass


def get_all_subtitle_indexes(file):
    pass


def main():
    if not os.path.isdir(EPISODES_DIR):
        print(f"Directory not found: {EPISODES_DIR}")
        exit(1)

    if not os.path.isdir(os.path.join(EPISODES_DIR, 'processed')):
        os.mkdir(os.path.join(EPISODES_DIR, 'processed'))

    for episode in os.listdir(EPISODES_DIR):
        if episode.endswith('.' + EPISODE_EXT):
            base_name = os.path.splitext(episode)[0]
            episode_path = os.path.join(EPISODES_DIR, episode)

            if not os.path.isfile(episode_path):
                print(f"File not found: {episode_path}")
                continue

            subtitle_path = os.path.join(SUBTITLES_DIR, base_name + '.' + SUBTITLE_EXT)
            output_file = os.path.join(EPISODES_DIR, 'processed', base_name + '_new.' + EPISODE_EXT)

            audio_tracks = get_all_audio_indexes(episode_path)
            japanese_audio_track_index = get_japanese_audio_track_index(episode_path)
            default_audio_indexes = get_current_default_audio_indexes(episode_path)

            # Set the default disposition for the Japanese audio track
            disp_command = []
            for index in audio_tracks:
                if index == japanese_audio_track_index:
                    disp_command.append((index, 'default'))
                elif index in default_audio_indexes:
                    disp_command.append((index, 'none'))

            subtitle_command = []


metadata=FFProbe('test.mkv')
for stream in metadata.streams:
    if stream.is_video():
        print('Stream contains {} frames.'.format(stream.frames()))
