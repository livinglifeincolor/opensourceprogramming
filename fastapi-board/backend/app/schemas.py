"""Pydantic request/response schemas for the posts resource.

This module defines the data-transfer objects used throughout the API:

* :class:`PostCreate` – validates a new-post request body.
* :class:`PostUpdate` – validates a partial-update request body.  At least
  one field must be present (enforced by a model validator).  Provides
  :meth:`PostUpdate.apply_to` to merge changes onto an existing row dict.
* :class:`PostResponse` – serialises a post row returned from the database.
* :class:`SearchResponse` – wraps a paginated search result set.

All models leverage Pydantic v2 field-level validation so that invalid
payloads are rejected at the boundary before they reach the database layer.
"""

from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class PostCreate(BaseModel):
    """Schema for creating a new post.

    Attributes:
        title: The post title.  Must be between 1 and 100 characters.
        content: The post body text.  Must be at least 10 characters long.
    """

    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=10)


class PostUpdate(BaseModel):
    """Schema for partially updating an existing post.

    Both fields are optional, but at least one must be explicitly provided
    (validated by :meth:`at_least_one_field`).  Use :meth:`apply_to` to
    merge only the sent fields onto an existing row dictionary.

    Attributes:
        title: New title for the post, or ``None`` to keep the existing one.
        content: New body text for the post, or ``None`` to keep the existing
            one.
    """

    title: str | None = None
    content: str | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "PostUpdate":
        """Require at least one field to be present in the request body.

        If both ``title`` and ``content`` are omitted there is nothing to
        update, so a 422 Unprocessable Entity error is returned.

        Returns:
            PostUpdate: The validated model instance (unchanged).

        Raises:
            ValueError: If neither ``title`` nor ``content`` was included in
                the request body.
        """
        if not self.model_fields_set:
            raise ValueError("At least one of 'title' or 'content' must be provided.")
        return self

    def apply_to(self, existing: dict) -> dict:
        """Merge only the explicitly sent fields onto an existing row dict.

        Uses ``model_fields_set`` to distinguish fields that were actually
        included in the request from those that were merely defaulted to
        ``None``.  Fields absent from the request body are left unchanged.

        Args:
            existing: A dictionary representing the current database row
                (e.g. ``dict(asyncpg.Record)``).

        Returns:
            dict: A new dictionary with the same keys as ``existing`` but
                with the client-supplied fields overwritten.
        """
        patch = self.model_dump(include=self.model_fields_set)
        return {**existing, **patch}


class PostResponse(BaseModel):
    """Schema for a post returned by the API.

    Attributes:
        id: Auto-incremented primary key of the post.
        title: Title of the post.
        content: Body text of the post.
        created_at: UTC timestamp of when the post was created.
    """

    id: int
    title: str
    content: str
    created_at: datetime

    # Allow initialisation directly from asyncpg Record objects.
    model_config = {"from_attributes": True}


class SearchResponse(BaseModel):
    """Schema for a paginated post search result.

    Attributes:
        total: Total number of posts that match the search query (across all
            pages).
        results: The post objects for the current page.
    """

    total: int
    results: list[PostResponse]
