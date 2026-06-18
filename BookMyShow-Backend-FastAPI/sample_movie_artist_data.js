// movie details of Dies Irae

db.movie_details.insertOne({
  _id: ObjectId("690dd4ca7d3359fc33ddad9f"),
  title: "Dies Irae",
  date_of_release: ISODate("2025-11-01T11:12:00.419Z"),
  duration: "1h55m",
  language: "Malayalam",
  rating: "A",
  format: "2D",
  genre: "Thriller",
  about: "Rohan's Lifestyle",
  is_active: true,
  is_available: true,
  is_stream: false,
  price_rent: 0,
  price_buy: 0,
  cast: [
    {
      _id: "690dd1f4ef47522c45f53ca5",
      role: "Actor"
    }
  ]
});


// Insert multiple artist documents into the artist_details collection

db.artist_details.insertMany([
  {
    _id: ObjectId("690dd1f4ef47522c45f53ca5"),
    name: "Pranav Mohanlal",
    occupation: ["Actor", "Lyricist"],
    birthplace: "TVM",
    about: "Artist also son of mohanlal",
    is_available: true,
    family: [
      { _id: "690dd278ef47522c45f53ca6", role: "Father" }
    ],
    children: 0
  },
  {
    _id: ObjectId("690dd278ef47522c45f53ca6"),
    name: "Mohanlal",
    occupation: ["Actor"],
    birthplace: "Pathanamthitta",
    children: 2,
    about: "Superstar",
    spouse: "Suchithra",
    family: [
      { _id: "690dd1f4ef47522c45f53ca5", role: "Son" }
    ],
    is_available: true,
    peer_and_more: [
      { _id: "690dd2d2ef47522c45f53ca7", role: "Actor" }
    ]
  },
  {
    _id: ObjectId("690dd2d2ef47522c45f53ca7"),
    name: "Mammootty",
    occupation: ["Actor"],
    also_known: "Mammootty",
    birthplace: "Kottayam",
    children: 2,
    about: "Indian film actor",
    spouse: "Sulfath",
    peer_and_more: [
      { _id: "690dd278ef47522c45f53ca6", role: "Actor" }
    ],
    is_available: true
  }
]);

