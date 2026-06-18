from sqlalchemy.orm import Session

from app.models.postgres.user_model import User
from app.schemas.user_schema import  UserUpdate, UserLogin

############ User CRUD #########
def user_login(db: Session, data: UserLogin):
    # Look for an existing user by phone or email
    user = None
    if data.phone_no:
        user = db.query(User).filter(User.phone_no == data.phone_no).first()
    if not user and data.email:
        user = db.query(User).filter(User.email == data.email).first()

    if user:
        user.signed_in = True
        db.commit()
        db.refresh(user)
        return {"message": "Login successful", "user": user}

    # If user doesn't exist, create new
    new_user = User(**data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "New user created and logged in", "user": new_user}  

def read_user(db:Session, user_id: int | None = None):
    query = db.query(User)
    if user_id :
        return query.filter(User.user_id == user_id).first()
    return query.all()

def update_user(db:Session,user: UserUpdate, user_id: int):
    update_query = db.query(User).filter(User.user_id == user_id).first()
    if update_query:
        for key,value in user.model_dump(exclude_unset=True).items():
            setattr(update_query,key,value)
    if not update_query:
        return None
    db.commit()
    db.refresh(update_query)
    return update_query

def sign_out_user(db:Session,user_id: str):
    user = db.query(User).filter(User.user_id==user_id).first()
    if user:
        user.signed_in = False
        db.commit()
        db.refresh(user)

    return {"message": "User signed out successfully"}