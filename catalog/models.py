from datetime import datetime
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator


User = get_user_model()


class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    portrait = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

    def get_absolute_url(self):
        return reverse('catalog:author-detail', args=(self.pk,))

    def serialize(self):
        """Returns author information in a Python dictionary. 
        
        This is helpful for returning JSON responses."""
        return {
            "full_name": str(self),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "url": self.get_absolute_url()
        }


class Book(models.Model):
    """Model representing a book."""
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author, related_name='books')
    summary = models.TextField(max_length=10000)
    cover = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f"{self.title} - {self.author_list()}"

    def author_list(self):
        """Returns a string listing all authors of a book separated by semicolons."""
        return '; '.join(
            [str(author) for author in self.authors.all()]
        )

    def get_absolute_url(self):
        return reverse('catalog:book-detail', args=(self.pk,))

    def available_copies(self):
        """Returns all available bookcopies 
        
        i.e book copies thaat are not on loan and not on maintenance."""
        return BookCopy.objects.filter(book_id=self.id, on_maintenance=False).exclude(
            id__in=Loan.objects.filter(return_date=None).values_list('bookcopy', flat=True)
        )

    def average_rating(self):
        """Returns the average rating of a book."""
        ratings = Review.objects.filter(book_id=self.id).values_list('rating', flat=True)
        if ratings:
            return round(sum(ratings) / len(ratings), 1)
        else:
            return None

    def serialize(self):
        """Returns author information in a Python dictionary. 
        
        This is helpful for returning JSON responses."""
        return {
            "title": self.title,
            "authors": [str(author) for author in self.authors.all()],
            "summary": self.summary,
            "cover": self.cover,
            "url": self.get_absolute_url()
        }

    


class BookCopy(models.Model):
    """Model representing a copy of a book."""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    on_maintenance = models.BooleanField(default=False)

    def __str__(self):
        return self.book.title

    def on_loan(self):
        """Returns True if a book copy is currently on loan and False otherwise."""
        return self.loans.filter(return_date=None).exists()


class Loan(models.Model):
    """Model representing a loan of a book copy."""
    bookcopy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name='loans')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateField()
    due_back_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['due_back_date']

    def __str__(self):
        return f'{self.bookcopy.book.title}; {self.loan_date}'

    def is_overdue(self):
        """Returns True if a loan is overdue and False otherwise."""
        return (self.return_date is None) and (self.due_back_date <= datetime.today().date())


class Review(models.Model):
    """Model representing a review made by a user on a book."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField(max_length=1000, blank=True, null=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user.username}: {self.rating}; {self.comment}'