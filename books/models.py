from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from datetime import date
from django.core.validators import RegexValidator

class Author(models.Model):
    """ This class represents the Model for an author of the book.
    """
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)

    # class Meta:
    #     ordering = ['lastname', 'firstname']

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.firstname} {self.lastname}'


class Category(models.Model):
    """ This class represents the category model for book category.
        e.g. social, comedy etc.
    """
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Book(models.Model):
    """ This is the class representing the model for books.
    """
    numeric = RegexValidator(r'^[0-9]*$', 'Only  numeric characters are allowed.')
    book_status = (('a', 'available'), ('l', 'lent'))

    title = models.CharField(max_length=250)
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Character ISBN number', validators=[numeric])
    description = models.TextField(max_length=500)
    price = models.IntegerField()
    total_quantity = models.IntegerField()
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=1, choices = book_status, blank = True, default = 'a')
    author = models.ManyToManyField(Author)
    category = models.ManyToManyField(Category)

    def __str__(self):
        return self.title

    # def save(self, *args, **kwargs):
    #     if self.pk is None:
    #         self.quantity = self.total_quantity
        
    def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.id)])

    def display_category(self):
        return ', '.join(category.name for category in self.category.all()[:3])

    display_category.short_description = "Category"

    def display_author(self):
        return ', '.join(author.firstname for author in self.author.all()[:3])

    display_author.short_description = "Author"



class BookLendDetail(models.Model):
    """ This class represents the actual details of the process of book lending.
        User can request to lend a book and librarial can grant it to the user.
    """
    book_status = (('p', 'pending'), ('l', 'lent'), ('r', 'returned'), ('c', 'closed'), ('n', 'rejected'))

    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    reader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    request_date = models.DateField(null=True, blank=True)
    lent_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    close_date = models.DateField(null=True, blank=True)
    charge = models.IntegerField()
    status = models.CharField(max_length=1, choices = book_status, blank = True, default = 'p')

    def __str__(self):
        return self.book.title

    @property
    def is_overdue(self):
        if self.return_date and date.today() > self.return_date:
            return True
        return False
