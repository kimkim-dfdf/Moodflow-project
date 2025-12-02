import { BookOpen } from 'lucide-react';

const BookCard = ({ book, showTags = false }) => {
  return (
    <div className="book-card">
      <div className="book-icon">
        <BookOpen size={24} />
      </div>
      <div className="book-info">
        <h4 className="book-title">{book.title}</h4>
        <p className="book-author">{book.author}</p>
        <span className="book-genre">{book.genre}</span>
        {book.description && (
          <p className="book-description">{book.description}</p>
        )}
        {showTags && book.tags && book.tags.length > 0 && (
          <div className="book-tags">
            {book.tags.map((tag) => (
              <span 
                key={tag.id} 
                className="book-tag-pill"
                style={{ '--pill-color': tag.color }}
              >
                {tag.name}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BookCard;
