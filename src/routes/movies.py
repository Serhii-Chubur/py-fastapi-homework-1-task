import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.database.models import MovieModel
from src.schemas.movies import (
    MovieDetailResponseSchema,
    MovieListResponseSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select  # Import select for async queries
from src.database.models import MovieModel


router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movies(
    db: AsyncSession, first_movie: int = 0, per_page: int = 10
):
    stmt = select(MovieModel).offset(first_movie).limit(per_page)
    movies = db.query(MovieModel).offset(first_movie).limit(per_page).all()
    # Execute the statement
    # movies = result.scalars().all()  # Get the results
    return movies


# def get_movies(
#     page: int = Query(1, ge=1, description="Page number"),
#     per_page: int = Query(10, ge=1, le=20, description="Page size"),
#     db: Session = Depends(get_db),
# ):
# first_movie: int = (page - 1) * per_page
# movies = db.query(MovieModel).offset(first_movie).limit(per_page).all()
# if not movies:
#     raise HTTPException(status_code=404, detail="No movies found.")
# total_items = db.query(MovieModel).count()
# total_pages = math.ceil(total_items / per_page)
# if page < 1:
#     raise HTTPException(
#         status_code=422,
#         detail=[
#             {
#                 "loc": ["query", "page"],
#                 "msg": "ensure this value is greater than or equal to 1",
#                 "type": "value_error.number.not_ge",
#             }
#         ],
#     )
# prev_page = (
#     f"/theater/movies/?page={page - 1}&per_page={per_page}"
#     if page > 1
#     else None
# )
# next_page = (
#     f"/theater/movies/?page={page + 1}&per_page={per_page}"
#     if page < total_pages
#     else None
# )
# return MovieListResponseSchema(
#     movies=movies,
#     prev_page=prev_page,
#     next_page=next_page,
#     total_pages=total_pages,
#     total_items=total_items,
# )


@router.get("/movies/{movie_id}", response_model=MovieDetailResponseSchema)
def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=404, detail="Movie with the given ID was not found."
        )
    return movie
