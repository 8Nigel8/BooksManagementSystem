class BookNotFound(Exception):
    def __init__(self, book_id):
        super().__init__("Book {} not found".format(book_id))