import json
import os

# Ensure the local directory exists
LOCAL_DIR = 'D:\\Miraclesoft\\BookRecommendation_System'
os.makedirs(LOCAL_DIR, exist_ok=True)

# File paths for storing books and ratings
BOOKS_FILE = os.path.join(LOCAL_DIR, 'books_data2.json')
RATINGS_FILE = os.path.join(LOCAL_DIR, 'ratings_data2.json')

# Trie Node
class TrieNode:
    def __init__(self):
        self.children = {}
        self.books = []

# Trie data structure for searching
class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, book):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.books.append(book)

    def search(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._get_books(node)

    def _get_books(self, node):
        books = []
        if node.books:
            books.extend(node.books)
        for child in node.children.values():
            books.extend(self._get_books(child))
        return books

# Book class
class Book:
    def __init__(self, title, author, genre):
        self.title = title
        self.author = author
        self.genre = genre

    def to_dict(self):
        return {'title': self.title, 'author': self.author, 'genre': self.genre}

# User Rating class
class UserRating:
    def __init__(self, user_id):
        self.user_id = user_id
        self.ratings = {}

    def rate_book(self, book_title, rating):
        self.ratings[book_title] = rating

    def get_ratings(self):
        return self.ratings

    def save_ratings(self, file_path=RATINGS_FILE):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        data[self.user_id] = self.ratings
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_ratings(user_id, file_path=RATINGS_FILE):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data.get(user_id, {})
        except FileNotFoundError:
            return {}

def add_book(trie, books_list, title, author, genre):
    new_book = Book(title, author, genre)
    books_list.append(new_book.to_dict())
    trie.insert(title, new_book)

def view_books(books_list):
    if not books_list:
        print("No books available.")
    for idx, book in enumerate(books_list, 1):
        print(f"{idx}. Title: {book['title']}, Author: {book['author']}, Genre: {book['genre']}")

def save_books(books_list, file_path=BOOKS_FILE):
    with open(file_path, 'w') as f:
        json.dump(books_list, f, indent=4)

def load_books(trie, file_path=BOOKS_FILE):
    try:
        with open(file_path, 'r') as f:
            books_list = json.load(f)
            for book in books_list:
                trie.insert(book['title'], Book(book['title'], book['author'], book['genre']))
            return books_list
    except FileNotFoundError:
        return []

def recommend_books(user, books_list):
    user_ratings = user.get_ratings()

    if not user_ratings:
        print("No ratings available to base recommendations on.")
        return

    # Debug: Print the user's ratings
    print(f"User Ratings: {user_ratings}")

    favorite_genres = {}
    for book_title, rating in user_ratings.items():
        if rating >= 4:
            for book in books_list:
                if book['title'] == book_title:
                    favorite_genre = book['genre']
                    favorite_genres[favorite_genre] = favorite_genres.get(favorite_genre, 0) + 1

    # Debug: Print favorite genres and their counts
    print(f"Favorite Genres: {favorite_genres}")

    recommendations = []
    
    # Check for books in the user's favorite genre that haven't been rated yet
    if favorite_genres:
        top_genre = max(favorite_genres, key=favorite_genres.get)
        recommendations = [book for book in books_list if book['genre'] == top_genre and book['title'] not in user_ratings]

    # If no recommendations found in the favorite genre, recommend books from other genres
    if not recommendations:
        recommendations = [book for book in books_list if book['title'] not in user_ratings]
    
    # Format the output as required
    if recommendations:
        print("\nRecommendations:")
        for book in recommendations:
            print(f"Title: {book['title']}, Author: {book['author']}, Genre: {book['genre']}")
    else:
        print("No recommendations available.")

def search_books(trie, prefix):
    books = trie.search(prefix)
    if not books:
        print("No books found with that title.")
    else:
        for book in books:
            print(f"Title: {book.title}, Author: {book.author}, Genre: {book.genre}")

def main():
    trie = Trie()
    books_list = load_books(trie)

    while True:
        print("\n1. Add Book")
        print("2. View Books")
        print("3. Rate Book")
        print("4. Get Recommendations")
        print("5. Search Books")
        print("6. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            title = input("Enter book title: ")
            author = input("Enter author name: ")
            genre = input("Enter genre: ")
            add_book(trie, books_list, title, author, genre)
            save_books(books_list)
        elif choice == '2':
            view_books(books_list)
        elif choice == '3':
            username = input("Enter your username: ")
            user = UserRating(username)
            user.ratings = UserRating.load_ratings(username)

            if not books_list:
                print("No books available to rate.")
            else:
                print("Select a book to rate:")
                for idx, book in enumerate(books_list, 1):
                    print(f"{idx}. Title: {book['title']}, Author: {book['author']}, Genre: {book['genre']}")

                try:
                    book_choice = int(input("Enter the number of the book you want to rate: "))
                    if 1 <= book_choice <= len(books_list):
                        selected_book = books_list[book_choice - 1]
                        rating = float(input(f"Enter your rating for {selected_book['title']} (1-5): "))
                        user.rate_book(selected_book['title'], rating)
                        user.save_ratings()
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        elif choice == '4':
            username = input("Enter your username: ")
            user = UserRating(username)
            user.ratings = UserRating.load_ratings(username)
            print("\nRecommendations:")
            recommend_books(user, books_list)
        elif choice == '5':
            title_prefix = input("Enter title prefix to search: ")
            search_books(trie, title_prefix)
        elif choice == '6':
            break
        else:
            print("Invalid choice.")

if __name__ == '__main__':
    main()
