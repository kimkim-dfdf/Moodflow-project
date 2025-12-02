def seed_database(db):
    from models import Emotion, MusicRecommendation, BookRecommendation
    
    if Emotion.query.first():
        return
    
    # Emotions
    emotions = [
        {'name': 'Happy', 'emoji': '😊', 'color': '#FFD93D'},
        {'name': 'Sad', 'emoji': '😢', 'color': '#6B7FD7'},
        {'name': 'Tired', 'emoji': '😴', 'color': '#8B4513'},
        {'name': 'Angry', 'emoji': '😠', 'color': '#FF6B6B'},
        {'name': 'Stressed', 'emoji': '😰', 'color': '#FF9F43'},
        {'name': 'Neutral', 'emoji': '😐', 'color': '#95A5A6'}
    ]
    
    emo_map = {}
    for e in emotions:
        obj = Emotion(**e)
        db.session.add(obj)
        db.session.flush()
        emo_map[e['name']] = obj
    
    # Music data
    music = {
        'Happy': [
            ('Happy', 'Pharrell Williams', 'Pop', 'ZbZSe6N_BXs'),
            ('Good as Hell', 'Lizzo', 'Pop', 'SmbmeOgWsqE'),
            ('Walking on Sunshine', 'Katrina and the Waves', 'Pop Rock', 'iPUmE-tne5U'),
            ('Uptown Funk', 'Bruno Mars', 'Funk Pop', 'OPf0YbXqDm0'),
        ],
        'Sad': [
            ('Someone Like You', 'Adele', 'Pop Ballad', 'hLQl3WQQoQ0'),
            ('Fix You', 'Coldplay', 'Alternative Rock', 'k4V3Mo61fJM'),
            ('Hurt', 'Johnny Cash', 'Country', '8AHCfZTRGiI'),
            ('The Night We Met', 'Lord Huron', 'Indie Folk', 'KtlgYxa6BMU'),
        ],
        'Tired': [
            ('Weightless', 'Marconi Union', 'Ambient', 'UfcAVejslrU'),
            ('Clair de Lune', 'Debussy', 'Classical', 'CvFH_6DNRCY'),
            ('Sunset Lover', 'Petit Biscuit', 'Electronic', 'wuCK-oiE3rM'),
            ('Sleep', 'Max Richter', 'Ambient Classical', '4UAqmSJhN9M'),
        ],
        'Angry': [
            ('Break Stuff', 'Limp Bizkit', 'Nu Metal', 'ZpUYjpKg9KY'),
            ('Killing in the Name', 'Rage Against the Machine', 'Rock', 'bWXazVhlyxQ'),
            ('Bodies', 'Drowning Pool', 'Metal', '04F4xlWSFh0'),
            ('Chop Suey!', 'System of a Down', 'Metal', 'CSvFpBOe8eY'),
        ],
        'Stressed': [
            ('Breathe Me', 'Sia', 'Pop', 'wHOH3VMHVx8'),
            ('Orinoco Flow', 'Enya', 'New Age', 'LTrk4X9ACtw'),
            ('Ocean Eyes', 'Billie Eilish', 'Electropop', 'viimfQi_pUw'),
            ('Strawberry Swing', 'Coldplay', 'Alternative Rock', 'h3pJZSTQqIg'),
        ],
        'Neutral': [
            ('Lovely Day', 'Bill Withers', 'Soul', 'bEeaS6fuUoA'),
            ('Here Comes the Sun', 'The Beatles', 'Rock', 'KQetemT1sWc'),
            ('Budapest', 'George Ezra', 'Folk Pop', 'VHrLPs3_1Fs'),
            ('Electric Feel', 'MGMT', 'Indie Electronic', 'MmZexg8sxyk'),
        ]
    }
    
    for emo_name, songs in music.items():
        emo = emo_map.get(emo_name)
        if emo:
            for i, (title, artist, genre, vid) in enumerate(songs):
                db.session.add(MusicRecommendation(emotion_id=emo.id, title=title, artist=artist, genre=genre, youtube_url='https://www.youtube.com/watch?v=' + vid, popularity_score=10.0 - i * 0.5))
    
    # Books data
    books = {
        'Happy': [
            ('The Alchemist', 'Paulo Coelho', 'Fiction', 'A magical story about following your dreams'),
            ('Big Magic', 'Elizabeth Gilbert', 'Self-Help', 'Creative living beyond fear'),
            ('The Happiness Project', 'Gretchen Rubin', 'Self-Help', 'A year-long journey to discover happiness'),
            ('Yes Please', 'Amy Poehler', 'Memoir', 'Hilarious and inspiring stories'),
        ],
        'Sad': [
            ('When Breath Becomes Air', 'Paul Kalanithi', 'Memoir', 'A profound reflection on life and death'),
            ('The Year of Magical Thinking', 'Joan Didion', 'Memoir', 'Processing grief and loss'),
            ('Tiny Beautiful Things', 'Cheryl Strayed', 'Self-Help', 'Advice on life and love'),
            ('Norwegian Wood', 'Haruki Murakami', 'Fiction', 'A story of love and melancholy'),
        ],
        'Tired': [
            ('The Little Prince', 'Antoine de Saint-Exupery', 'Fiction', 'A gentle tale with deep meaning'),
            ('Winnie-the-Pooh', 'A.A. Milne', 'Fiction', 'Comforting adventures in the Hundred Acre Wood'),
            ('The House in the Cerulean Sea', 'TJ Klune', 'Fantasy', 'A cozy, heartwarming fantasy'),
            ('Hygge: The Danish Art of Living', 'Meik Wiking', 'Lifestyle', 'Finding comfort in simple pleasures'),
        ],
        'Angry': [
            ('The Art of War', 'Sun Tzu', 'Philosophy', 'Ancient wisdom on strategy'),
            ('Rage', 'Bob Woodward', 'Non-Fiction', 'Understanding power and politics'),
            ('Anger: Wisdom for Cooling the Flames', 'Thich Nhat Hanh', 'Self-Help', 'Buddhist approach to managing anger'),
            ('The Count of Monte Cristo', 'Alexandre Dumas', 'Classic', 'An epic tale of revenge and redemption'),
        ],
        'Stressed': [
            ('The Power of Now', 'Eckhart Tolle', 'Self-Help', 'Living in the present moment'),
            ('Wherever You Go, There You Are', 'Jon Kabat-Zinn', 'Self-Help', 'Mindfulness meditation in everyday life'),
            ('The Untethered Soul', 'Michael Singer', 'Self-Help', 'Journey beyond yourself'),
            ('Why Zebras Dont Get Ulcers', 'Robert Sapolsky', 'Science', 'Understanding stress and health'),
        ],
        'Neutral': [
            ('Sapiens', 'Yuval Noah Harari', 'Non-Fiction', 'A brief history of humankind'),
            ('Thinking, Fast and Slow', 'Daniel Kahneman', 'Psychology', 'How we make decisions'),
            ('Atomic Habits', 'James Clear', 'Self-Help', 'Tiny changes for remarkable results'),
            ('A Short History of Nearly Everything', 'Bill Bryson', 'Science', 'Exploring the wonders of science'),
        ]
    }
    
    for emo_name, book_list in books.items():
        emo = emo_map.get(emo_name)
        if emo:
            for i, (title, author, genre, desc) in enumerate(book_list):
                db.session.add(BookRecommendation(emotion_id=emo.id, title=title, author=author, genre=genre, description=desc, popularity_score=10.0 - i * 0.5))
    
    db.session.commit()
    print("Database seeded!")
