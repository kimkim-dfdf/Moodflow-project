import { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import { BookOpen, X, Search, Heart, Share2, Star, Trash2, User, ShoppingCart, CreditCard, Check } from 'lucide-react';

function BookCard(props) {
  var book = props.book;
  var showTags = props.showTags || false;
  var isFavorite = props.isFavorite || false;
  var onToggleFavorite = props.onToggleFavorite;
  var onOpenDetail = props.onOpenDetail;
  var onAddToCart = props.onAddToCart;
  var [imgError, setImgError] = useState(false);
  
  function handleFavoriteClick(e) {
    e.stopPropagation();
    if (onToggleFavorite) {
      onToggleFavorite(book.id);
    }
  }
  
  function handleCartClick(e) {
    e.stopPropagation();
    if (onAddToCart) {
      onAddToCart(book);
    }
  }
  
  function handleCardClick() {
    if (onOpenDetail) {
      onOpenDetail(book);
    }
  }
  
  function handleImgError() {
    setImgError(true);
  }
  
  return (
    <div className="book-card" onClick={handleCardClick}>
      <div className="book-cover">
        {imgError ? (
          <div className="book-icon"><BookOpen size={24} /></div>
        ) : (
          <img 
            src={'/books/' + book.id + '.jpg'} 
            alt={book.title}
            onError={handleImgError}
            className="book-cover-img"
          />
        )}
      </div>
      <div className="book-info">
        <div className="book-title-row">
          <h4 className="book-title">{book.title}</h4>
          <button 
            className={'favorite-btn ' + (isFavorite ? 'active' : '')} 
            onClick={handleFavoriteClick}
            title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            <Heart size={18} fill={isFavorite ? '#ef4444' : 'none'} />
          </button>
        </div>
        <p className="book-author">{book.author}</p>
        <span className="book-genre">{book.genre}</span>
        <div className="book-price-row">
          <span className="book-price">${book.price.toFixed(2)}</span>
          <button className="add-to-cart-btn" onClick={handleCartClick} title="Add to Cart">
            <ShoppingCart size={16} />
          </button>
        </div>
        {showTags && book.tags && book.tags.length > 0 && (
          <div className="book-tags">
            {book.tags.map(function(tag) {
              return <span key={tag.id} className="book-tag-pill">{tag.name}</span>;
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function BookDetailModal(props) {
  var book = props.book;
  var onClose = props.onClose;
  var isFavorite = props.isFavorite;
  var onToggleFavorite = props.onToggleFavorite;
  var onAddToCart = props.onAddToCart;
  var currentUserId = props.currentUserId;
  var [shareMessage, setShareMessage] = useState('');
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
      loadReviews();
    }
  }, [book]);
  
  function loadReviews() {
    api.get('/books/' + book.id + '/reviews').then(function(res) {
      setReviews(res.data);
      var userHasReview = false;
      for (var i = 0; i < res.data.length; i++) {
        if (Number(res.data[i].user_id) === Number(currentUserId)) {
          userHasReview = true;
          break;
        }
      }
      setHasUserReview(userHasReview);
    }).catch(function() {
      setReviews([]);
    });
  }
  
  if (!book) {
    return null;
  }
  
  function handleOverlayClick(e) {
    if (e.target.className === 'modal-overlay') {
      onClose();
    }
  }
  
  function handleFavoriteClick() {
    if (onToggleFavorite) {
      onToggleFavorite(book.id);
    }
  }
  
  function handleAddToCart() {
    if (onAddToCart) {
      onAddToCart(book);
      setAddedToCart(true);
      setTimeout(function() {
        setAddedToCart(false);
      }, 2000);
    }
  }
  
  function handleShareClick() {
    var shareText = 'Check out this book I found on MoodFlow!\n\n';
    shareText = shareText + book.title + ' by ' + book.author + '\n';
    shareText = shareText + 'Genre: ' + book.genre + '\n';
    if (book.description) {
      shareText = shareText + '\n' + book.description;
    }
    
    if (navigator.share) {
      navigator.share({
        title: book.title,
        text: shareText
      }).catch(function(error) {
        console.log('Share cancelled');
      });
    } else {
      navigator.clipboard.writeText(shareText).then(function() {
        setShareMessage('Copied to clipboard!');
        setTimeout(function() {
          setShareMessage('');
        }, 2000);
      }).catch(function() {
        setShareMessage('Failed to copy');
        setTimeout(function() {
          setShareMessage('');
        }, 2000);
      });
    }
  }
  
  function handleSubmitReview() {
    if (!reviewContent.trim()) {
      setReviewError('Please write a review');
      return;
    }
    
    setIsSubmitting(true);
    setReviewError('');
    
    api.post('/books/' + book.id + '/reviews', {
      rating: reviewRating,
      content: reviewContent
    }).then(function(res) {
      setReviews([res.data].concat(reviews));
      setReviewContent('');
      setReviewRating(5);
      setHasUserReview(true);
      setIsSubmitting(false);
    }).catch(function(err) {
      var message = 'Failed to submit review';
      if (err.response && err.response.data && err.response.data.error) {
        message = err.response.data.error;
      }
      setReviewError(message);
      setIsSubmitting(false);
    });
  }
  
  function handleDeleteReview(reviewId) {
    api.delete('/books/reviews/' + reviewId).then(function() {
      var newReviews = [];
      for (var i = 0; i < reviews.length; i++) {
        if (reviews[i].id !== reviewId) {
          newReviews.push(reviews[i]);
        }
      }
      setReviews(newReviews);
      setHasUserReview(false);
    }).catch(function() {
      setReviewError('Failed to delete review');
    });
  }
  
  function createStarClickHandler(starValue) {
    return function() {
      setReviewRating(starValue);
    };
  }
  
  function renderStars(rating, interactive) {
    var stars = [];
    for (var i = 1; i <= 5; i++) {
      if (interactive) {
        stars.push(
          <button 
            key={i} 
            type="button"
            className="star-btn"
            onClick={createStarClickHandler(i)}
          >
            <Star size={20} fill={i <= reviewRating ? '#fbbf24' : 'none'} color={i <= reviewRating ? '#fbbf24' : '#d1d5db'} />
          </button>
        );
      } else {
        stars.push(
          <Star key={i} size={16} fill={i <= rating ? '#fbbf24' : 'none'} color={i <= rating ? '#fbbf24' : '#d1d5db'} />
        );
      }
    }
    return stars;
  }
  
  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="book-detail-modal">
        <button className="modal-close-btn" onClick={onClose}>
          <X size={24} />
        </button>
        
        <div className="modal-header">
          <div className="modal-book-cover">
            {modalImgError ? (
              <div className="modal-book-icon"><BookOpen size={48} /></div>
            ) : (
              <img 
                src={'/books/' + book.id + '.jpg'} 
                alt={book.title}
                onError={function() { setModalImgError(true); }}
                className="modal-cover-img"
              />
            )}
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
            {book.emotion && (
              <span className="modal-emotion">Recommended for: {book.emotion}</span>
            )}
          </div>
          
          <div className="modal-reviews">
            <h4>Reviews ({reviews.length})</h4>
            
            {!hasUserReview && (
              <div className="review-form">
                <div className="review-rating-input">
                  <span>Your Rating:</span>
                  <div className="stars-input">{renderStars(reviewRating, true)}</div>
                </div>
                <textarea
                  className="review-textarea"
                  placeholder="Write your review..."
                  value={reviewContent}
                  onChange={function(e) { setReviewContent(e.target.value); }}
                  rows={3}
                />
                {reviewError && <div className="review-error">{reviewError}</div>}
                <button 
                  className="review-submit-btn"
                  onClick={handleSubmitReview}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Review'}
                </button>
              </div>
            )}
            
            {hasUserReview && (
              <div className="review-notice">You have already reviewed this book.</div>
            )}
            
            <div className="reviews-list">
              {reviews.length === 0 ? (
                <p className="no-reviews">No reviews yet. Be the first to review!</p>
              ) : (
                reviews.map(function(review) {
                  return (
                    <div key={review.id} className="review-item">
                      <div className="review-header">
                        <div className="review-user">
                          <User size={16} />
                          <span>{review.username}</span>
                        </div>
                        <div className="review-stars">{renderStars(review.rating, false)}</div>
                        {Number(review.user_id) === Number(currentUserId) && (
                          <button 
                            className="review-delete-btn"
                            onClick={function() { handleDeleteReview(review.id); }}
                            title="Delete review"
                          >
                            <Trash2 size={16} />
                          </button>
                        )}
                      </div>
                      <p className="review-content">{review.content}</p>
                      <span className="review-date">
                        {new Date(review.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>
          
          {book.description && (
            <div className="modal-description">
              <h4>Description</h4>
              <p>{book.description}</p>
            </div>
          )}
          
          {book.tags && book.tags.length > 0 && (
            <div className="modal-tags">
              <h4>Mood Tags</h4>
              <div className="modal-tags-list">
                {book.tags.map(function(tag) {
                  return (
                    <span 
                      key={tag.id} 
                      className="modal-tag-pill"
                      style={{ backgroundColor: tag.color || '#6B7280' }}
                    >
                      {tag.name}
                    </span>
                  );
                })}
              </div>
            </div>
          )}
        </div>
        
        <div className="modal-footer">
          <button 
            className={'modal-favorite-btn ' + (isFavorite ? 'active' : '')}
            onClick={handleFavoriteClick}
          >
            <Heart size={20} fill={isFavorite ? '#ef4444' : 'none'} />
            {isFavorite ? 'Remove from Favorites' : 'Add to Favorites'}
          </button>
          <button 
            className={'modal-cart-btn ' + (addedToCart ? 'added' : '')}
            onClick={handleAddToCart}
          >
            {addedToCart ? (
              <>
                <Check size={20} />
                Added to Cart!
              </>
            ) : (
              <>
                <ShoppingCart size={20} />
                Add to Cart - ${book.price.toFixed(2)}
              </>
            )}
          </button>
          <button 
            className="modal-share-btn"
            onClick={handleShareClick}
          >
            <Share2 size={20} />
            Share
          </button>
        </div>
        {shareMessage && (
          <div className="share-message">{shareMessage}</div>
        )}
      </div>
    </div>
  );
}

function CheckoutModal(props) {
  var onClose = props.onClose;
  var cartItems = props.cartItems;
  var total = props.total;
  var onCheckoutSuccess = props.onCheckoutSuccess;
  
  var [cardNumber, setCardNumber] = useState('');
  var [cardName, setCardName] = useState('');
  var [expiry, setExpiry] = useState('');
  var [cvv, setCvv] = useState('');
  var [isProcessing, setIsProcessing] = useState(false);
  var [error, setError] = useState('');
  var [success, setSuccess] = useState(false);
  
  function handleOverlayClick(e) {
    if (e.target.className === 'modal-overlay') {
      onClose();
    }
  }
  
  function formatCardNumber(value) {
    var cleaned = value.replace(/\D/g, '');
    var formatted = '';
    for (var i = 0; i < cleaned.length && i < 16; i++) {
      if (i > 0 && i % 4 === 0) {
        formatted = formatted + ' ';
      }
      formatted = formatted + cleaned[i];
    }
    return formatted;
  }
  
  function formatExpiry(value) {
    var cleaned = value.replace(/\D/g, '');
    if (cleaned.length >= 2) {
      return cleaned.substring(0, 2) + '/' + cleaned.substring(2, 4);
    }
    return cleaned;
  }
  
  function handleCardNumberChange(e) {
    setCardNumber(formatCardNumber(e.target.value));
  }
  
  function handleExpiryChange(e) {
    setExpiry(formatExpiry(e.target.value));
  }
  
  function handleCvvChange(e) {
    var cleaned = e.target.value.replace(/\D/g, '');
    if (cleaned.length <= 4) {
      setCvv(cleaned);
    }
  }
  
  function handleSubmit(e) {
    e.preventDefault();
    setError('');
    
    var cleanCardNumber = cardNumber.replace(/\s/g, '');
    if (cleanCardNumber.length < 13) {
      setError('Please enter a valid card number');
      return;
    }
    if (!cardName.trim()) {
      setError('Please enter the cardholder name');
      return;
    }
    if (expiry.length < 5) {
      setError('Please enter a valid expiry date');
      return;
    }
    if (cvv.length < 3) {
      setError('Please enter a valid CVV');
      return;
    }
    
    setIsProcessing(true);
    
    api.post('/checkout', {
      card_number: cleanCardNumber,
      card_name: cardName,
      expiry: expiry,
      cvv: cvv
    }).then(function(res) {
      setIsProcessing(false);
      setSuccess(true);
      setTimeout(function() {
        onCheckoutSuccess();
      }, 2000);
    }).catch(function(err) {
      setIsProcessing(false);
      var message = 'Checkout failed. Please try again.';
      if (err.response && err.response.data && err.response.data.error) {
        message = err.response.data.error;
      }
      setError(message);
    });
  }
  
  if (success) {
    return (
      <div className="modal-overlay" onClick={handleOverlayClick}>
        <div className="checkout-modal success-modal">
          <div className="success-content">
            <div className="success-icon">
              <Check size={48} />
            </div>
            <h2>Purchase Complete!</h2>
            <p>Thank you for your order.</p>
            <p className="success-total">Total: ${total.toFixed(2)}</p>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="checkout-modal">
        <button className="modal-close-btn" onClick={onClose}>
          <X size={24} />
        </button>
        
        <div className="checkout-header">
          <CreditCard size={28} />
          <h2>Checkout</h2>
        </div>
        
        <div className="checkout-summary">
          <h3>Order Summary</h3>
          <div className="checkout-items">
            {cartItems.map(function(item) {
              return (
                <div key={item.id} className="checkout-item">
                  <span className="checkout-item-title">{item.title}</span>
                  <span className="checkout-item-qty">x{item.quantity}</span>
                  <span className="checkout-item-price">${(item.price * item.quantity).toFixed(2)}</span>
                </div>
              );
            })}
          </div>
          <div className="checkout-total">
            <span>Total</span>
            <span>${total.toFixed(2)}</span>
          </div>
        </div>
        
        <form className="checkout-form" onSubmit={handleSubmit}>
          <h3>Payment Details</h3>
          <p className="checkout-note">This is a simulated payment for demo purposes.</p>
          
          <div className="form-group">
            <label>Card Number</label>
            <input
              type="text"
              placeholder="1234 5678 9012 3456"
              value={cardNumber}
              onChange={handleCardNumberChange}
              className="card-input"
            />
          </div>
          
          <div className="form-group">
            <label>Cardholder Name</label>
            <input
              type="text"
              placeholder="John Doe"
              value={cardName}
              onChange={function(e) { setCardName(e.target.value); }}
              className="card-input"
            />
          </div>
          
          <div className="form-row">
            <div className="form-group half">
              <label>Expiry Date</label>
              <input
                type="text"
                placeholder="MM/YY"
                value={expiry}
                onChange={handleExpiryChange}
                className="card-input"
              />
            </div>
            <div className="form-group half">
              <label>CVV</label>
              <input
                type="text"
                placeholder="123"
                value={cvv}
                onChange={handleCvvChange}
                className="card-input"
              />
            </div>
          </div>
          
          {error && <div className="checkout-error">{error}</div>}
          
          <button 
            type="submit" 
            className="checkout-submit-btn"
            disabled={isProcessing}
          >
            {isProcessing ? 'Processing...' : 'Pay $' + total.toFixed(2)}
          </button>
        </form>
      </div>
    </div>
  );
}

function CartView(props) {
  var cartItems = props.cartItems;
  var onRemoveItem = props.onRemoveItem;
  var onCheckout = props.onCheckout;
  var total = props.total;
  
  if (cartItems.length === 0) {
    return (
      <div className="empty-state">
        <ShoppingCart size={48} />
        <p>Your cart is empty</p>
        <p className="empty-hint">Add books to your cart to purchase them</p>
      </div>
    );
  }
  
  return (
    <div className="cart-view">
      <div className="cart-items">
        {cartItems.map(function(item) {
          return (
            <div key={item.id} className="cart-item">
              <div className="cart-item-info">
                <h4 className="cart-item-title">{item.title}</h4>
                <p className="cart-item-author">{item.author}</p>
                <p className="cart-item-qty">Quantity: {item.quantity}</p>
              </div>
              <div className="cart-item-right">
                <span className="cart-item-price">${(item.price * item.quantity).toFixed(2)}</span>
                <button 
                  className="cart-remove-btn"
                  onClick={function() { onRemoveItem(item.id); }}
                  title="Remove from cart"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="cart-summary">
        <div className="cart-total-row">
          <span>Total ({cartItems.length} items)</span>
          <span className="cart-total-amount">${total.toFixed(2)}</span>
        </div>
        <button className="checkout-btn" onClick={onCheckout}>
          <CreditCard size={20} />
          Proceed to Checkout
        </button>
      </div>
    </div>
  );
}

function getFavoritesFromStorage() {
  try {
    var stored = localStorage.getItem('book_favorites');
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
  }
  return [];
}

function saveFavoritesToStorage(favoriteIds) {
  try {
    localStorage.setItem('book_favorites', JSON.stringify(favoriteIds));
  } catch (e) {
  }
}

function Books() {
  const [selectedTags, setSelectedTags] = useState([]);
  const [books, setBooks] = useState([]);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [favoriteIds, setFavoriteIds] = useState(getFavoritesFromStorage());
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [allBooks, setAllBooks] = useState([]);
  const [selectedBook, setSelectedBook] = useState(null);
  const [currentUserId, setCurrentUserId] = useState(null);
  const [popularBooks, setPopularBooks] = useState([]);
  const [cartItems, setCartItems] = useState([]);
  const [showCheckout, setShowCheckout] = useState(false);
  const [cartMessage, setCartMessage] = useState('');
  const fetchIdRef = useRef(0);
  const searchTimeoutRef = useRef(null);

  useEffect(function() {
    api.get('/books/tags').then(function(res) {
      setTags(res.data);
    });
    api.get('/books').then(function(res) {
      setAllBooks(res.data);
    });
    api.get('/books/popular?limit=5').then(function(res) {
      setPopularBooks(res.data);
    }).catch(function() {
      setPopularBooks([]);
    });
    api.get('/auth/me').then(function(res) {
      setCurrentUserId(res.data.id);
    }).catch(function() {
      setCurrentUserId(null);
    });
    loadCart();
    fetchBooks([]);
  }, []);

  function loadCart() {
    api.get('/cart').then(function(res) {
      setCartItems(res.data);
    }).catch(function() {
      setCartItems([]);
    });
  }

  function addToCart(book) {
    api.post('/cart', { book_id: book.id }).then(function(res) {
      loadCart();
      setCartMessage('Added to cart!');
      setTimeout(function() {
        setCartMessage('');
      }, 2000);
    }).catch(function(err) {
      console.error('Failed to add to cart:', err);
    });
  }

  function removeFromCart(itemId) {
    api.delete('/cart/' + itemId).then(function() {
      loadCart();
    }).catch(function(err) {
      console.error('Failed to remove from cart:', err);
    });
  }

  function getCartTotal() {
    var total = 0;
    for (var i = 0; i < cartItems.length; i++) {
      var price = cartItems[i].price;
      var qty = cartItems[i].quantity || 1;
      total = total + (price * qty);
    }
    return total;
  }

  function handleCheckout() {
    setShowCheckout(true);
  }

  function handleCheckoutSuccess() {
    setShowCheckout(false);
    setCartItems([]);
    setActiveTab('all');
  }

  function fetchBooks(tagList) {
    var fetchId = ++fetchIdRef.current;
    setLoading(true);
    
    var url = '/books';
    if (tagList.length > 0) {
      var params = [];
      for (var i = 0; i < tagList.length; i++) {
        params.push('tags=' + tagList[i]);
      }
      url = '/books?' + params.join('&');
    }
    
    api.get(url).then(function(res) {
      if (fetchId === fetchIdRef.current) {
        setBooks(res.data);
        setLoading(false);
      }
    }).catch(function() {
      if (fetchId === fetchIdRef.current) {
        setLoading(false);
      }
    });
  }

  function handleSearch(query) {
    setSearchQuery(query);
    
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    if (!query.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }
    
    setIsSearching(true);
    
    searchTimeoutRef.current = setTimeout(function() {
      api.get('/books/search?q=' + encodeURIComponent(query)).then(function(res) {
        setSearchResults(res.data);
        setIsSearching(false);
      }).catch(function() {
        setSearchResults([]);
        setIsSearching(false);
      });
    }, 300);
  }

  function clearSearch() {
    setSearchQuery('');
    setSearchResults([]);
    setIsSearching(false);
  }

  function toggleTag(slug) {
    var newTags;
    if (selectedTags.indexOf(slug) >= 0) {
      newTags = selectedTags.filter(function(t) { return t !== slug; });
    } else {
      newTags = selectedTags.concat([slug]);
    }
    setSelectedTags(newTags);
    fetchBooks(newTags);
  }

  function clearAllTags() {
    setSelectedTags([]);
    fetchBooks([]);
  }

  function getSelectedTagNames() {
    var names = [];
    for (var i = 0; i < selectedTags.length; i++) {
      var slug = selectedTags[i];
      for (var j = 0; j < tags.length; j++) {
        if (tags[j].slug === slug) {
          names.push(tags[j].name);
          break;
        }
      }
    }
    return names;
  }

  function toggleFavorite(bookId) {
    var isFav = favoriteIds.indexOf(bookId) >= 0;
    var newIds;
    
    if (isFav) {
      newIds = favoriteIds.filter(function(id) { return id !== bookId; });
    } else {
      newIds = favoriteIds.concat([bookId]);
    }
    
    setFavoriteIds(newIds);
    saveFavoritesToStorage(newIds);
  }

  function isFavorite(bookId) {
    return favoriteIds.indexOf(bookId) >= 0;
  }

  function handleTabChange(tab) {
    setActiveTab(tab);
    setSearchQuery('');
    setSearchResults([]);
    
    if (tab === 'all') {
      fetchBooks(selectedTags);
    }
  }

  function openBookDetail(book) {
    setSelectedBook(book);
  }

  function closeBookDetail() {
    setSelectedBook(null);
  }

  function getFavoriteBooks() {
    var result = [];
    for (var i = 0; i < allBooks.length; i++) {
      var book = allBooks[i];
      if (favoriteIds.indexOf(book.id) >= 0) {
        result.push(book);
      }
    }
    return result;
  }

  function getDisplayBooks() {
    if (searchQuery.trim()) {
      return searchResults;
    }
    if (activeTab === 'favorites') {
      return getFavoriteBooks();
    }
    return books;
  }

  var displayBooks = getDisplayBooks();
  var cartTotal = getCartTotal();
  var cartCount = 0;
  for (var i = 0; i < cartItems.length; i++) {
    cartCount = cartCount + (cartItems[i].quantity || 1);
  }

  return (
    <div className="books-page">
      <header className="page-header">
        <h1><BookOpen size={28} /> Book Recommendations</h1>
        <p>Discover books that match your current mood</p>
      </header>

      {cartMessage && (
        <div className="cart-message">{cartMessage}</div>
      )}

      <div className="books-search-section">
        <div className="search-input-wrapper">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            className="books-search-input"
            placeholder="Search by title or author..."
            value={searchQuery}
            onChange={function(e) { handleSearch(e.target.value); }}
          />
          {searchQuery && (
            <button className="search-clear-btn" onClick={clearSearch}>
              <X size={18} />
            </button>
          )}
        </div>
      </div>

      <div className="books-tabs">
        <button 
          className={'books-tab ' + (activeTab === 'all' ? 'active' : '')}
          onClick={function() { handleTabChange('all'); }}
        >
          <BookOpen size={18} />
          All Books
        </button>
        <button 
          className={'books-tab ' + (activeTab === 'favorites' ? 'active' : '')}
          onClick={function() { handleTabChange('favorites'); }}
        >
          <Heart size={18} />
          Favorites ({favoriteIds.length})
        </button>
        <button 
          className={'books-tab ' + (activeTab === 'cart' ? 'active' : '')}
          onClick={function() { handleTabChange('cart'); }}
        >
          <ShoppingCart size={18} />
          Cart ({cartCount})
        </button>
      </div>

      {activeTab === 'cart' ? (
        <CartView 
          cartItems={cartItems}
          onRemoveItem={removeFromCart}
          onCheckout={handleCheckout}
          total={cartTotal}
        />
      ) : (
        <>
          {activeTab === 'all' && !searchQuery && popularBooks.length > 0 && (
            <div className="popular-books-section">
              <h3 className="popular-books-title">
                <Star size={20} fill="#fbbf24" color="#fbbf24" />
                Popular Books
              </h3>
              <p className="popular-books-subtitle">Most reviewed by our community</p>
              <div className="popular-books-grid">
                {popularBooks.map(function(book) {
                  return (
                    <div key={book.id} className="popular-book-card" onClick={function() { openBookDetail(book); }}>
                      <div className="popular-book-icon"><BookOpen size={20} /></div>
                      <div className="popular-book-info">
                        <h4 className="popular-book-title">{book.title}</h4>
                        <p className="popular-book-author">{book.author}</p>
                        <div className="popular-book-reviews">
                          <Star size={14} fill="#fbbf24" color="#fbbf24" />
                          <span>{book.review_count} reviews</span>
                        </div>
                      </div>
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
                {selectedTags.length > 0 && (
                  <button className="clear-tags-btn" onClick={clearAllTags}>Clear All</button>
                )}
              </div>
              
              <div className="tag-chips-container">
                {tags.map(function(tag) {
                  var isActive = selectedTags.indexOf(tag.slug) >= 0;
                  return (
                    <button key={tag.id} className={'tag-chip ' + (isActive ? 'active' : '')} onClick={function() { toggleTag(tag.slug); }}>
                      {tag.name}
                      <span className="tag-count">{tag.book_count}</span>
                    </button>
                  );
                })}
              </div>

              {selectedTags.length > 0 && (
                <div className="selected-tags-display">
                  <span>Selected:</span>
                  <div className="selected-tags-list">
                    {getSelectedTagNames().map(function(name, idx) {
                      return (
                        <span key={idx} className="selected-tag-pill">
                          {name}
                          <X size={14} onClick={function() { toggleTag(selectedTags[idx]); }} className="remove-tag-icon" />
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {loading || isSearching ? (
            <div className="loading-state">Loading books...</div>
          ) : (
            <div className="books-container">
              {displayBooks.length > 0 ? (
                <>
                  <div className="books-result-info">
                    {searchQuery ? (
                      displayBooks.length + ' search results for "' + searchQuery + '"'
                    ) : activeTab === 'favorites' ? (
                      displayBooks.length + ' favorite books'
                    ) : selectedTags.length > 0 ? (
                      displayBooks.length + ' books found'
                    ) : (
                      'All ' + displayBooks.length + ' books'
                    )}
                  </div>
                  <div className="books-full-grid">
                    {displayBooks.map(function(book) {
                      return (
                        <BookCard 
                          key={book.id} 
                          book={book} 
                          showTags={true}
                          isFavorite={isFavorite(book.id)}
                          onToggleFavorite={toggleFavorite}
                          onOpenDetail={openBookDetail}
                          onAddToCart={addToCart}
                        />
                      );
                    })}
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <BookOpen size={48} />
                  {searchQuery ? (
                    <p>No books found for "{searchQuery}"</p>
                  ) : activeTab === 'favorites' ? (
                    <p>No favorite books yet. Click the heart icon to add books to your favorites!</p>
                  ) : (
                    <p>No books found for selected tags.</p>
                  )}
                </div>
              )}
            </div>
          )}
        </>
      )}

      {selectedBook && (
        <BookDetailModal
          book={selectedBook}
          onClose={closeBookDetail}
          isFavorite={isFavorite(selectedBook.id)}
          onToggleFavorite={toggleFavorite}
          onAddToCart={addToCart}
          currentUserId={currentUserId}
        />
      )}

      {showCheckout && (
        <CheckoutModal
          cartItems={cartItems}
          total={cartTotal}
          onClose={function() { setShowCheckout(false); }}
          onCheckoutSuccess={handleCheckoutSuccess}
        />
      )}
    </div>
  );
}

export default Books;
