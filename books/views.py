from django.shortcuts import render
from .models import Book, Category, Author, BookLendDetail, User
from django.views import generic
from . import forms
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.db.models import Q

class BookDetailView(generic.DetailView):
    model = Book

class UserCreate(CreateView):
    model = User
    fields = ['first_name', 'last_name', 'username', 'password', 'email']
    success_url = reverse_lazy('manage_books')

class BookCreate(CreateView):
    model = Book
    fields = ['title', 'isbn', 'description', 'price', 'total_quantity', 'author', 'category']

def index(request):
    context = []
    search_key = str(request.GET.get('search_key', "")).strip()
    filter_key = str(request.GET.get('filter_key', "")).strip()
    
    if filter_key == 'firstname':
        context = Book.objects.filter(author__firstname__contains = search_key)
    elif filter_key == 'lastname':
        context = Book.objects.filter(author__lastname__contains = search_key)
    elif filter_key == 'title':
        context = Book.objects.filter(title__contains = search_key)
    elif filter_key == 'isbn':
        context = Book.objects.filter(isbn = search_key)
    elif filter_key == 'status_a':
        context = Book.objects.filter(status = 'a', title__contains = search_key)
    elif filter_key == 'status_l':
        context = Book.objects.filter(status = 'l', title__contains = search_key)
    else:
        context = Book.objects.filter(Q(title__contains = search_key) | Q(author__firstname__contains = search_key) | Q(author__lastname__contains = search_key))

    paginator = Paginator(context, 10)
    page = request.GET.get('page')

    try:
        context = paginator.page(page)
    except PageNotAnInteger:
        context = paginator.page(1)
    except EmptyPage:
        context = paginator.page(paginator.num_pages)

    filter_list = [
        {'value': 'all', 'name': 'Search By'},
        {'value': 'firstname', 'name': 'Author Firstname'},
        {'value': 'lastname', 'name': 'Author Lastname'},
        {'value': 'title', 'name': 'Book Title'},
        {'value': 'isbn', 'name': 'ISBN'},
        {'value': 'status_a', 'name': 'Books Available'},
        {'value': 'status_l', 'name': 'Books Lent'}
    ]

    book_ids = []

    if request.user.is_authenticated:
        request_history = BookLendDetail.objects.filter(reader = request.user)
        for data in request_history:
            if data.status in ['p', 'l', 'r']:
                book_ids.append(data.book.id)

    return render(request, 'index.html', {'context' : context, 'filter_list': filter_list, 'book_ids': book_ids})

@login_required
def make_request(request):
    book_id = request.GET.get('book_id')

    book_detail = Book.objects.get(id = book_id)
    data = BookLendDetail(book = book_detail, reader = request.user, request_date = date.today(), charge = 0)
    data.save()

    # messages.add_message(request, messages.INFO, 'Your request for the book (' + book_detail.title + ') has been submitted.')
    
    return render(request, 'make_request.html', {})


@login_required
def request_history(request):
    req_pending = BookLendDetail.objects.filter(reader = request.user, status = 'p').order_by("-request_date")
    req_close =  BookLendDetail.objects.filter(reader = request.user, status = 'c').order_by("-close_date")
    req_lending =  BookLendDetail.objects.filter(reader = request.user, status = 'l').order_by("-lent_date")
    req_return = BookLendDetail.objects.filter(reader = request.user, status = 'r').order_by("-return_date")
    req_rejected = BookLendDetail.objects.filter(reader = request.user, status = 'n').order_by("-request_date")
    context = {
        'p': req_pending,
        'c': req_close,
        'l': req_lending,
        'r': req_return,
        'n': req_rejected
    }
    return render(request, 'request_history.html', {'context' : context})

@login_required
def cancel_request(request):
    request_id = request.GET.get('request_id')

    BookLendDetail.objects.filter(id=request_id).delete()

    return render(request, 'request_history.html')

@login_required
def return_book(request):
    request_id = request.GET.get('request_id')

    request_data = BookLendDetail.objects.get(id=request_id)
    charge_day = 20
    today_date = date.today()
    day = today_date - request_data.lent_date
    charge = (day.days + 1) * charge_day
    
    request_data.return_date = today_date
    request_data.status = 'r'
    request_data.charge = charge
    request_data.save()

    return render(request, 'request_history.html')

@login_required
def add_quantity(request, pk):

    book_data = Book.objects.get(id = pk)
    message = ""
    if request.method == "POST":
        if request.POST.get('quantity'):
            book_data.total_quantity = int(book_data.total_quantity) + int(request.POST.get('quantity'))
            book_data.save()
            if int(request.POST.get('quantity')) == 1:
                c = "copy"
                h = "has"
            else:
                c = "copies"
                h = "have"
            message = request.POST.get('quantity') + " " + c + " of the book (" + book_data.title + ") " + h + " been added."
            messages.add_message(request, messages.INFO, message)
            return redirect('/library/')

    return render(request, 'add_quantity.html', { 'book' : book_data } )

@login_required
def lend_book(request, pk):
    book_data = Book.objects.get(id = pk)
    readers = User.objects.filter(groups__name = 'Readers')

    if request.method == "POST":
        reader_id = request.POST.get('reader')
        reader = User.objects.get(id=reader_id)
        req = BookLendDetail(book = book_data, reader = reader, lent_date = date.today(), status = 'l', charge = 0)
        req.save()
        if book_data.quantity == 1:
            book_data.status = 'l'
        book_data.quantity = book_data.quantity - 1
        book_data.save()
        message = "The book (" + book_data.title + ") has been lent to the reader (" + reader.username + ")."
        messages.add_message(request, messages.INFO, message)
        return redirect('/library/')

    return render(request, 'lend_book.html', { 'book' : book_data, 'readers' : readers })

def manage_requests_count():
    p = BookLendDetail.objects.filter(status = 'p').order_by("-request_date")
    r = BookLendDetail.objects.filter(status = 'r').order_by("-return_date")
    l = BookLendDetail.objects.filter(status = 'l').order_by("-lent_date")
    c = BookLendDetail.objects.filter(status = 'c').order_by("-close_date")
    n = BookLendDetail.objects.filter(status = 'n').order_by("-close_date")

    context = {
        'p' : p.count,
        'r' : r.count,
        'l' : l.count,
        'c' : c.count,
        'n' : n.count
    }
    return context

@login_required
def manage_requests(request):

    lend_request_data = BookLendDetail.objects.filter(status = 'p').order_by("-request_date")
    context = manage_requests_count()

    paginator = Paginator(lend_request_data, 10)
    page = request.GET.get('page')

    try:
        lend_request_data = paginator.page(page)
    except PageNotAnInteger:
        lend_request_data = paginator.page(1)
    except EmptyPage:
        lend_request_data = paginator.page(paginator.num_pages)

    return render(request, 'manage_requests.html', {'lend_request' : lend_request_data, 'context': context})

@login_required
def manage_requests_return(request):

    return_request_data = BookLendDetail.objects.filter(status = 'r').order_by("-return_date")
    context = manage_requests_count()

    paginator = Paginator(return_request_data, 10)
    page = request.GET.get('page')

    try:
        return_request_data = paginator.page(page)
    except PageNotAnInteger:
        return_request_data = paginator.page(1)
    except EmptyPage:
        return_request_data = paginator.page(paginator.num_pages)

    return render(request, 'manage_requests_return.html', {'return_request' : return_request_data, 'context': context})

@login_required
def manage_requests_lent(request):
    lent_request_data = BookLendDetail.objects.filter(status = 'l').order_by("-lent_date")
    context = manage_requests_count()

    paginator = Paginator(lent_request_data, 10)
    page = request.GET.get('page')

    try:
        lent_request_data = paginator.page(page)
    except PageNotAnInteger:
        lent_request_data = paginator.page(1)
    except EmptyPage:
        lent_request_data = paginator.page(paginator.num_pages)

    return render(request, 'manage_requests_lent.html', {'lent_request' : lent_request_data, 'context': context})

@login_required
def manage_requests_rejected(request):
    rejected_request_data = BookLendDetail.objects.filter(status = 'n').order_by("-close_date")
    context = manage_requests_count()

    paginator = Paginator(rejected_request_data, 10)
    page = request.GET.get('page')

    try:
        rejected_request_data = paginator.page(page)
    except PageNotAnInteger:
        rejected_request_data = paginator.page(1)
    except EmptyPage:
        rejected_request_data = paginator.page(paginator.num_pages)

    return render(request, 'manage_requests_rejected.html', {'rejected_request' : rejected_request_data, 'context': context})

@login_required
def manage_requests_close(request):
    close_request_data = BookLendDetail.objects.filter(status = 'c').order_by("-close_date")
    context = manage_requests_count()

    paginator = Paginator(close_request_data, 10)
    page = request.GET.get('page')

    try:
        close_request_data = paginator.page(page)
    except PageNotAnInteger:
        close_request_data = paginator.page(1)
    except EmptyPage:
        close_request_data = paginator.page(paginator.num_pages)

    return render(request, 'manage_requests_close.html', {'close_request' : close_request_data, 'context': context})


@login_required
def confirm_lend_request(request):

    request_id = request.GET.get('request_id')
    request_data = BookLendDetail.objects.get(id = request_id)
    request_data.lent_date = date.today()
    request_data.status = 'l'
    if request_data.book.quantity == 1:
        request_data.book.status = 'l'
    request_data.book.quantity = request_data.book.quantity - 1
    request_data.save()

    return render(request, 'manage_requests')

@login_required
def reject_lend_request(request):
    request_id = request.GET.get('request_id')
    request_data = BookLendDetail.objects.get(id = request_id)
    request_data.close_date = date.today()
    request_data.status = 'n'
    request_data.save()

    return render(request, 'manage_requests')

@login_required
def close_request(request):
    request_id = request.GET.get('request_id')
    request_data = BookLendDetail.objects.get(id = request_id)
    request_data.close_date = date.today()
    request_data.status = 'c'
    request_data.save()

    return render(request, 'manage_requests')