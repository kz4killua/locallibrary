import datetime
import json

from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model, get_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Book, Author, BookCopy, Loan, Review
from .forms import LoanForm, ReviewForm, BookSearchForm, AuthorSearchForm, BookForm, AuthorForm, BookCopyForm


User = get_user_model()


def can_review(user_id, book_id):
    """Returns True if a user can review a book and False otherwise.
    
    A user can only review a book that they have previously borrowed."""
    return Loan.objects.filter(
        borrower__id=user_id, 
        bookcopy__book__id=book_id).exists()


def index(request):
    return HttpResponseRedirect(reverse('catalog:all-books'))


class BookListView(generic.ListView):
    model = Book
    template_name = "catalog/book_list.html"
    paginate_by = 20


class BookDetailView(generic.DetailView):
    model = Book
    template_name = "catalog/book_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["user_review"] = Review.objects.get(
                user__id=self.request.user.id, 
                book__id=self.kwargs['pk'])
        except Review.DoesNotExist:
            context["user_review"] = None
        context["can_review"] = can_review(self.request.user.id, self.kwargs['pk'])
        return context


class AuthorListView(generic.ListView):
    model = Author
    template_name = "catalog/author_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author_search_form"] = AuthorSearchForm()
        return context


class AuthorDetailView(BookListView):
    template_name = "catalog/author_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = Author.objects.get(pk=self.kwargs['pk'])
        context['list_name'] = f"Books by {str(context['author'])}"
        return context

    def get_queryset(self):
        return Book.objects.filter(authors__id=self.kwargs['pk'])


class AllBooks(BookListView, generic.ListView):
    template_name = "catalog/all_books.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["book_search_form"] = BookSearchForm()
        context['list_name'] = 'All Books'
        return context


class AllAuthors(AuthorListView, generic.ListView):
    template_name = "catalog/all_authors.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author_search_form"] = AuthorSearchForm()
        context['list_name'] = 'All Authors'
        return context


class BookCopyListView(generic.ListView):
    model = BookCopy
    template_name = "catalog/bookcopy_list.html"

    def get_queryset(self):
        return BookCopy.objects.filter(book__id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = Book.objects.get(id=self.kwargs['pk'])
        return context


class BookSearchView(BookListView):
    """Displays search results for a book."""

    def get_form_query(self):
        form = BookSearchForm(self.request.GET)
        if not form.is_valid():
            raise Http404()
        query = form.cleaned_data["query"] 
        return query
    
    def get_queryset(self):  
        return Book.objects.filter(title__icontains=self.get_form_query())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_name'] = f'Search results for "{self.get_form_query()}"'
        return context
        

class AuthorSearchView(AuthorListView):
    """Displays search results for an author."""

    def get_form_query(self):
        form = BookSearchForm(self.request.GET)
        if not form.is_valid():
            raise Http404()
        query = form.cleaned_data["query"] 
        return query

    def get_queryset(self):  
        return Author.objects.filter(
            Q(first_name__icontains=self.get_form_query()) |
            Q(last_name__icontains=self.get_form_query())
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_name'] = f'Search results for "{self.get_form_query()}"'
        return context


class CartView(LoginRequiredMixin, BookListView):
    """Displays all books in a user's cart."""
    template_name = 'catalog/cart.html'

    def get_queryset(self):
        cart = self.request.session.get('cart', list())
        return Book.objects.filter(pk__in=cart)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_name'] = f"Books in Cart"
        return context


@login_required
def toggle_cart(request, pk):   
    """Adds or removes a book from the cart.""" 
    cart = request.session.get('cart', list())
    # Make sure a book with that pk exists
    try:
        Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        raise Http404()
    # Add or remove the book from the cart
    if pk not in cart:
        cart.append(pk)
        message = f"Added book {pk} to cart"
    else:
        cart.remove(pk)
        message = f"Removed book {pk} from cart"
    # Update the cart and return response
    request.session['cart'] = cart
    return JsonResponse({
        "message": message
    }, status=201)


@login_required
def checkout(request):
    """Creates loans for all books on a user's cart."""

    # Cart must not be empty
    if not len(request.session.get('cart', list())):
        raise Http404()

    # Collect data
    loan_form = LoanForm(request.POST or None)
    books = Book.objects.filter(id__in=request.session['cart'])
    loan_date = datetime.date.today()
    due_back_date = datetime.date.today() + datetime.timedelta(weeks=3)
    context = {
        "loan_form": loan_form,
        "books": books,
        "loan_date": loan_date,
        "due_back_date": due_back_date,
    }

    if request.method == "GET":
        return render(request, "catalog/checkout.html", context)
    else:
        # Display error messages if the form is invalid
        if not loan_form.is_valid():
            return render(request, "catalog/checkout.html", context)
        # Create a loan object for each book
        for book in books:
            Loan(
                bookcopy = book.available_copies()[0],
                borrower = request.user,
                loan_date = loan_date,
                due_back_date = due_back_date,
            ).save()
        # Clear the cart
        request.session['cart'] = list()
        # Return a success message
        return render(request, "catalog/checkout_success.html", {
            "books": books,
            "due_back_date": due_back_date,
            "loan_date": loan_date,
        })


@login_required
def borrowed(request):
    """Display all of the user's active loans."""
    return render(request, "catalog/borrowed.html", {
        "loans": Loan.objects.filter(borrower_id=request.user.id, return_date=None)
    })


@login_required
def review(request, pk):
    """Posts or updates a review."""
    if request.method == "POST":

        # Load data
        data = json.loads(request.body)
        review = ReviewForm(data={
            'comment': data['comment'],
            'rating': int(data['rating'])
        })
        book = get_object_or_404(Book, pk=pk)

        # Make sure the review is valid.
        if not review.is_valid():
            return JsonResponse({'message': 'invalid review'}, status=400)
        if not can_review(request.user.id, book.id):
            raise Http404()

        # Delete any previous reviews by the user
        try:
            Review.objects.get(user_id=request.user.id, book_id=book.id).delete()
        except Review.DoesNotExist:
            pass

        # Save the new review
        review = review.save(commit=False)
        review.user = request.user
        review.book = book
        review.save()
        return JsonResponse({'message': 'review saved'}, status=201)


class BookCreateView(PermissionRequiredMixin, generic.CreateView):
    permission_required = 'catalog.add_book'
    model = Book
    form_class = BookForm
    template_name = 'catalog/model_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = 'Book'
        return context

    def get_success_url(self):
        return reverse('catalog:book-detail', args=(self.object.pk,))


class BookUpdateView(PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'catalog.change_book'
    model = Book
    form_class = BookForm
    template_name = 'catalog/model_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = 'Book'
        return context


class BookDeleteView(PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'catalog.delete_book'
    model = Book
    success_url = reverse_lazy('catalog:all-books')


class AuthorCreateView(PermissionRequiredMixin, generic.CreateView):
    permission_required = 'catalog.add_author'
    model = Author
    form_class = AuthorForm
    template_name = 'catalog/model_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = 'Author'
        return context

    def get_success_url(self):
        return reverse('catalog:author-detail', args=(self.object.pk,))


class AuthorUpdateView(PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'catalog.change_author'
    model = Author
    form_class = AuthorForm
    template_name = 'catalog/model_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = 'Author'
        return context


class AuthorDeleteView(PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'catalog.delete_author'
    model = Author
    success_url = reverse_lazy('catalog:all-authors')


class BookCopyCreateView(PermissionRequiredMixin, generic.CreateView):
    permission_required = 'catalog.add_bookcopy'
    model = BookCopy
    form_class = BookCopyForm
    template_name = 'catalog/model_form.html'

    def get_initial(self):
        return {'book': get_object_or_404(Book, id=self.kwargs['pk'])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = 'BookCopy'
        return context

    def get_success_url(self):
        return reverse('catalog:book-copies', args=(self.object.book.pk,))


class BookCopyUpdateView(PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'catalog.change_bookcopy'
    model = BookCopy
    form_class = BookCopyForm
    template_name = 'catalog/model_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = 'BookCopy'
        return context

    def get_success_url(self):
        return reverse('catalog:book-copies', args=(self.object.book.pk,))


class BookCopyDeleteView(PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'catalog.delete_bookcopy'
    model = BookCopy

    def get_success_url(self):
        return reverse('catalog:book-copies', args=(self.object.book.pk,))


class ActiveLoanListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.view_loan'
    model = Loan
    template_name = "loan_list.html"

    def get_queryset(self):
        return Loan.objects.filter(return_date=None)


class LoanUpdateView(PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'catalog.change_loan'
    model = Loan
    form_class = LoanForm
    template_name = 'catalog/model_form.html'
    success_url = reverse_lazy('catalog:active-loans')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = 'Loan'
        return context


class LoanDeleteView(PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'catalog.delete_loan'
    model = Loan

    def get_success_url(self):
        return reverse('catalog:active-loans')


def author_search_api(request):
    """Asynchronously returns all authors matching a search query."""
    query = request.GET['query']
    # Get all authors matching the query
    authors = Author.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )
    # Return JSON response
    response = [author.serialize() for author in authors]
    return JsonResponse(response, safe=False)


def book_search_api(request):
    """Asynchronously returns all books matching a search query."""
    query = request.GET['query']
    # Get all books matching the query
    books = Book.objects.filter(title__icontains=query)
    # Return JSON response
    response = [book.serialize() for book in books]
    return JsonResponse(response, safe=False)