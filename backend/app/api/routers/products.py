"""Router de productos. Lectura pública, escritura solo admin."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_admin, get_db
from app.models import Product
from app.schemas.common import MessageResponse
from app.schemas.product import ProductCreate, ProductPublic, ProductUpdate
from app.services import ProductService

router = APIRouter(prefix="/productos", tags=["productos"])


def _service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)


def _to_public(product: Product) -> ProductPublic:
    return ProductPublic.model_validate(
        {
            "_id": product.id,
            "nombre": product.nombre,
            "precio": product.precio,
            "descripcion": product.descripcion,
            "imagen": product.imagen,
            "categoria": product.categoria.value,
            "createdAt": product.created_at,
            "updatedAt": product.updated_at,
        }
    )


@router.get("", response_model=List[ProductPublic])
def list_products(service: ProductService = Depends(_service)) -> List[ProductPublic]:
    return [_to_public(p) for p in service.list_products()]


@router.post(
    "",
    response_model=ProductPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: ProductCreate,
    _: CurrentUser = Depends(get_current_admin),
    service: ProductService = Depends(_service),
) -> ProductPublic:
    product = service.create_product(payload)
    return _to_public(product)


@router.put("/{product_id}", response_model=ProductPublic)
def update_product(
    product_id: str,
    payload: ProductUpdate,
    _: CurrentUser = Depends(get_current_admin),
    service: ProductService = Depends(_service),
) -> ProductPublic:
    product = service.update_product(product_id, payload)
    return _to_public(product)


@router.delete("/{product_id}", response_model=MessageResponse)
def delete_product(
    product_id: str,
    _: CurrentUser = Depends(get_current_admin),
    service: ProductService = Depends(_service),
) -> MessageResponse:
    service.delete_product(product_id)
    return MessageResponse(message="Producto eliminado")
