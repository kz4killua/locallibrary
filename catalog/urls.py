from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.index, name='index'),
    path('books', views.AllBooks.as_view(), name='all-books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors', views.AllAuthors.as_view(), name='all-authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('search/authors', views.AuthorSearchView.as_view(), name='author-search'),
    path('search/books', views.BookSearchView.as_view(), name='book-search'),
    path('cart', views.CartView.as_view(), name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('borrowed', views.borrowed, name='borrowed'),
    
    path('review/<int:pk>', views.review, name='review'),

    path('book/create/', views.BookCreateView.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    path('author/create/', views.AuthorCreateView.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdateView.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDeleteView.as_view(), name='author-delete'),

    path('copies/<int:pk>', views.BookCopyListView.as_view(), name='book-copies'),

    path('bookcopy/create/', views.BookCopyCreateView.as_view(), name='bookcopy-create'),
    path('bookcopy/<int:pk>/update/', views.BookCopyUpdateView.as_view(), name='bookcopy-update'),
    path('bookcopy/<int:pk>/delete/', views.BookCopyDeleteView.as_view(), name='bookcopy-delete'),

    path('loan/<int:pk>/update', views.LoanUpdateView.as_view(), name='loan-update'),
    path('loan/<int:pk>/delete', views.LoanDeleteView.as_view(), name='loan-delete'),

    path('loans/active', views.ActiveLoanListView.as_view(), name='active-loans'),

    path('cart/toggle/<int:pk>', views.toggle_cart, name='toggle-cart'),
    path('api/search/author', views.author_search_api, name='api-author-search'),
    path('api/search/book', views.book_search_api, name='api-book-search'),
]