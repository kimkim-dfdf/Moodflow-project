# ==============================================
# MoodFlow - Static Data Seeding
# ==============================================
# This file seeds the static data for emotions,
# music, books, and book tags into the database.
# Called automatically when the app starts.
# ==============================================

from models import db, Emotion, Music, BookTag, Book


def seed_all_static_data():
    """
    Seed all static data into the database.
    This function is idempotent - safe to run multiple times.
    It only adds data if the tables are empty.
    """
    
    seed_emotions()
    seed_book_tags()
    seed_music()
    seed_books()
    
    print("Static data seeding complete.")


def seed_emotions():
    """
    Seed the 6 emotions into the database.
    """
    
    # Check if emotions already exist
    existing_count = Emotion.query.count()
    if existing_count > 0:
        print("Emotions already exist, skipping...")
        return
    
    # Define all emotions
    emotions_data = [
        {'name': 'Happy', 'emoji': '😊', 'color': '#FFD93D'},
        {'name': 'Sad', 'emoji': '😢', 'color': '#6B7FD7'},
        {'name': 'Tired', 'emoji': '😴', 'color': '#8B4513'},
        {'name': 'Angry', 'emoji': '😠', 'color': '#FF6B6B'},
        {'name': 'Stressed', 'emoji': '😰', 'color': '#FF9F43'},
        {'name': 'Neutral', 'emoji': '😐', 'color': '#95A5A6'}
    ]
    
    # Add each emotion to database
    for emotion_data in emotions_data:
        emotion = Emotion()
        emotion.name = emotion_data['name']
        emotion.emoji = emotion_data['emoji']
        emotion.color = emotion_data['color']
        db.session.add(emotion)
    
    db.session.commit()
    print("Seeded 6 emotions.")


def seed_book_tags():
    """
    Seed the 10 book tags into the database.
    """
    
    # Check if tags already exist
    existing_count = BookTag.query.count()
    if existing_count > 0:
        print("Book tags already exist, skipping...")
        return
    
    # Define all book tags
    tags_data = [
        {'name': 'Hopeful', 'slug': 'hopeful', 'color': '#22c55e'},
        {'name': 'Comforting', 'slug': 'comforting', 'color': '#f97316'},
        {'name': 'Peaceful', 'slug': 'peaceful', 'color': '#06b6d4'},
        {'name': 'Growth', 'slug': 'growth', 'color': '#8b5cf6'},
        {'name': 'Emotional', 'slug': 'emotional', 'color': '#ec4899'},
        {'name': 'Escapism', 'slug': 'escapism', 'color': '#6366f1'},
        {'name': 'Recharge', 'slug': 'recharge', 'color': '#14b8a6'},
        {'name': 'Courage', 'slug': 'courage', 'color': '#dc2626'},
        {'name': 'New Perspective', 'slug': 'new-perspective', 'color': '#0d9488'},
        {'name': 'Focus', 'slug': 'focus', 'color': '#3b82f6'}
    ]
    
    # Add each tag to database
    for tag_data in tags_data:
        tag = BookTag()
        tag.name = tag_data['name']
        tag.slug = tag_data['slug']
        tag.color = tag_data['color']
        db.session.add(tag)
    
    db.session.commit()
    print("Seeded 10 book tags.")


def seed_music():
    """
    Seed the music recommendations into the database.
    4 songs per emotion = 24 songs total.
    """
    
    # Check if music already exists
    existing_count = Music.query.count()
    if existing_count > 0:
        print("Music already exists, skipping...")
        return
    
    # Define all music
    music_data = [
        # Happy songs
        {'emotion': 'Happy', 'title': 'Happy', 'artist': 'Pharrell Williams', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=ZbZSe6N_BXs'},
        {'emotion': 'Happy', 'title': 'Good as Hell', 'artist': 'Lizzo', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=SmbmeOgWsqE'},
        {'emotion': 'Happy', 'title': 'Walking on Sunshine', 'artist': 'Katrina and the Waves', 'genre': 'Pop Rock', 'youtube_url': 'https://www.youtube.com/watch?v=iPUmE-tne5U'},
        {'emotion': 'Happy', 'title': 'Uptown Funk', 'artist': 'Bruno Mars', 'genre': 'Funk Pop', 'youtube_url': 'https://www.youtube.com/watch?v=OPf0YbXqDm0'},
        
        # Sad songs
        {'emotion': 'Sad', 'title': 'Someone Like You', 'artist': 'Adele', 'genre': 'Pop Ballad', 'youtube_url': 'https://www.youtube.com/watch?v=hLQl3WQQoQ0'},
        {'emotion': 'Sad', 'title': 'Fix You', 'artist': 'Coldplay', 'genre': 'Alternative Rock', 'youtube_url': 'https://www.youtube.com/watch?v=k4V3Mo61fJM'},
        {'emotion': 'Sad', 'title': 'Hurt', 'artist': 'Johnny Cash', 'genre': 'Country', 'youtube_url': 'https://www.youtube.com/watch?v=8AHCfZTRGiI'},
        {'emotion': 'Sad', 'title': 'The Night We Met', 'artist': 'Lord Huron', 'genre': 'Indie Folk', 'youtube_url': 'https://www.youtube.com/watch?v=KtlgYxa6BMU'},
        
        # Tired songs
        {'emotion': 'Tired', 'title': 'Weightless', 'artist': 'Marconi Union', 'genre': 'Ambient', 'youtube_url': 'https://www.youtube.com/watch?v=UfcAVejslrU'},
        {'emotion': 'Tired', 'title': 'Clair de Lune', 'artist': 'Debussy', 'genre': 'Classical', 'youtube_url': 'https://www.youtube.com/watch?v=CvFH_6DNRCY'},
        {'emotion': 'Tired', 'title': 'Sunset Lover', 'artist': 'Petit Biscuit', 'genre': 'Electronic', 'youtube_url': 'https://www.youtube.com/watch?v=wuCK-oiE3rM'},
        {'emotion': 'Tired', 'title': 'Sleep', 'artist': 'Max Richter', 'genre': 'Ambient Classical', 'youtube_url': 'https://www.youtube.com/watch?v=4UAqmSJhN9M'},
        
        # Angry songs
        {'emotion': 'Angry', 'title': 'Break Stuff', 'artist': 'Limp Bizkit', 'genre': 'Nu Metal', 'youtube_url': 'https://www.youtube.com/watch?v=ZpUYjpKg9KY'},
        {'emotion': 'Angry', 'title': 'Killing in the Name', 'artist': 'Rage Against the Machine', 'genre': 'Rock', 'youtube_url': 'https://www.youtube.com/watch?v=bWXazVhlyxQ'},
        {'emotion': 'Angry', 'title': 'Bodies', 'artist': 'Drowning Pool', 'genre': 'Metal', 'youtube_url': 'https://www.youtube.com/watch?v=04F4xlWSFh0'},
        {'emotion': 'Angry', 'title': 'Chop Suey!', 'artist': 'System of a Down', 'genre': 'Metal', 'youtube_url': 'https://www.youtube.com/watch?v=CSvFpBOe8eY'},
        
        # Stressed songs
        {'emotion': 'Stressed', 'title': 'Breathe Me', 'artist': 'Sia', 'genre': 'Pop', 'youtube_url': 'https://www.youtube.com/watch?v=wHOH3VMHVx8'},
        {'emotion': 'Stressed', 'title': 'Orinoco Flow', 'artist': 'Enya', 'genre': 'New Age', 'youtube_url': 'https://www.youtube.com/watch?v=LTrk4X9ACtw'},
        {'emotion': 'Stressed', 'title': 'Ocean Eyes', 'artist': 'Billie Eilish', 'genre': 'Electropop', 'youtube_url': 'https://www.youtube.com/watch?v=viimfQi_pUw'},
        {'emotion': 'Stressed', 'title': 'Strawberry Swing', 'artist': 'Coldplay', 'genre': 'Alternative Rock', 'youtube_url': 'https://www.youtube.com/watch?v=h3pJZSTQqIg'},
        
        # Neutral songs
        {'emotion': 'Neutral', 'title': 'Lovely Day', 'artist': 'Bill Withers', 'genre': 'Soul', 'youtube_url': 'https://www.youtube.com/watch?v=bEeaS6fuUoA'},
        {'emotion': 'Neutral', 'title': 'Here Comes the Sun', 'artist': 'The Beatles', 'genre': 'Rock', 'youtube_url': 'https://www.youtube.com/watch?v=KQetemT1sWc'},
        {'emotion': 'Neutral', 'title': 'Budapest', 'artist': 'George Ezra', 'genre': 'Folk Pop', 'youtube_url': 'https://www.youtube.com/watch?v=VHrLPs3_1Fs'},
        {'emotion': 'Neutral', 'title': 'Electric Feel', 'artist': 'MGMT', 'genre': 'Indie Electronic', 'youtube_url': 'https://www.youtube.com/watch?v=MmZexg8sxyk'}
    ]
    
    # Add each music to database
    for music_item in music_data:
        music = Music(
            emotion=music_item['emotion'],
            title=music_item['title'],
            artist=music_item['artist'],
            genre=music_item['genre'],
            youtube_url=music_item['youtube_url']
        )
        db.session.add(music)
    
    db.session.commit()
    print("Seeded 24 music recommendations.")


def seed_books():
    """
    Seed the book recommendations into the database.
    15 books with tags.
    """
    
    # Check if books already exist
    existing_count = Book.query.count()
    if existing_count > 0:
        print("Books already exist, skipping...")
        return
    
    # Define all books
    books_data = [
        # Happy books
        {'emotion': 'Happy', 'title': 'The Alchemist', 'author': 'Paulo Coelho', 'genre': 'Fiction', 'description': 'A magical story about following your dreams', 'tags': 'hopeful,growth,new-perspective'},
        {'emotion': 'Happy', 'title': 'Big Magic', 'author': 'Elizabeth Gilbert', 'genre': 'Self-Help', 'description': 'Creative living beyond fear', 'tags': 'growth,focus,hopeful'},
        {'emotion': 'Happy', 'title': 'The Happiness Project', 'author': 'Gretchen Rubin', 'genre': 'Self-Help', 'description': 'A year-long journey to discover happiness', 'tags': 'hopeful,growth,recharge'},
        {'emotion': 'Happy', 'title': 'Yes Please', 'author': 'Amy Poehler', 'genre': 'Memoir', 'description': 'Hilarious and inspiring stories', 'tags': 'hopeful,courage,emotional'},
        
        # Sad books
        {'emotion': 'Sad', 'title': 'When Breath Becomes Air', 'author': 'Paul Kalanithi', 'genre': 'Memoir', 'description': 'A profound reflection on life and death', 'tags': 'emotional,comforting,growth'},
        {'emotion': 'Sad', 'title': 'The Year of Magical Thinking', 'author': 'Joan Didion', 'genre': 'Memoir', 'description': 'Processing grief and loss', 'tags': 'comforting,emotional,peaceful'},
        {'emotion': 'Sad', 'title': 'Tiny Beautiful Things', 'author': 'Cheryl Strayed', 'genre': 'Self-Help', 'description': 'Advice on life and love', 'tags': 'comforting,emotional,peaceful'},
        {'emotion': 'Sad', 'title': 'Norwegian Wood', 'author': 'Haruki Murakami', 'genre': 'Fiction', 'description': 'A story of love and melancholy', 'tags': 'emotional,escapism,peaceful'},
        
        # Tired books
        {'emotion': 'Tired', 'title': 'The Little Prince', 'author': 'Antoine de Saint-Exupery', 'genre': 'Fiction', 'description': 'A gentle tale with deep meaning', 'tags': 'hopeful,escapism,new-perspective'},
        {'emotion': 'Tired', 'title': 'Winnie-the-Pooh', 'author': 'A.A. Milne', 'genre': 'Fiction', 'description': 'Comforting adventures in the Hundred Acre Wood', 'tags': 'comforting,recharge,peaceful'},
        {'emotion': 'Tired', 'title': 'The House in the Cerulean Sea', 'author': 'TJ Klune', 'genre': 'Fantasy', 'description': 'A cozy, heartwarming fantasy', 'tags': 'escapism,comforting,peaceful'},
        {'emotion': 'Tired', 'title': 'Hygge: The Danish Art of Living', 'author': 'Meik Wiking', 'genre': 'Lifestyle', 'description': 'Finding comfort in simple pleasures', 'tags': 'recharge,peaceful,comforting'},
        
        # Angry books
        {'emotion': 'Angry', 'title': 'The Art of War', 'author': 'Sun Tzu', 'genre': 'Philosophy', 'description': 'Ancient wisdom on strategy', 'tags': 'courage,focus,growth'},
        {'emotion': 'Angry', 'title': 'Rage', 'author': 'Bob Woodward', 'genre': 'Non-Fiction', 'description': 'Understanding power and politics', 'tags': 'emotional,courage,comforting'},
        {'emotion': 'Angry', 'title': 'Anger: Wisdom for Cooling the Flames', 'author': 'Thich Nhat Hanh', 'genre': 'Self-Help', 'description': 'Buddhist approach to managing anger', 'tags': 'peaceful,new-perspective,growth'}
    ]
    
    # Add each book to database
    for book_item in books_data:
        book = Book(
            emotion=book_item['emotion'],
            title=book_item['title'],
            author=book_item['author'],
            genre=book_item['genre'],
            description=book_item['description'],
            tags=book_item['tags']
        )
        db.session.add(book)
    
    db.session.commit()
    print("Seeded 15 books.")
