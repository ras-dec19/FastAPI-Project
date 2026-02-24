from datetime import datetime
from typing import Literal, Union
from pydantic import BaseModel, EmailStr

### Request models


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


############################


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    pass


class UserLogin(UserBase):
    pass


#############################


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Union[int, None] = None


class Vote(BaseModel):
    post_id: int
    dir: Literal[0, 1]  # 0 for downvote, 1 for upvote


### Response model


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


##########################


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True
