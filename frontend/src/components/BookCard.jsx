import { BookOpen } from 'lucide-react';

const BookCard = ({ book }) => {
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
      </div>
    </div>
  );
};

export default BookCard;
