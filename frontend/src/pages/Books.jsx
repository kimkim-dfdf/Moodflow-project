import { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import { BookOpen, X, Search, Heart, Share2, Star, Trash2, User, ShoppingCart, CreditCard, Check } from 'lucide-react';

// 책 카드 컴포넌트
function BookCard(props) {
  var book = props.book;
  var isFavorite = props.isFavorite || false;
  var [imgError, setImgError] = useState(false);
  
  return (
    <div className="book-card" onClick={function() { if (props.onOpenDetail) props.onOpenDetail(book); }}>
      <div className="book-cover">
        {imgError ? (
          <div className="book-icon"><BookOpen size={24} /></div>
        ) : (
          <img src={'/books/' + book.id + '.jpg'} alt={book.title} onError={function() { setImgError(true); }} className="book-cover-img" />
        )}
      </div>
      <div className="book-info">
        <div className="book-title-row">
          <h4 className="book-title">{book.title}</h4>
          <button className={'favorite-btn ' + (isFavorite ? 'active' : '')} onClick={function(e) { e.stopPropagation(); if (props.onToggleFavorite) props.onToggleFavorite(book.id); }}>
            <Heart size={18} fill={isFavorite ? '#ef4444' : 'none'} />
          </button>
        </div>
        <p className="book-author">{book.author}</p>
        <span className="book-genre">{book.genre}</span>
        <div className="book-price-row">
          <span className="book-price">${book.price.toFixed(2)}</span>
          <button className="add-to-cart-btn" onClick={function(e) { e.stopPropagation(); if (props.onAddToCart) props.onAddToCart(book); }}>
            <ShoppingCart size={16} />
          </button>
        </div>
        {props.showTags && book.tags && book.tags.length > 0 && (
          <div className="book-tags">
            {book.tags.map(function(tag) { return <span key={tag.id} className="book-tag-pill">{tag.name}</span>; })}
          </div>
        )}
      </div>
    </div>
  );
}

// 책 상세 모달
function BookDetailModal(props) {
  var book = props.book;
  var [reviews, setReviews] = useState([]);
  var [reviewRating, setReviewRating] = useState(5);
  var [reviewContent, setReviewContent] = useState('');
  var [isSubmitting, setIsSubmitting] = useState(false);
  var [reviewError, setReviewError] = useState('');
  var [hasUserReview, setHasUserReview] = useState(false);
  var [modalImgError, setModalImgError] = useState(false);
  var [addedToCart, setAddedToCart] = useState(false);
  
  useEffect(function() {
    if (book) {
      api.get('/books/' + book.id + '/reviews').then(function(res) {
        setReviews(res.data);
        var hasReview = false;
        for (var i = 0; i < res.data.length; i++) {
          if (Number(res.data[i].user_id) === Number(props.currentUserId)) {
            hasReview = true;
            break;
          }
        }
        setHasUserReview(hasReview);
      }).catch(function() { setReviews([]); });
    }
  }, [book]);
  
  if (!book) return null;
  
  function handleSubmitReview() {
    if (!reviewContent.trim()) { setReviewError('Please write a review'); return; }
    setIsSubmitting(true);
    api.post('/books/' + book.id + '/reviews', { rating: reviewRating, content: reviewContent }).then(function(res) {
      setReviews([res.data].concat(reviews));
      setReviewContent('');
      setHasUserReview(true);
      setIsSubmitting(false);
    }).catch(function(err) {
      setReviewError(err.response?.data?.error || 'Failed');
      setIsSubmitting(false);
    });
  }
  
  function handleDeleteReview(reviewId) {
    api.delete('/books/reviews/' + reviewId).then(function() {
      var newReviews = [];
      for (var i = 0; i < reviews.length; i++) {
        if (reviews[i].id !== reviewId) newReviews.push(reviews[i]);
      }
      setReviews(newReviews);
      setHasUserReview(false);
    });
  }
  
  function handleShare() {
    var text = 'Check out this book!\n\n' + book.title + ' by ' + book.author + '\nGenre: ' + book.genre + '\nPrice: $' + book.price.toFixed(2);
    var whatsappUrl = 'https://api.whatsapp.com/send?text=' + encodeURIComponent(text);
    window.open(whatsappUrl, '_blank');
  }
  
  // 별점 클릭 핸들러 생성 함수
  function createStarClickHandler(starValue) {
    return function() {
      setReviewRating(starValue);
    };
  }
  
  function renderStars(rating, interactive) {
    var stars = [];
    for (var i = 1; i <= 5; i++) {
      if (interactive) {
        stars.push(<button key={i} type="button" className="star-btn" onClick={createStarClickHandler(i)}><Star size={20} fill={i <= reviewRating ? '#fbbf24' : 'none'} color={i <= reviewRating ? '#fbbf24' : '#d1d5db'} /></button>);
      } else {
        stars.push(<Star key={i} size={16} fill={i <= rating ? '#fbbf24' : 'none'} color={i <= rating ? '#fbbf24' : '#d1d5db'} />);
      }
    }
    return stars;
  }
  
  return (
    <div className="modal-overlay" onClick={function(e) { if (e.target.className === 'modal-overlay') props.onClose(); }}>
      <div className="book-detail-modal">
        <button className="modal-close-btn" onClick={props.onClose}><X size={24} /></button>
        
        <div className="modal-header">
          <div className="modal-book-cover">
            {modalImgError ? <div className="modal-book-icon"><BookOpen size={48} /></div> : <img src={'/books/' + book.id + '.jpg'} alt={book.title} onError={function() { setModalImgError(true); }} className="modal-cover-img" />}
          </div>
          <div className="modal-title-section">
            <h2>{book.title}</h2>
            <p className="modal-author">{book.author}</p>
            <p className="modal-price">${book.price.toFixed(2)}</p>
          </div>
        </div>
        
        <div className="modal-body">
          <div className="modal-meta">
            <span className="modal-genre">{book.genre}</span>
            {book.emotion && <span className="modal-emotion">Recommended for: {book.emotion}</span>}
          </div>
          
          <div className="modal-reviews">
            <h4>Reviews ({reviews.length})</h4>
            
            {!hasUserReview && (
              <div className="review-form">
                <div className="review-rating-input">
                  <span>Your Rating:</span>
                  <div className="stars-input">{renderStars(reviewRating, true)}</div>
                </div>
                <textarea className="review-textarea" placeholder="Write your review..." value={reviewContent} onChange={function(e) { setReviewContent(e.target.value); }} rows={3} />
                {reviewError && <div className="review-error">{reviewError}</div>}
                <button className="review-submit-btn" onClick={handleSubmitReview} disabled={isSubmitting}>{isSubmitting ? 'Submitting...' : 'Submit Review'}</button>
              </div>
            )}
            
            {hasUserReview && <div className="review-notice">You have already reviewed this book.</div>}
            
            <div className="reviews-list">
              {reviews.length === 0 ? <p className="no-reviews">No reviews yet.</p> : reviews.map(function(review) {
                return (
                  <div key={review.id} className="review-item">
                    <div className="review-header">
                      <div className="review-user"><User size={16} /><span>{review.username}</span></div>
                      <div className="review-stars">{renderStars(review.rating, false)}</div>
                      {Number(review.user_id) === Number(props.currentUserId) && <button className="review-delete-btn" onClick={function() { handleDeleteReview(review.id); }}><Trash2 size={16} /></button>}
                    </div>
                    <p className="review-content">{review.content}</p>
                    <span className="review-date">{new Date(review.created_at).toLocaleDateString()}</span>
                  </div>
                );
              })}
            </div>
          </div>
          
          {book.description && <div className="modal-description"><h4>Description</h4><p>{book.description}</p></div>}
          
          {book.tags && book.tags.length > 0 && (
            <div className="modal-tags">
              <h4>Mood Tags</h4>
              <div className="modal-tags-list">
                {book.tags.map(function(tag) { return <span key={tag.id} className="modal-tag-pill" style={{ backgroundColor: tag.color || '#6B7280' }}>{tag.name}</span>; })}
              </div>
            </div>
          )}
        </div>
        
        <div className="modal-footer">
          <button className={'modal-favorite-btn ' + (props.isFavorite ? 'active' : '')} onClick={function() { props.onToggleFavorite(book.id); }}>
            <Heart size={20} fill={props.isFavorite ? '#ef4444' : 'none'} />
            {props.isFavorite ? 'Remove from Favorites' : 'Add to Favorites'}
          </button>
          <button className={'modal-cart-btn ' + (addedToCart ? 'added' : '')} onClick={function() { props.onAddToCart(book); setAddedToCart(true); setTimeout(function() { setAddedToCart(false); }, 2000); }}>
            {addedToCart ? <><Check size={20} />Added!</> : <><ShoppingCart size={20} />Add to Cart - ${book.price.toFixed(2)}</>}
          </button>
          <button className="modal-share-btn" onClick={handleShare}><Share2 size={20} />WhatsApp</button>
        </div>
      </div>
    </div>
  );
}

// 결제 모달
function CheckoutModal(props) {
  var [cardNumber, setCardNumber] = useState('');
  var [cardName, setCardName] = useState('');
  var [expiry, setExpiry] = useState('');
  var [cvv, setCvv] = useState('');
  var [isProcessing, setIsProcessing] = useState(false);
  var [error, setError] = useState('');
  var [success, setSuccess] = useState(false);
  
  function formatCardNumber(value) {
    var cleaned = value.replace(/\D/g, '');
    var formatted = '';
    for (var i = 0; i < cleaned.length && i < 16; i++) {
      if (i > 0 && i % 4 === 0) formatted = formatted + ' ';
      formatted = formatted + cleaned[i];
    }
    return formatted;
  }
  
  function formatExpiry(value) {
    var cleaned = value.replace(/\D/g, '');
    if (cleaned.length >= 2) return cleaned.substring(0, 2) + '/' + cleaned.substring(2, 4);
    return cleaned;
  }
  
  function handleSubmit(e) {
    e.preventDefault();
    var cleanCardNumber = cardNumber.replace(/\s/g, '');
    if (cleanCardNumber.length < 13) { setError('Invalid card number'); return; }
    if (!cardName.trim()) { setError('Name required'); return; }
    if (expiry.length < 5) { setError('Invalid expiry'); return; }
    if (cvv.length < 3) { setError('Invalid CVV'); return; }
    
    setIsProcessing(true);
    api.post('/checkout', { card_number: cleanCardNumber, card_name: cardName, expiry: expiry, cvv: cvv }).then(function() {
      setSuccess(true);
      setTimeout(function() { props.onCheckoutSuccess(); }, 2000);
    }).catch(function(err) {
      setError(err.response?.data?.error || 'Checkout failed');
      setIsProcessing(false);
    });
  }
  
  if (success) {
    return (
      <div className="modal-overlay"><div className="checkout-modal success-modal">
        <div className="success-content"><div className="success-icon"><Check size={48} /></div><h2>Purchase Complete!</h2><p>Total: ${props.total.toFixed(2)}</p></div>
      </div></div>
    );
  }
  
  return (
    <div className="modal-overlay" onClick={function(e) { if (e.target.className === 'modal-overlay') props.onClose(); }}>
      <div className="checkout-modal">
        <button className="modal-close-btn" onClick={props.onClose}><X size={24} /></button>
        <div className="checkout-header"><CreditCard size={28} /><h2>Checkout</h2></div>
        
        <div className="checkout-summary">
          <h3>Order Summary</h3>
          <div className="checkout-items">
            {props.cartItems.map(function(item) {
              return <div key={item.id} className="checkout-item"><span className="checkout-item-title">{item.title}</span><span className="checkout-item-qty">x{item.quantity}</span><span className="checkout-item-price">${(item.price * item.quantity).toFixed(2)}</span></div>;
            })}
          </div>
          <div className="checkout-total"><span>Total</span><span>${props.total.toFixed(2)}</span></div>
        </div>
        
        <form className="checkout-form" onSubmit={handleSubmit}>
          <h3>Payment Details</h3>
          <p className="checkout-note">Simulated payment for demo purposes.</p>
          <div className="form-group"><label>Card Number</label><input type="text" placeholder="1234 5678 9012 3456" value={cardNumber} onChange={function(e) { setCardNumber(formatCardNumber(e.target.value)); }} className="card-input" /></div>
          <div className="form-group"><label>Cardholder Name</label><input type="text" placeholder="John Doe" value={cardName} onChange={function(e) { setCardName(e.target.value); }} className="card-input" /></div>
          <div className="form-row">
            <div className="form-group half"><label>Expiry</label><input type="text" placeholder="MM/YY" value={expiry} onChange={function(e) { setExpiry(formatExpiry(e.target.value)); }} className="card-input" /></div>
            <div className="form-group half"><label>CVV</label><input type="text" placeholder="123" value={cvv} onChange={function(e) { var c = e.target.value.replace(/\D/g, ''); if (c.length <= 4) setCvv(c); }} className="card-input" /></div>
          </div>
          {error && <div className="checkout-error">{error}</div>}
          <button type="submit" className="checkout-submit-btn" disabled={isProcessing}>{isProcessing ? 'Processing...' : 'Pay $' + props.total.toFixed(2)}</button>
        </form>
      </div>
    </div>
  );
}

// 장바구니 뷰
function CartView(props) {
  if (props.cartItems.length === 0) {
    return <div className="empty-state"><ShoppingCart size={48} /><p>Your cart is empty</p></div>;
  }
  
  return (
    <div className="cart-view">
      <div className="cart-items">
        {props.cartItems.map(function(item) {
          return (
            <div key={item.id} className="cart-item">
              <div className="cart-item-info"><h4 className="cart-item-title">{item.title}</h4><p className="cart-item-author">{item.author}</p><p className="cart-item-qty">Qty: {item.quantity}</p></div>
              <div className="cart-item-right"><span className="cart-item-price">${(item.price * item.quantity).toFixed(2)}</span><button className="cart-remove-btn" onClick={function() { props.onRemoveItem(item.id); }}><Trash2 size={18} /></button></div>
            </div>
          );
        })}
      </div>
      <div className="cart-summary">
        <div className="cart-total-row"><span>Total ({props.cartItems.length} items)</span><span className="cart-total-amount">${props.total.toFixed(2)}</span></div>
        <button className="checkout-btn" onClick={props.onCheckout}><CreditCard size={20} />Proceed to Checkout</button>
      </div>
    </div>
  );
}

// 로컬 스토리지 헬퍼
function getFavorites() { try { var s = localStorage.getItem('book_favorites'); if (s) return JSON.parse(s); } catch (e) {} return []; }
function saveFavorites(ids) { try { localStorage.setItem('book_favorites', JSON.stringify(ids)); } catch (e) {} }

// 메인 Books 컴포넌트
function Books() {
  var [selectedTags, setSelectedTags] = useState([]);
  var [books, setBooks] = useState([]);
  var [tags, setTags] = useState([]);
  var [loading, setLoading] = useState(true);
  var [favoriteIds, setFavoriteIds] = useState(getFavorites());
  var [searchQuery, setSearchQuery] = useState('');
  var [searchResults, setSearchResults] = useState([]);
  var [isSearching, setIsSearching] = useState(false);
  var [activeTab, setActiveTab] = useState('all');
  var [selectedBook, setSelectedBook] = useState(null);
  var [cartItems, setCartItems] = useState([]);
  var [showCheckout, setShowCheckout] = useState(false);
  var [popularBooks, setPopularBooks] = useState([]);
  var [currentUserId, setCurrentUserId] = useState(null);
  var searchTimeoutRef = useRef(null);

  useEffect(function() {
    Promise.all([api.get('/books/tags'), api.get('/books'), api.get('/books/popular', { params: { limit: 5 } }), api.get('/cart'), api.get('/auth/me')]).then(function(results) {
      setTags(results[0].data);
      setBooks(results[1].data);
      setPopularBooks(results[2].data);
      setCartItems(results[3].data);
      if (results[4].data && results[4].data.user) setCurrentUserId(results[4].data.user.id);
      setLoading(false);
    }).catch(function() { setLoading(false); });
  }, []);

  function fetchBooks() {
    var params = {};
    if (selectedTags.length > 0) params.tags = selectedTags;
    api.get('/books', { params: params }).then(function(res) { setBooks(res.data); });
  }

  useEffect(function() { fetchBooks(); }, [selectedTags]);

  function toggleTag(slug) {
    var idx = selectedTags.indexOf(slug);
    if (idx >= 0) {
      var newTags = [];
      for (var i = 0; i < selectedTags.length; i++) { if (selectedTags[i] !== slug) newTags.push(selectedTags[i]); }
      setSelectedTags(newTags);
    } else {
      setSelectedTags(selectedTags.concat([slug]));
    }
  }

  function clearAllTags() { setSelectedTags([]); }

  function handleSearch(query) {
    setSearchQuery(query);
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    if (!query.trim()) { setSearchResults([]); setIsSearching(false); return; }
    setIsSearching(true);
    searchTimeoutRef.current = setTimeout(function() {
      api.get('/books/search', { params: { q: query } }).then(function(res) { setSearchResults(res.data); setIsSearching(false); });
    }, 300);
  }

  function clearSearch() { setSearchQuery(''); setSearchResults([]); setIsSearching(false); }

  function toggleFavorite(bookId) {
    var isFav = favoriteIds.indexOf(bookId) >= 0;
    var newIds;
    if (isFav) {
      newIds = [];
      for (var i = 0; i < favoriteIds.length; i++) { if (favoriteIds[i] !== bookId) newIds.push(favoriteIds[i]); }
    } else {
      newIds = favoriteIds.concat([bookId]);
    }
    setFavoriteIds(newIds);
    saveFavorites(newIds);
  }

  function isFavorite(bookId) { return favoriteIds.indexOf(bookId) >= 0; }

  function addToCart(book) {
    api.post('/cart', { book_id: book.id }).then(function(res) {
      var found = false;
      var newCart = [];
      for (var i = 0; i < cartItems.length; i++) {
        if (cartItems[i].book_id === book.id) {
          newCart.push(res.data);
          found = true;
        } else {
          newCart.push(cartItems[i]);
        }
      }
      if (!found) newCart.push(res.data);
      setCartItems(newCart);
    });
  }

  function removeFromCart(itemId) {
    api.delete('/cart/' + itemId).then(function() {
      var newCart = [];
      for (var i = 0; i < cartItems.length; i++) { if (cartItems[i].id !== itemId) newCart.push(cartItems[i]); }
      setCartItems(newCart);
    });
  }

  function handleCheckoutSuccess() { setShowCheckout(false); setCartItems([]); setActiveTab('all'); }

  var cartTotal = 0;
  for (var i = 0; i < cartItems.length; i++) { cartTotal = cartTotal + (cartItems[i].price * cartItems[i].quantity); }
  var cartCount = cartItems.length;

  function getDisplayBooks() {
    if (searchQuery) return searchResults;
    if (activeTab === 'favorites') {
      var favBooks = [];
      for (var i = 0; i < books.length; i++) { if (isFavorite(books[i].id)) favBooks.push(books[i]); }
      return favBooks;
    }
    return books;
  }

  function getSelectedTagNames() {
    var names = [];
    for (var i = 0; i < selectedTags.length; i++) {
      for (var j = 0; j < tags.length; j++) {
        if (tags[j].slug === selectedTags[i]) { names.push(tags[j].name); break; }
      }
    }
    return names;
  }

  var displayBooks = getDisplayBooks();

  return (
    <div className="books-page">
      <header className="page-header"><h1><BookOpen size={28} /> Book Recommendations</h1><p>Find books that match your mood</p></header>

      <div className="book-search-section">
        <div className="search-input-wrapper">
          <Search size={20} className="search-icon" />
          <input type="text" className="books-search-input" placeholder="Search books..." value={searchQuery} onChange={function(e) { handleSearch(e.target.value); }} />
          {searchQuery && <button className="search-clear-btn" onClick={clearSearch}><X size={18} /></button>}
        </div>
      </div>

      <div className="books-tabs">
        <button className={'books-tab ' + (activeTab === 'all' ? 'active' : '')} onClick={function() { setActiveTab('all'); setSearchQuery(''); }}><BookOpen size={18} />All Books</button>
        <button className={'books-tab ' + (activeTab === 'favorites' ? 'active' : '')} onClick={function() { setActiveTab('favorites'); setSearchQuery(''); }}><Heart size={18} />Favorites ({favoriteIds.length})</button>
        <button className={'books-tab ' + (activeTab === 'cart' ? 'active' : '')} onClick={function() { setActiveTab('cart'); setSearchQuery(''); }}><ShoppingCart size={18} />Cart ({cartCount})</button>
      </div>

      {activeTab === 'cart' ? (
        <CartView cartItems={cartItems} onRemoveItem={removeFromCart} onCheckout={function() { setShowCheckout(true); }} total={cartTotal} />
      ) : (
        <>
          {activeTab === 'all' && !searchQuery && popularBooks.length > 0 && (
            <div className="popular-books-section">
              <h3 className="popular-books-title"><Star size={20} fill="#fbbf24" color="#fbbf24" />Popular Books</h3>
              <div className="popular-books-grid">
                {popularBooks.map(function(book) {
                  return (
                    <div key={book.id} className="popular-book-card" onClick={function() { setSelectedBook(book); }}>
                      <div className="popular-book-icon"><BookOpen size={20} /></div>
                      <div className="popular-book-info"><h4 className="popular-book-title">{book.title}</h4><p className="popular-book-author">{book.author}</p><div className="popular-book-reviews"><Star size={14} fill="#fbbf24" /><span>{book.review_count} reviews</span></div></div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {activeTab === 'all' && !searchQuery && (
            <div className="tag-filter-section">
              <div className="tag-filter-header">
                <span className="tag-filter-label">Filter by Mood Tags</span>
                {selectedTags.length > 0 && <button className="clear-tags-btn" onClick={clearAllTags}>Clear All</button>}
              </div>
              <div className="tag-chips-container">
                {tags.map(function(tag) {
                  var isActive = selectedTags.indexOf(tag.slug) >= 0;
                  return <button key={tag.id} className={'tag-chip ' + (isActive ? 'active' : '')} onClick={function() { toggleTag(tag.slug); }}>{tag.name}<span className="tag-count">{tag.book_count}</span></button>;
                })}
              </div>
              {selectedTags.length > 0 && (
                <div className="selected-tags-display"><span>Selected:</span><div className="selected-tags-list">
                  {getSelectedTagNames().map(function(name, idx) { return <span key={idx} className="selected-tag-pill">{name}<X size={14} onClick={function() { toggleTag(selectedTags[idx]); }} className="remove-tag-icon" /></span>; })}
                </div></div>
              )}
            </div>
          )}

          {loading || isSearching ? <div className="loading-state">Loading books...</div> : (
            <div className="books-container">
              {displayBooks.length > 0 ? (
                <>
                  <div className="books-result-info">{searchQuery ? displayBooks.length + ' results for "' + searchQuery + '"' : activeTab === 'favorites' ? displayBooks.length + ' favorites' : 'All ' + displayBooks.length + ' books'}</div>
                  <div className="books-full-grid">
                    {displayBooks.map(function(book) { return <BookCard key={book.id} book={book} showTags={true} isFavorite={isFavorite(book.id)} onToggleFavorite={toggleFavorite} onOpenDetail={function(b) { setSelectedBook(b); }} onAddToCart={addToCart} />; })}
                  </div>
                </>
              ) : (
                <div className="empty-state"><BookOpen size={48} />{searchQuery ? <p>No books found for "{searchQuery}"</p> : activeTab === 'favorites' ? <p>No favorites yet.</p> : <p>No books found.</p>}</div>
              )}
            </div>
          )}
        </>
      )}

      {selectedBook && <BookDetailModal book={selectedBook} onClose={function() { setSelectedBook(null); }} isFavorite={isFavorite(selectedBook.id)} onToggleFavorite={toggleFavorite} onAddToCart={addToCart} currentUserId={currentUserId} />}
      {showCheckout && <CheckoutModal cartItems={cartItems} total={cartTotal} onClose={function() { setShowCheckout(false); }} onCheckoutSuccess={handleCheckoutSuccess} />}
    </div>
  );
}

export default Books;
