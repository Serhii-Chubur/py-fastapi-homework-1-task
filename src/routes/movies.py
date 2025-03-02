from math import ceil
from re import M
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.movies import (
    MovieDetailResponseSchema,
    MovieListResponseSchema,
)
from src.database import get_db, MovieModel


router = APIRouter()


# Write your code here
@router.get("/movies", response_model=MovieListResponseSchema)
async def get_movies(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
):
    total_items_query = select(func.count()).select_from(MovieModel)
    total_items_result = await db.execute(total_items_query)
    total_items = total_items_result.scalar()

    if total_items == 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    total_pages = ceil(total_items / per_page)

    movies_query = (
        select(MovieModel).limit(per_page).offset((page - 1) * per_page)
    )
    movies_result = await db.execute(movies_query)
    movies = movies_result.scalars().all()

    prev_page = (
        f"/movies?page={page - 1}&per_page={per_page}" if page > 1 else None
    )
    next_page = (
        f"/movies?page={page + 1}&per_page={per_page}"
        if page < total_pages
        else None
    )

    return MovieListResponseSchema(
        movies=movies,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
    )


@router.get("/movies/{movie_id}")
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await db.get(MovieModel, movie_id)
    if movie is None:
        raise HTTPException(
            status_code=404, detail="Movie with the given ID was not found."
        )
    return movie


@router.post("/create/", response_model=MovieDetailResponseSchema)
async def create_movie(
    movie: MovieDetailResponseSchema, db: AsyncSession = Depends(get_db)
):
    movie = MovieModel(**movie.model_dump())
    db.add(movie)
    await db.commit()
    await db.refresh(movie)
    return movie
