# Local Library

# Video Demo
https://youtu.be/U8VyPCXplWM

# Description
This is a website for a library. It allows users to borrow books which can then be picked up at a library. 

It allows users to:
- Search for books
- Search for authors
- View the availability status of books in the library
- View details about each book or author
- View all books by an author

Logged in users can:
- Rate and comment on books that they have previously borrowed
- Add books to their cart
- Checkout (borrow) books in the cart
- View their borrowed books

Librarians have extra permissions to:
- Create, delete, and modify books
- Create, delete, and modify authors
- Create, delete, and modify book copies
- View all active loans by all users
- Edit and delete a loan

# Distinctiveness and Complexity
This is my final project for CS50's Web Programming with Python and JavaScript course. (Learn more about CS50 [here](https://cs50.harvard.edu/)). This project however, is very distinct from the *search*, *wiki*, *commerce*, *mail*, and *network* projects used in the course. Project details are described below.

This locallibrary site was built using Django at the backend and Javascript, HTML, and CSS on the front end. *catalog/static/main.js* is a Javascript file that allows users to:
- Search for books and authors asynchronously i.e. without full reloads of the page
- Submit and edit reviews asynchronously
- Add and remove a book from the cart asynchronously

The app is also mobile-responsive. (Seriously, check it out!)

# Files Overview
The project includes two apps: **accounts** and **catalog**.

## accounts
The **accounts** app handles user authentication and registration. it includes a custom user model which is used in the project and urls to login, logout, and register a user. These urls are defined in *accounts/urls.py* and the custom user model can be found in *accounts/models.py*. This user model is just a subclass of Django's *AbstractUser* and does not add any new properties but can be used to extend user functionality down the line. (In fact, Django recommends starting each new project with a custom user model.)

*accounts/views.py* includes a views to register a user (register), login a user (Login), and logout a user (Logout). The views Login and Logout inherit from Django's built in authentication views: LoginView and LogoutView respectively.

Templates for this app can be found in *accounts/templates*, static files can be found in *accounts/static* and forms for the accounts app can be found in *accounts/forms.py*. 

## catalog
The **catalog** app handles all the main library functionality.

### Models
In *catalog/models.py*, models are defined for a/an Author, Book, BookCopy, Loan, and Review. 

The Author model represents an author and includes their first name, last name, and a URL linking to a portrait image. Most notably, the Author class has a *serialize* method which returns author information in a Python dictionary. This is helpful for returning JSON responses.

The Book model represents a book and contains the title, the author(s) of the book, a summary and a URL linking to a cover photo. It also implements some important methods:
- *author_list*: Returns a string listing all authors of a book separated by semicolons.
- *available_copies*: Returns all available copies (BookCopy) of a book.
- *average_rating*: Returns the average rating of a book.
- *serialize*: Returns book information in a Python dictionary. Again, this is helpful for returning JSON responses.

The BookCopy model represents a physical (or digital) copy of a book. A book copy can be marked as *on_maintenance*. Book copies on maintenance are not visible to regular users and are not available for loans.

The Loan model represents information about a book. It has fields to represent the book copy that was borrowed, the user who borrowed the book, the date the book was borrowed, the date the book is due to be returned, and the date the user eventually returned the book. 
By default, loans are 3 weeks long and the *due_back_date* is added automatically upon checkout. (See *checkout* in *catalog/views.py*)

The Review model represents information about a review (comment and rating) made by a user on a book. It is important to note that:
- Each user is only allowed to review a book once.
- A user can only review a book if they have previously borrowed the book.
These constraints are not enforced by the model itself but by the views.

### Views
Views are defined in *catalog/views.py*. Most of these are class based views inheriting from Django's built in generic views. The views are documented with docstrings.

### Forms
Forms for this app are defined in *catalog/forms.py*. These include forms for searching for a user, searching for a book, and creating and updating books, authors, loans, reviews and book copies.

### URLS
URLS are defined in *catalog/urls.py*

### Templates and Static Files
Static files and templates are contained in *catalog/static* and *catalog/templates* respectively.

# Styling
Most of the styling for this site was done with [Bootstrap](https://getbootstrap.com/). However, a lot of custom CSS was used as well.

# How to Run
1. Install Python.
2. Open a terminal and run `pip install -r requirements.txt`.
3. Navigate to the project directory.
4. Run `python manage.py runserver`.

# How to add a librarian
Many parts of the site can only be accessed by *Librarian* users. To add a librarian:
1. Run the site.
2. Go to the admin page. 
3. Login as a superuser.
4. Go to Groups.
5. Add a group with name *Librarian*.
6. Add the following permissions:
    - add author
    - change author
    - delete author
    - view author
    - add book
    - change book
    - delete book
    - view book
    - add bookcopy
    - change bookcopy
    - delete bookcopy
    - view bookcopy
    - add loan
    - change loan
    - delete loan
    - view loan
7. Create a new user from the admin page.
8. Add the user to the *Librarian* group.

# What this site does not do
- A book copy can be placed *on_maintenance*. This restricts users from borrowing that copy. However, there is currently no way to view all book copies that are on maintenance.
- The admin page for this site is Django's default admin. No customization was done. This is because books, authors, book copies, etc. can be created, modified and deleted in the site by *Librarians* without the admin page.
- It is possible that a book placed in a cart could have all its available copies loaned out before it is moved to checkout. Say there is only one copy of a book, and a user adds it to their cart. The user could return to their cart a few hours later, after a different user has borrowed that available copy and still attempt to checkout.

# Additional Information
This site was inspired by and builds on the Mozilla Developer Network's [local library tutorial](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Tutorial_local_library_website). However, this site is far more complex and goes beyond the basics covered in this tutorial.