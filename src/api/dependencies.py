from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: Annotated[int, Query(default=1, ge=1)]
    per_page: Annotated[int | None, Query(default=None, ge=1, le=30)]


PaginationDep = Annotated[PaginationParams, Depends()]