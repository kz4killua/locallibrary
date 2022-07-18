from django import forms

from .models import BookCopy, Loan, Review, Book, Author


class StyledValidation:

    def clean(self):
        data = super().clean()
        # Add a CSS class to any field that is invalid
        for error in self.errors:
            try:
                self.fields[error].widget.attrs['class'] += ' is-invalid'
            except KeyError:
                self.fields[error].widget.attrs['class'] = 'is-invalid'
        return data


class BookSearchForm(StyledValidation, forms.Form):
    query = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'book-search-input',
            'placeholder': 'Enter the name of a book',
            }),
        help_text="Enter the name of a book", 
        min_length=1, 
        strip=True,)


class AuthorSearchForm(StyledValidation, forms.Form):
    query = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'author-search-input',
            'placeholder': 'Enter the name of an author'
            }),
        help_text="Enter the name of an author", 
        min_length=1, 
        strip=True)


class LoanForm(forms.Form):
    pass


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("comment", "rating")


class BookForm(StyledValidation, forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'authors', 'summary', 'cover')
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'authors': forms.SelectMultiple(
                attrs={
                    'class': 'form-select',
                }
            ),
            'summary': forms.Textarea(
                attrs={
                    'class': 'form-control'
                }
            ),
            'cover': forms.URLInput(
                attrs={
                    'class': 'form-control'
                }
            )
        }


class AuthorForm(StyledValidation, forms.ModelForm):

    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'portrait')
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'portrait': forms.URLInput(
                attrs={
                    'class': 'form-control'
                }
            )
        }


class BookCopyForm(StyledValidation, forms.ModelForm):

    class Meta:
        model = BookCopy
        fields = ('book', 'on_maintenance')
        widgets = {
            'book': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'on_maintenance': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            )
        }