"""Router de pedidos."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_admin, get_current_user, get_db
from app.models import Order
from app.schemas.common import MessageResponse
from app.schemas.order import OrderPublic, OrderResponse, OrderStatusUpdate
from app.services import OrderService

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(db)


def _to_public(order: Order) -> OrderPublic:
    return OrderPublic.model_validate(
        {
            "_id": order.id,
            "userId": order.user_id,
            "username": order.username,
            "items": [
                {
                    "productId": item.product_id,
                    "nombre": item.nombre,
                    "precio": item.precio,
                    "cantidad": item.cantidad,
                    "subtotal": item.subtotal,
                }
                for item in order.items
            ],
            "total": order.total,
            "status": order.status.value,
            "createdAt": order.created_at,
            "updatedAt": order.updated_at,
        }
    )


@router.get("", response_model=List[OrderPublic])
def list_all_orders(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    _: CurrentUser = Depends(get_current_admin),
    service: OrderService = Depends(_service),
) -> List[OrderPublic]:
    return [_to_public(o) for o in service.list_orders(status_filter)]


@router.get("/my-orders", response_model=List[OrderPublic])
def list_my_orders(
    current: CurrentUser = Depends(get_current_user),
    service: OrderService = Depends(_service),
) -> List[OrderPublic]:
    return [_to_public(o) for o in service.list_my_orders(current.id)]


@router.get("/{order_id}", response_model=OrderPublic)
def get_order(
    order_id: str,
    current: CurrentUser = Depends(get_current_user),
    service: OrderService = Depends(_service),
) -> OrderPublic:
    order = service.get_order(
        order_id=order_id,
        requester_id=current.id,
        is_admin=current.is_admin,
    )
    return _to_public(order)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    current: CurrentUser = Depends(get_current_user),
    service: OrderService = Depends(_service),
) -> OrderResponse:
    order = service.create_order(user_id=current.id)
    return OrderResponse(message="Pedido creado exitosamente", order=_to_public(order))


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: str,
    payload: OrderStatusUpdate,
    _: CurrentUser = Depends(get_current_admin),
    service: OrderService = Depends(_service),
) -> OrderResponse:
    order = service.update_status(order_id=order_id, status=payload.status)
    return OrderResponse(message="Estado del pedido actualizado", order=_to_public(order))


@router.delete("/{order_id}", response_model=MessageResponse)
def cancel_order(
    order_id: str,
    current: CurrentUser = Depends(get_current_user),
    service: OrderService = Depends(_service),
) -> MessageResponse:
    service.cancel_order(
        order_id=order_id,
        requester_id=current.id,
        requester_role=current.role,
    )
    return MessageResponse(message="Pedido cancelado correctamente")
