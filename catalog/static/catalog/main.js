const numberOfSuggestions = 5;

// Get the CSFR token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

document.addEventListener('DOMContentLoaded', () => {

    document.querySelectorAll('.author-search-input').forEach(element => {
        element.onkeyup = searchAuthor;
    });
    document.querySelectorAll('.book-search-input').forEach(element => {
        element.onkeyup = searchBook;
    });
    document.querySelectorAll('.toggle-cart-button').forEach(element => {
        element.onclick = toggleCart;
    });

    let reviewButton = document.querySelector('#submit-review');
    if (reviewButton !== null) {
        reviewButton.onclick = reviewBook;
    }

    document.addEventListener('click', () => {

        // Clear suggestions when not active    
        if (!document.activeElement.classList.contains('author-search-input')) {
            suggestions = document.querySelector('.author-suggestions');
            if (suggestions !== null) {
                suggestions.replaceChildren();
            }
        } else {
            searchAuthor();
        };
        if (!document.activeElement.classList.contains('book-search-input')) {
            suggestions = document.querySelector('.book-suggestions');
            if (suggestions !== null) {
                suggestions.replaceChildren();
            }
        }
        else {
            searchBook();
        };
    })
})

function searchAuthor() {
    // Get information
    const query = document.querySelector('.author-search-input').value;
    const autocomplete = document.querySelector('.author-suggestions');
    // If no query, return
    if (query.length === 0) {
        autocomplete.replaceChildren();
        return;
    }
    // Request authors matching the query
    fetch(`/catalog/api/search/author?` + new URLSearchParams({
        'query': query
    }))
    .then(response => response.json())
    .then(results => {
        // Update the autocomplete list
        autocomplete.replaceChildren(
            ...results.slice(0, numberOfSuggestions).map(item => {
                let li = document.createElement('li');
                let a = document.createElement('a');
                li.className = 'suggestion-item'
                a.className = 'suggestion-link'
                a.href = item['url'];
                a.innerHTML = item['full_name'];
                li.appendChild(a);
                return li;
            })
        );
    });
}

function searchBook() {
    // Get information
    const query = document.querySelector('.book-search-input').value;
    const autocomplete = document.querySelector('.book-suggestions');
    // If no query, return
    if (query.length === 0) {
        autocomplete.replaceChildren();
        return;
    }
    // Request books matching the query
    fetch(`/catalog/api/search/book?` + new URLSearchParams({
        'query': query
    }))
    .then(response => response.json())
    .then(results => {
        // Update the autocomplete list
        autocomplete.replaceChildren(
            ...results.slice(0, numberOfSuggestions).map(item => {
                let li = document.createElement('li');
                let a = document.createElement('a');
                li.className = 'suggestion-item'
                a.className = 'suggestion-link'
                a.href = item['url'];
                a.innerHTML = item['title'];
                li.appendChild(a);
                return li;
            })
        );
    });
}

function toggleCart() {
    // Send request to add or remove item from cart
    fetch(`/catalog/cart/toggle/${this.dataset.book}`)
    .then(response => response.json())
    .then(response => {
        // Update the button label and cart badge
        if (response['message'].startsWith("Added")) {
            this.innerHTML = 'Remove from Cart';
            document.querySelector('#cart-badge').innerHTML++;
        } else if (response['message'].startsWith("Removed")) {
            this.innerHTML = 'Add to Cart';
            document.querySelector('#cart-badge').innerHTML--;
        }
    })
}

function reviewBook() {
    // Get comment and rating
    const comment = document.querySelector('#user-review-comment');
    const rating = document.querySelector('#user-review-rating');
    const button = document.querySelector('#submit-review');
    // If the input fields are disabled, enable them and change button label.
    if (comment.disabled || rating.disabled) {
        comment.disabled = false;
        rating.disabled = false;
        button.value = 'Post Review';
        return false;
    }
    // If either field is empty, prompt user to fill them.
    if (comment.value.length === 0) {
        comment.classList.add('is-invalid');
        return false;
    } else {
        comment.classList.remove('is-invalid');
    }
    if (rating.value.length === 0 || rating.value < 1 || rating.value > 10) {
        rating.classList.add('is-invalid');
        return false;
    } else {
        rating.classList.remove('is-invalid');
    }

    // Send a POST request to submit the review.
    fetch(`/catalog/review/${this.dataset.book}`, {
        method: 'POST',
        mode: 'same-origin',
        headers: {'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            comment: comment.value,
            rating: rating.value,
        }),
    })
    .then(response => {
        if (response.status !== 201) {
            throw `Some error occurred! Status: ${response.status}`;
        }
        return response;
    })
    .then(response => response.json())
    .then(response => {
        // Print result
        console.log(response);
    })
    .then(() => {
        // Disable the form and change button text.
        comment.disabled = true;
        rating.disabled = true;
        button.value = 'Edit Review';
    })

    return false;
}