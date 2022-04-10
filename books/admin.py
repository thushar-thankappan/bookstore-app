from django.contrib import admin
from .models import Author, Category, Book, BookLendDetail

# admin.site.register(Book)
# admin.site.register(Author)
# admin.site.register(Category)
# admin.site.register(BookLendDetail)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'status', 'display_author', 'display_category')

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(BookLendDetail)
class BookLendDetailAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'reader', 'lent_date', 'return_date')
    list_filter = ('status', 'lent_date', 'return_date')
