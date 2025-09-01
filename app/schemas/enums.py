from enum import Enum

class GenreEnum(str, Enum):
    FICTION = "Fiction"
    NON_FICTION = "Non-Fiction"
    SCIENCE = "Science"
    HISTORY = "History"
    BIOGRAPHY = "Biography"
    FANTASY = "Fantasy"
    MYSTERY = "Mystery"
    THRILLER = "Thriller"
    ROMANCE = "Romance"
    SCIENCE_FICTION = "Science Fiction"