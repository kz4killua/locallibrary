from django.contrib import admin

from .models import Author, Book, BookCopy, Loan, Review

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(BookCopy)
admin.site.register(Loan)
admin.site.register(Review)
