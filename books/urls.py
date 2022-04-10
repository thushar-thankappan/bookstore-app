from django.urls import path
from books import views
# from django.conf.urls import url

urlpatterns = [
    path('', views.index, name='index'),
    # path('books/', views.books, name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book_detail'),
    # path('books/book_filter', views.book_filter, name='book_filter'),
    path('books/make_request', views.make_request, name='make_request'),
    path('books/request_history', views.request_history, name='request_history'),
    path('books/cancel_request', views.cancel_request, name='cancel_request'),
    path('books/return_book', views.return_book, name='return_book'),
    # path('books/manage_books', views.manage_books, name='manage_books'),
    path('user/create/', views.UserCreate.as_view(), name='create_user'),
    path('book/add/', views.BookCreate.as_view(), name='add_book'),
    path('books/add_quantity/<int:pk>', views.add_quantity, name='add_quantity'),
    path('books/lend_book/<int:pk>', views.lend_book, name='lend_book'),
    path('books/manage_requests', views.manage_requests, name='manage_requests'),
    path('books/manage_requests_return', views.manage_requests_return, name='manage_requests_return'),
    path('books/manage_requests_lent', views.manage_requests_lent, name='manage_requests_lent'),
    path('books/manage_requests_rejected', views.manage_requests_rejected, name='manage_requests_rejected'),
    path('books/manage_requests_close', views.manage_requests_close, name='manage_requests_close'),
    path('books/confirm_lend_request', views.confirm_lend_request, name='confirm_lend_request'),
    path('books/reject_lend_request', views.reject_lend_request, name='reject_lend_request'),
    path('books/close_request', views.close_request, name='close_request'),
]
