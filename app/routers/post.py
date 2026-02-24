from typing import Dict, List, Optional
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: Dict = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):

    # To get all the posts, uncomment the line below and comment the line after it
    # posts = db.query(models.Post).all()

    # To get only the posts of the current user, uncomment the line below and comment the line above
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()

    # To get all the posts with a URL query parameters, uncomment the line below and comment the line above
    # posts = (
    #     db.query(models.Post)
    #     .filter(models.Post.title.contains(search))
    #     .limit(limit)
    #     .offset(skip)
    #     .all()
    # )

    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(oauth2.get_current_user),
):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostOut)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(oauth2.get_current_user),
):
    # To get a single post, uncomment the line below and comment the line after it
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found",
        )
    # To get only the post of the current user, uncomment the lines below and comment the lines above
    # if post.owner_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not authorized to perform requested action",
    #     )

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with is: {id} was not found",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Post)
def update_post(
    id: int,
    updated_post: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.update(updated_post.model_dump(), synchronize_session=False)

    db.commit()

    return post_query.first()
