from enum import Enum

######## Movie Enums #########

class LanguageEnum(str,Enum):
    English = "English"
    Hindi = "Hindi" 
    Tamil = "Tamil"
    Kannada = "Kannada"
    Telugu = "Telugu"
    Malayalam = "Malayalam"
    Marathi = "Marathi"
    Sanskrit = "Sanskrit"

class FormatEnum(str,Enum):
    _2D = "2D"
    _3D = "3D"
    _4DX = "4DX"
    _4DX_3D = "4DX 3D" 
    IMAX_3D = "IMAX 3D"

class GenreEnum(str,Enum):
    Drama = "Drama"
    Action = "Action"
    Thriller = "Thriller"
    Comedy = "Comedy"
    Adventure = "Adventure"
    Romance = "Romance"
    Fantasy = "Fantasy"
    SciFi = "SciFi"
    Family = "Family"
    Sports = "Sports"
    Animation = "Animation"
    Documentary = "Documentary"
    Musical = "Musical"
    Biography = "Biography"
    Horror = "Horror"

######## Artists Enums #########
class OccupationEnum(str, Enum):
    Actor = "Actor"
    Musician = "Musician"
    Singer = "Singer"
    Producer = "Producer"
    Director = "Director"
    Cameraman = "Cameraman"
    Music_Director = "Music Director"
    Composer = "Composer"
    Background_Scorev= "Background Score"
    Special_Appearances = "Special Appearances"
    Lyricist = "Lyricist"
    Writer = "Writer"
    Screenplay = "Screenplay"
    Dialogue_Writer = "Dialogue Writer"
    Voice_Cast = "Voice Cast"

######## Venue Enums #########
class FacilitiesEnum(str, Enum):
    Parking_Facility = "Parking Facility"
    Ticket_Cancellation = "Ticket Cancellation"
    F_B = "F&B"
    M_Ticket = "M Ticket"
    Food_Court = "Food Court"

######## Booking Enums #########
class BookingEnum(str, Enum):
    Booked = "Booked"
    Cancelled = "Cancelled"

######## User Gender Enums #########
class GenderEnum(str, Enum):
    Male = "Male"
    Female = "Female"

######## Seat Status Enums #########
class SeatStatus(str,Enum):
    Sold_Out = "Sold Out"
    Selected = "Selected"
    Available = "Available"
    Bestseller = "Bestseller"
    Filling_Fast = "Filling Fast"
    Almost_Full = "Almost Full"