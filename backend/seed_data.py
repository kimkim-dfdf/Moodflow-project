def seed_database(db):
    from models import Emotion, MusicRecommendation
    
    if Emotion.query.first() is not None:
        return
    
    emotions = [
        {
            'name': 'Happy',
            'emoji': '😊',
            'color': '#FFD93D',
            'energy_level': 9,
            'focus_level': 7
        },
        {
            'name': 'Sad',
            'emoji': '😢',
            'color': '#6B7FD7',
            'energy_level': 3,
            'focus_level': 4
        },
        {
            'name': 'Tired',
            'emoji': '😴',
            'color': '#8B4513',
            'energy_level': 2,
            'focus_level': 3
        },
        {
            'name': 'Angry',
            'emoji': '😠',
            'color': '#FF6B6B',
            'energy_level': 8,
            'focus_level': 4
        },
        {
            'name': 'Stressed',
            'emoji': '😰',
            'color': '#FF9F43',
            'energy_level': 6,
            'focus_level': 5
        },
        {
            'name': 'Neutral',
            'emoji': '😐',
            'color': '#95A5A6',
            'energy_level': 5,
            'focus_level': 6
        }
    ]
    
    emotion_objects = {}
    for emotion_data in emotions:
        emotion = Emotion(**emotion_data)
        db.session.add(emotion)
        db.session.flush()
        emotion_objects[emotion_data['name']] = emotion
    
    music_data = [
        {
            'emotion': 'Happy',
            'songs': [
                {'title': 'Happy', 'artist': 'Pharrell Williams', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=ZbZSe6N_BXs', 'spotify_url': 'https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH'},
                {'title': 'Good as Hell', 'artist': 'Lizzo', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=SmbmeOgWsqE', 'spotify_url': 'https://open.spotify.com/track/3Yh9lLpL2gM3N4cUx3n9vN'},
                {'title': 'Walking on Sunshine', 'artist': 'Katrina and the Waves', 'genre': 'Pop Rock', 'youtube_url': 'https://www.youtube.com/watch?v=iPUmE-tne5U', 'spotify_url': 'https://open.spotify.com/track/05wIrZSwuaVWhcv5FfqeH0'},
                {'title': 'Uptown Funk', 'artist': 'Bruno Mars', 'genre': 'Funk Pop', 'youtube_url': 'https://www.youtube.com/watch?v=OPf0YbXqDm0', 'spotify_url': 'https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS'},
            ]
        },
        {
            'emotion': 'Sad',
            'songs': [
                {'title': 'Someone Like You', 'artist': 'Adele', 'genre': 'Pop Ballad', 'youtube_url': 'https://www.youtube.com/watch?v=hLQl3WQQoQ0', 'spotify_url': 'https://open.spotify.com/track/1zwMYTA5nlNjZxYrvBB2pV'},
                {'title': 'Fix You', 'artist': 'Coldplay', 'genre': 'Alternative Rock', 'youtube_url': 'https://www.youtube.com/watch?v=k4V3Mo61fJM', 'spotify_url': 'https://open.spotify.com/track/7LVHVU3tWfcxj5aiPFEW4Q'},
                {'title': 'Hurt', 'artist': 'Johnny Cash', 'genre': 'Country', 'youtube_url': 'https://www.youtube.com/watch?v=8AHCfZTRGiI', 'spotify_url': 'https://open.spotify.com/track/28cnXtME493VX9NOw9cIUh'},
                {'title': 'The Night We Met', 'artist': 'Lord Huron', 'genre': 'Indie Folk', 'youtube_url': 'https://www.youtube.com/watch?v=KtlgYxa6BMU', 'spotify_url': 'https://open.spotify.com/track/0QZ5yyl6B6utIWkxeBDxQN'},
            ]
        },
        {
            'emotion': 'Tired',
            'songs': [
                {'title': 'Weightless', 'artist': 'Marconi Union', 'genre': 'Ambient', 'youtube_url': 'https://www.youtube.com/watch?v=UfcAVejslrU', 'spotify_url': 'https://open.spotify.com/track/6kkwzB6N3A3MzMb4TqDwFi'},
                {'title': 'Clair de Lune', 'artist': 'Debussy', 'genre': 'Classical', 'youtube_url': 'https://www.youtube.com/watch?v=CvFH_6DNRCY', 'spotify_url': 'https://open.spotify.com/track/1DGF6cBccPrxBoYSlpTfLi'},
                {'title': 'Sunset Lover', 'artist': 'Petit Biscuit', 'genre': 'Electronic', 'youtube_url': 'https://www.youtube.com/watch?v=wuCK-oiE3rM', 'spotify_url': 'https://open.spotify.com/track/3firkXnnAoNZlxNHlbIqUz'},
                {'title': 'Sleep', 'artist': 'Max Richter', 'genre': 'Ambient Classical', 'youtube_url': 'https://www.youtube.com/watch?v=4UAqmSJhN9M', 'spotify_url': 'https://open.spotify.com/track/6Y1CLPwYe7NnBOYN5NlpSS'},
            ]
        },
        {
            'emotion': 'Angry',
            'songs': [
                {'title': 'Break Stuff', 'artist': 'Limp Bizkit', 'genre': 'Nu Metal', 'youtube_url': 'https://www.youtube.com/watch?v=ZpUYjpKg9KY', 'spotify_url': 'https://open.spotify.com/track/7w9bgPAmPTtrkt2v16lVEH'},
                {'title': 'Killing in the Name', 'artist': 'Rage Against the Machine', 'genre': 'Rock', 'youtube_url': 'https://www.youtube.com/watch?v=bWXazVhlyxQ', 'spotify_url': 'https://open.spotify.com/track/59WN2psjkt1tyaxjspN8fp'},
                {'title': 'Bodies', 'artist': 'Drowning Pool', 'genre': 'Metal', 'youtube_url': 'https://www.youtube.com/watch?v=04F4xlWSFh0', 'spotify_url': 'https://open.spotify.com/track/3rvROF3XEuY0S4AEaVvLtI'},
                {'title': 'Chop Suey!', 'artist': 'System of a Down', 'genre': 'Metal', 'youtube_url': 'https://www.youtube.com/watch?v=CSvFpBOe8eY', 'spotify_url': 'https://open.spotify.com/track/2DlHlPMa4M17kufBvI2lEN'},
            ]
        },
        {
            'emotion': 'Stressed',
            'songs': [
                {'title': 'Breathe Me', 'artist': 'Sia', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=wHOH3VMHVx8', 'spotify_url': 'https://open.spotify.com/track/3PJNjjPFGZLJdMzRCrqxlO'},
                {'title': 'Orinoco Flow', 'artist': 'Enya', 'genre': 'New Age', 'youtube_url': 'https://www.youtube.com/watch?v=LTrk4X9ACtw', 'spotify_url': 'https://open.spotify.com/track/2fXKyAyPrEa24c6PJyqznF'},
                {'title': 'Ocean Eyes', 'artist': 'Billie Eilish', 'genre': 'Electropop', 'youtube_url': 'https://www.youtube.com/watch?v=viimfQi_pUw', 'spotify_url': 'https://open.spotify.com/track/7hDVYcQq6MxkdJGweuCtl9'},
                {'title': 'Strawberry Swing', 'artist': 'Coldplay', 'genre': 'Alternative Rock', 'youtube_url': 'https://www.youtube.com/watch?v=h3pJZSTQqIg', 'spotify_url': 'https://open.spotify.com/track/6RjkxzFkawz40HJnHKwgVd'},
            ]
        },
        {
            'emotion': 'Neutral',
            'songs': [
                {'title': 'Lovely Day', 'artist': 'Bill Withers', 'genre': 'Soul', 'youtube_url': 'https://www.youtube.com/watch?v=bEeaS6fuUoA', 'spotify_url': 'https://open.spotify.com/track/0bRXwKfigvpKZUurwqAlEh'},
                {'title': 'Here Comes the Sun', 'artist': 'The Beatles', 'genre': 'Rock', 'youtube_url': 'https://www.youtube.com/watch?v=KQetemT1sWc', 'spotify_url': 'https://open.spotify.com/track/6dGnYIeXmHdcikdzNNDMm2'},
                {'title': 'Budapest', 'artist': 'George Ezra', 'genre': 'Folk Pop', 'youtube_url': 'https://www.youtube.com/watch?v=VHrLPs3_1Fs', 'spotify_url': 'https://open.spotify.com/track/6kGvvXbIflwMQzsdj1J7ZY'},
                {'title': 'Electric Feel', 'artist': 'MGMT', 'genre': 'Indie Electronic', 'youtube_url': 'https://www.youtube.com/watch?v=MmZexg8sxyk', 'spotify_url': 'https://open.spotify.com/track/3FtYbEfBqAlGO46NUDQSAt'},
            ]
        }
    ]
    
    for emotion_music in music_data:
        emotion = emotion_objects.get(emotion_music['emotion'])
        if emotion:
            for i, song in enumerate(emotion_music['songs']):
                music = MusicRecommendation(
                    emotion_id=emotion.id,
                    title=song['title'],
                    artist=song['artist'],
                    genre=song['genre'],
                    youtube_url=song['youtube_url'],
                    spotify_url=song['spotify_url'],
                    popularity_score=10.0 - (i * 0.5)
                )
                db.session.add(music)
    
    db.session.commit()
    print("Database seeded successfully!")
