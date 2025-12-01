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
            'color': '#A8A8A8',
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
                {'title': 'Happy', 'artist': 'Pharrell Williams', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=ZbZSe6N_BXs'},
                {'title': 'Good as Hell', 'artist': 'Lizzo', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=SmbmeOgWsqE'},
                {'title': 'Walking on Sunshine', 'artist': 'Katrina and the Waves', 'genre': 'Pop Rock', 'youtube_url': 'https://www.youtube.com/watch?v=iPUmE-tne5U'},
                {'title': 'Uptown Funk', 'artist': 'Bruno Mars', 'genre': 'Funk Pop', 'youtube_url': 'https://www.youtube.com/watch?v=OPf0YbXqDm0'},
            ]
        },
        {
            'emotion': 'Sad',
            'songs': [
                {'title': 'Someone Like You', 'artist': 'Adele', 'genre': 'Pop Ballad', 'youtube_url': 'https://www.youtube.com/watch?v=hLQl3WQQoQ0'},
                {'title': 'Fix You', 'artist': 'Coldplay', 'genre': 'Alternative Rock', 'youtube_url': 'https://www.youtube.com/watch?v=k4V3Mo61fJM'},
                {'title': 'Hurt', 'artist': 'Johnny Cash', 'genre': 'Country', 'youtube_url': 'https://www.youtube.com/watch?v=8AHCfZTRGiI'},
                {'title': 'The Night We Met', 'artist': 'Lord Huron', 'genre': 'Indie Folk', 'youtube_url': 'https://www.youtube.com/watch?v=KtlgYxa6BMU'},
            ]
        },
        {
            'emotion': 'Tired',
            'songs': [
                {'title': 'Weightless', 'artist': 'Marconi Union', 'genre': 'Ambient', 'youtube_url': 'https://www.youtube.com/watch?v=UfcAVejslrU'},
                {'title': 'Clair de Lune', 'artist': 'Debussy', 'genre': 'Classical', 'youtube_url': 'https://www.youtube.com/watch?v=CvFH_6DNRCY'},
                {'title': 'Sunset Lover', 'artist': 'Petit Biscuit', 'genre': 'Electronic', 'youtube_url': 'https://www.youtube.com/watch?v=wuCK-oiE3rM'},
                {'title': 'Sleep', 'artist': 'Max Richter', 'genre': 'Ambient Classical', 'youtube_url': 'https://www.youtube.com/watch?v=4UAqmSJhN9M'},
            ]
        },
        {
            'emotion': 'Angry',
            'songs': [
                {'title': 'Break Stuff', 'artist': 'Limp Bizkit', 'genre': 'Nu Metal', 'youtube_url': 'https://www.youtube.com/watch?v=ZpUYjpKg9KY'},
                {'title': 'Killing in the Name', 'artist': 'Rage Against the Machine', 'genre': 'Rock', 'youtube_url': 'https://www.youtube.com/watch?v=bWXazVhlyxQ'},
                {'title': 'Bodies', 'artist': 'Drowning Pool', 'genre': 'Metal', 'youtube_url': 'https://www.youtube.com/watch?v=04F4xlWSFh0'},
                {'title': 'Chop Suey!', 'artist': 'System of a Down', 'genre': 'Metal', 'youtube_url': 'https://www.youtube.com/watch?v=CSvFpBOe8eY'},
            ]
        },
        {
            'emotion': 'Stressed',
            'songs': [
                {'title': 'Breathe Me', 'artist': 'Sia', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=wHOH3VMHVx8'},
                {'title': 'Orinoco Flow', 'artist': 'Enya', 'genre': 'New Age', 'youtube_url': 'https://www.youtube.com/watch?v=LTrk4X9ACtw'},
                {'title': 'Ocean Eyes', 'artist': 'Billie Eilish', 'genre': 'Electropop', 'youtube_url': 'https://www.youtube.com/watch?v=viimfQi_pUw'},
                {'title': 'Strawberry Swing', 'artist': 'Coldplay', 'genre': 'Alternative Rock', 'youtube_url': 'https://www.youtube.com/watch?v=h3pJZSTQqIg'},
            ]
        },
        {
            'emotion': 'Neutral',
            'songs': [
                {'title': 'Lovely Day', 'artist': 'Bill Withers', 'genre': 'Soul', 'youtube_url': 'https://www.youtube.com/watch?v=bEeaS6fuUoA'},
                {'title': 'Here Comes the Sun', 'artist': 'The Beatles', 'genre': 'Rock', 'youtube_url': 'https://www.youtube.com/watch?v=KQetemT1sWc'},
                {'title': 'Budapest', 'artist': 'George Ezra', 'genre': 'Folk Pop', 'youtube_url': 'https://www.youtube.com/watch?v=VHrLPs3_1Fs'},
                {'title': 'Electric Feel', 'artist': 'MGMT', 'genre': 'Indie Electronic', 'youtube_url': 'https://www.youtube.com/watch?v=MmZexg8sxyk'},
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
                    popularity_score=10.0 - (i * 0.5)
                )
                db.session.add(music)
    
    db.session.commit()
    print("Database seeded successfully!")
