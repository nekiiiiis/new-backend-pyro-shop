"""Router del carrito (requiere autenticación)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db
from app.models import Cart
from app.schemas.cart import (
    AddToCartRequest,
    CartPublic,
    CartResponse,
    UpdateCartItemRequest,
)
from app.services import CartService

router = APIRouter(prefix="/api/cart", tags=["cart"])


def _service(db: Session = Depends(get_db)) -> CartService:
    return CartService(db)


def _to_public(cart: Cart) -> CartPublic:
    return CartPublic.model_validate(
        {
            "_id": cart.id,
            "userId": cart.user_id,
            "items": [
                {
                    "productId": item.product_id,
                    "nombre": item.nombre,
                    "precio": item.precio,
                    "imagen": item.imagen,
                    "cantidad": item.cantidad,
                }
                for item in cart.items
            ],
            "total": cart.total,
        }
    )


@router.get("", response_model=CartPublic)
def get_cart(
    current: CurrentUser = Depends(get_current_user),
    service: CartService = Depends(_service),
) -> CartPublic:
    cart = service.get_cart(current.id)
    return _to_public(cart)


@router.post("/add", response_model=CartResponse)
def add_to_cart(
    payload: AddToCartRequest,
    current: CurrentUser = Depends(get_current_user),
    service: CartService = Depends(_service),
) -> CartResponse:
    cart = service.add_item(
        user_id=current.id,
        product_id=payload.product_id,
        cantidad=payload.cantidad,
    )
    return CartResponse(message="Producto añadido al carrito", cart=_to_public(cart))


@router.put("/update", response_model=CartResponse)
def update_cart_item(
    payload: UpdateCartItemRequest,
    current: CurrentUser = Depends(get_current_user),
    service: CartService = Depends(_service),
) -> CartResponse:
    cart = service.update_item(
        user_id=current.id,
        product_id=payload.product_id,
        cantidad=payload.cantidad,
    )
    return CartResponse(message="Carrito actualizado", cart=_to_public(cart))


@router.delete("/clear", response_model=CartResponse)
def clear_cart(
    current: CurrentUser = Depends(get_current_user),
    service: CartService = Depends(_service),
) -> CartResponse:
    cart = service.clear(user_id=current.id)
    return CartResponse(message="Carrito vaciado", cart=_to_public(cart))


@router.delete("/remove/{product_id}", response_model=CartResponse)
def remove_from_cart(
    product_id: str,
    current: CurrentUser = Depends(get_current_user),
    service: CartService = Depends(_service),
) -> CartResponse:
    cart = service.remove_item(user_id=current.id, product_id=product_id)
    return CartResponse(message="Producto eliminado del carrito", cart=_to_public(cart))
