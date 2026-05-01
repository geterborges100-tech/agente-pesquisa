"""
app/routers/contacts.py
Endpoints de Contacts — alinhado com openapi_v1.yaml.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models_v1 import Contact
from app.repositories.contact_repository import ContactRepository
from app.schemas.schemas import ContactResponse, ContactUpdate, PaginatedContacts

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("", response_model=PaginatedContacts)
def list_contacts(
    segment: str | None = Query(None),
    consent_status: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedContacts:
    stmt = select(Contact)

    if segment:
        stmt = stmt.where(Contact.segment == segment)
    if consent_status:
        stmt = stmt.where(Contact.consent_status == consent_status)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    contacts = db.scalars(stmt.offset((page - 1) * limit).limit(limit)).all()

    return PaginatedContacts(
        data=[ContactResponse.model_validate(c) for c in contacts],
        total=total or 0,
    )


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ContactResponse:
    repo = ContactRepository(db)
    contact = repo.get_by_id(contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contato não encontrado.")
    return ContactResponse.model_validate(contact)


@router.patch("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: uuid.UUID,
    body: ContactUpdate,
    db: Session = Depends(get_db),
) -> ContactResponse:
    repo = ContactRepository(db)
    contact = repo.get_by_id(contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contato não encontrado.")

    data = body.model_dump(exclude_none=True)
    if data:
        # profile_summary não está no modelo Contact — ignora silenciosamente
        allowed = {"segment", "lead_score"}
        filtered = {k: v for k, v in data.items() if k in allowed}
        if filtered:
            repo.update(contact_id, filtered)
            db.commit()
            db.refresh(contact)

    return ContactResponse.model_validate(contact)
