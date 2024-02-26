from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str
    password: str


class ShowUser(BaseModel):
    name: str
    email: str

    class Config:
        orm_mode = True


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str = None


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


class ShowPost(BaseModel):
    title: str
    content: str
    published: bool

    class Config:
        orm_mode = True


class UpdatePost(BaseModel):
    title: str
    content: str
    published: bool


class UpdateUser(BaseModel):
    name: str
    email: str
    password: str


class ShowUpdateUser(BaseModel):
    name: str
    email: str

    class Config:
        orm_mode = True


class ShowUpdatePost(BaseModel):
    title: str
    content: str
    published: bool
