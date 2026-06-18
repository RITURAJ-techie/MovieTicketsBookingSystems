from bson import ObjectId
from fastapi import HTTPException

from app.config.mongo_config import db
from app.schemas.artist_schema import Artist,UpdateArtist

############### Create new artist ##############
async def create_artist(artist: Artist):
    artist_dict = artist.model_dump(by_alias=True, exclude_none=True)
    result = await db["artist_details"].insert_one(artist_dict)
    artist_dict["_id"] = str(result.inserted_id)
    return artist_dict 

############### Fetch artist ##############
async def get_artists():
    people = await db["artist_details"].find().to_list()
    convert_id_to_string = []
    for artist in people:
        artist["_id"] = str(artist["_id"])
        convert_id_to_string.append(artist)
    return convert_id_to_string 

############## Fetch artist by id ##############
#get the artist details - peers, family and more
async def get_artist_by_id(artist_id:str):
    pipeline = [
        {"$match":{"_id":ObjectId(artist_id)}},
        {"$lookup":{
            "from":"artist_details",
            "localField": "_id",
            "foreignField":"_id",
            "as":"peers_info"
        }},
        {"$lookup":{
            "from":"artist_details",
            "localField":"_id",
            "foreignField":"_id",
            "as":"family_info"
        }},
        {"$project":{
            "_id": {"$toString": "$_id"},
            "name":1,
            "occupation":1,
            "also_known":1,
            "birthplace":1,
            "children":1,
            "about":1,
            "spouse":1,
            "family":1,
            "peers_and_more":1,
            
            "peers_info":{
                "$map":{
                    "$input": "$peers_info",
                    "as":"person",
                    "in":{
                        "_id":{"$toString":"$$person.id"},
                        "name":"$$person.name",
                        "occupation":"$$person.occupation",
                        "also_known":"$$also_known",
                        "birthplace":"$$person.birthplace",
                        "children":"$$person.children",
                        "about":"$$person.about",
                        "spouse":"$$person.spouse",
                        "family":"$$person.family",
                        "peers_and_more":"$$person.peers_and_mmore"
                    }

                }

            },
            "family_info":{
                "$map":{
                    "$input": "$family_info",
                    "as":"person",
                    "in":{
                        "_id":{"$toString":"$$person.id"},
                        "name":"$$person.name",
                        "occupation":"$$person.occupation",
                        "also_known":"$$also_known",
                        "birthplace":"$$person.birthplace",
                        "children":"$$person.children",
                        "about":"$$person.about",
                        "spouse":"$$person.spouse",
                        "family":"$$person.family",
                        "peers_and_more":"$$person.peers_and_mmore"
                    }

                }

            }
            
            }}
    ]
    person = await db["artist_details"].find_one({"_id":ObjectId(artist_id)})
    if not person:
        raise HTTPException(status_code=404, detail="Artist not found!")
    person["_id"]=str(person["_id"])
    return person

############### Update an artist ##############
async def update_artist(artist_id: str, artist: UpdateArtist):
    update_data = artist.model_dump(exclude_unset=True)
    result = await db["artist_details"].update_one(
        {"_id":ObjectId(artist_id)},
        {"$set":update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Artist not found!")
    updated_artist = await db["artist_details"].find_one({"_id":ObjectId(artist_id)})
    updated_artist["id"] = str(updated_artist["_id"])
    return updated_artist    

############### Delete artist ##############
async def soft_delete_artist(artist_id: str):
    result = await db["artist_details"].update_one(
        {"_id":ObjectId(artist_id),"is_available":True},
        {"$set":{"is_available":False}}
    )
    if result.matched_count ==0:
        raise HTTPException(status_code=404, detail="Artist doesn't exits")
    return {"message":"Artist deleted successfully"}