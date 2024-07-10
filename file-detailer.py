import os
import ffmpeg

EPISODES_DIR = "."
SUBTITLES_DIR = "."
EPISODE_EXT = "mkv"
SUBTITLE_EXT = "srt"


def get_japanese_audio_track_index(file):
    probe = ffmpeg.probe(file)
    for stream in probe['streams']:
        if stream['codec_type'] == 'audio' and 'tags' in stream and stream['tags'].get('language', '') in ['jpn', 'ja']:
            return stream['index']
    return None


def get_current_default_audio_indexes(file):
    probe = ffmpeg.probe(file)
    indexes = []
    for stream in probe['streams']:
        if stream['codec_type'] == 'audio' and 'disposition' in stream and stream['disposition'].get('default', 0) == 1:
            indexes.append(stream['index'])
    return indexes


def get_all_audio_indexes(file):
    probe = ffmpeg.probe(file)
    indexes = []
    for stream in probe['streams']:
        if stream['codec_type'] == 'audio':
            indexes.append(stream['index'])
    return indexes


def get_all_subtitle_indexes(file):
    probe = ffmpeg.probe(file)
    indexes = []
    for stream in probe['streams']:
        if stream['codec_type'] == 'subtitle':
            indexes.append(stream['index'])
    return indexes


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
        if os.path.isfile(subtitle_path):
            subtitle_command = [
                ffmpeg.input(subtitle_path),
                ffmpeg.output(subtitle_path, **{
                    'c:s': 'mov_text',
                    'metadata:s:s': 'language=jpn',
                    'metadata:s:s': 'title=Japanese'
                })
            ]

        # Count the number of existing subtitle streams
        subtitle_count = len(get_all_subtitle_indexes(episode_path))

        # Process the episode
        stream = ffmpeg.input(episode_path)
        stream = ffmpeg.output(stream, *subtitle_command, **{
            'map': '0',
            'map': '1',
            'c': 'copy',
            'disposition:s:{}'.format(subtitle_count): 'default'
        })
        for index, disposition in disp_command:
            stream = stream.output(stream, **{'disposition:a:{}'.format(index): disposition})
        ffmpeg.run(stream, overwrite_output=True)
        print(f"Processed: {episode}")

print("All episodes processed.")
