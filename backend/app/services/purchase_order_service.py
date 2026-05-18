from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import resolve_tenant_scope
from app.models.audit_log import AuditLog
from app.models.enums import InventoryTransactionTypeEnum, PurchaseOrderStatusEnum, RecordStatusEnum, RoleEnum
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.user import User
from app.models.vendor import Vendor
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.inventory_repository import InventoryTransactionRepository, WarehouseStockRepository
from app.repositories.master_data_repository import MasterDataRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.purchase_order_repository import PurchaseOrderItemRepository, PurchaseOrderRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.notification_service import NotificationService


class PurchaseOrderService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.purchase_order_repository = PurchaseOrderRepository(db)
        self.item_repository = PurchaseOrderItemRepository(db)
        self.product_repository = ProductRepository(db)
        self.stock_repository = WarehouseStockRepository(db)
        self.transaction_repository = InventoryTransactionRepository(db)
        self.audit_repository = AuditLogRepository(db)
        self.tenant_repository = TenantRepository(db)
        self.vendor_repository = MasterDataRepository(db, Vendor)
        self.warehouse_repository = MasterDataRepository(db, Warehouse)
        self.notification_service = NotificationService(db)

    def list_purchase_orders(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        status_filter: PurchaseOrderStatusEnum | None = None,
        vendor_id: int | None = None,
        date_from=None,
        date_to=None,
        search: str | None = None,
    ) -> tuple[list[PurchaseOrder], int]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        return self.purchase_order_repository.list(
            page=page,
            page_size=page_size,
            tenant_id=scoped_tenant_id,
            status_filter=status_filter,
            vendor_id=vendor_id,
            date_from=date_from,
            date_to=date_to,
            search=search,
        )

    def get_purchase_order_for_user(self, *, current_user: User, purchase_order_id: int) -> tuple[PurchaseOrder, list[PurchaseOrderItem]]:
        purchase_order = self.purchase_order_repository.get_by_id(purchase_order_id)
        if not purchase_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found.")
        if current_user.role != RoleEnum.SUPER_ADMIN and purchase_order.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-tenant access is not allowed.")
        items = self.item_repository.list_by_purchase_order(purchase_order.id)
        return purchase_order, items

    def create_purchase_order(self, *, current_user: User, payload, tenant_id: int | None = None) -> tuple[PurchaseOrder, list[PurchaseOrderItem]]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=True)
        self._validate_tenant_exists(scoped_tenant_id)
        self._ensure_unique_po_number(tenant_id=scoped_tenant_id, po_number=payload.po_number)
        self._validate_vendor(tenant_id=scoped_tenant_id, vendor_id=payload.vendor_id)
        items_data = self._validate_items(tenant_id=scoped_tenant_id, items=payload.items)
        totals = self._build_order_totals(items_data)

        purchase_order = self.purchase_order_repository.create(
            PurchaseOrder(
                tenant_id=scoped_tenant_id,
                vendor_id=payload.vendor_id,
                po_number=payload.po_number,
                order_date=payload.order_date,
                expected_delivery_date=payload.expected_delivery_date,
                status=PurchaseOrderStatusEnum.DRAFT,
                subtotal=totals["subtotal"],
                tax_amount=totals["tax_amount"],
                total_amount=totals["total_amount"],
                notes=payload.notes,
                created_by=current_user.id,
            )
        )
        items = self.item_repository.create_many(
            [
                PurchaseOrderItem(
                    purchase_order_id=purchase_order.id,
                    product_id=item["product_id"],
                    warehouse_id=item["warehouse_id"],
                    quantity_ordered=item["quantity_ordered"],
                    quantity_received=0,
                    unit_price=item["unit_price"],
                    tax_rate=item["tax_rate"],
                    total_price=item["total_price"],
                )
                for item in items_data
            ]
        )
        self._log_purchase_order_action(
            actor=current_user,
            purchase_order=purchase_order,
            action="purchase_order.created",
            old_value=None,
            new_value=self._purchase_order_snapshot(purchase_order, items),
        )
        self.db.commit()
        return purchase_order, items

    def update_purchase_order(self, *, current_user: User, purchase_order_id: int, payload) -> tuple[PurchaseOrder, list[PurchaseOrderItem]]:
        purchase_order, current_items = self.get_purchase_order_for_user(current_user=current_user, purchase_order_id=purchase_order_id)
        if purchase_order.status != PurchaseOrderStatusEnum.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft purchase orders can be updated.")

        updates = payload.model_dump(exclude_unset=True)
        old_snapshot = self._purchase_order_snapshot(purchase_order, current_items)
        vendor_id = updates.get("vendor_id", purchase_order.vendor_id)
        po_number = updates.get("po_number", purchase_order.po_number)

        self._validate_vendor(tenant_id=purchase_order.tenant_id, vendor_id=vendor_id)
        self._ensure_unique_po_number(tenant_id=purchase_order.tenant_id, po_number=po_number, exclude_id=purchase_order.id)

        if "items" in updates and updates["items"] is not None:
            items_data = self._validate_items(tenant_id=purchase_order.tenant_id, items=updates["items"])
            totals = self._build_order_totals(items_data)
            self.item_repository.delete_for_purchase_order(purchase_order.id)
            current_items = self.item_repository.create_many(
                [
                    PurchaseOrderItem(
                        purchase_order_id=purchase_order.id,
                        product_id=item["product_id"],
                        warehouse_id=item["warehouse_id"],
                        quantity_ordered=item["quantity_ordered"],
                        quantity_received=0,
                        unit_price=item["unit_price"],
                        tax_rate=item["tax_rate"],
                        total_price=item["total_price"],
                    )
                    for item in items_data
                ]
            )
        else:
            totals = {
                "subtotal": purchase_order.subtotal,
                "tax_amount": purchase_order.tax_amount,
                "total_amount": purchase_order.total_amount,
            }

        purchase_order = self.purchase_order_repository.update(
            purchase_order,
            {
                "vendor_id": vendor_id,
                "po_number": po_number,
                "order_date": updates.get("order_date", purchase_order.order_date),
                "expected_delivery_date": updates.get("expected_delivery_date", purchase_order.expected_delivery_date),
                "notes": updates.get("notes", purchase_order.notes),
                "subtotal": totals["subtotal"],
                "tax_amount": totals["tax_amount"],
                "total_amount": totals["total_amount"],
            },
        )
        self._log_purchase_order_action(
            actor=current_user,
            purchase_order=purchase_order,
            action="purchase_order.updated",
            old_value=old_snapshot,
            new_value=self._purchase_order_snapshot(purchase_order, current_items),
        )
        self.db.commit()
        return purchase_order, current_items

    def issue_purchase_order(self, *, current_user: User, purchase_order_id: int, notes: str | None = None) -> tuple[PurchaseOrder, list[PurchaseOrderItem]]:
        purchase_order, items = self.get_purchase_order_for_user(current_user=current_user, purchase_order_id=purchase_order_id)
        if purchase_order.status != PurchaseOrderStatusEnum.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft purchase orders can be issued.")

        old_snapshot = self._purchase_order_snapshot(purchase_order, items)
        purchase_order = self.purchase_order_repository.update(
            purchase_order,
            {
                "status": PurchaseOrderStatusEnum.ISSUED,
                "notes": notes if notes is not None else purchase_order.notes,
            },
        )
        self._log_purchase_order_action(
            actor=current_user,
            purchase_order=purchase_order,
            action="purchase_order.issued",
            old_value=old_snapshot,
            new_value=self._purchase_order_snapshot(purchase_order, items),
        )
        self.db.commit()
        return purchase_order, items

    def cancel_purchase_order(self, *, current_user: User, purchase_order_id: int, notes: str | None = None) -> tuple[PurchaseOrder, list[PurchaseOrderItem]]:
        purchase_order, items = self.get_purchase_order_for_user(current_user=current_user, purchase_order_id=purchase_order_id)
        if purchase_order.status == PurchaseOrderStatusEnum.RECEIVED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Received purchase orders cannot be cancelled.")
        if purchase_order.status == PurchaseOrderStatusEnum.CANCELLED:
            return purchase_order, items

        old_snapshot = self._purchase_order_snapshot(purchase_order, items)
        purchase_order = self.purchase_order_repository.update(
            purchase_order,
            {
                "status": PurchaseOrderStatusEnum.CANCELLED,
                "notes": notes if notes is not None else purchase_order.notes,
            },
        )
        self._log_purchase_order_action(
            actor=current_user,
            purchase_order=purchase_order,
            action="purchase_order.cancelled",
            old_value=old_snapshot,
            new_value=self._purchase_order_snapshot(purchase_order, items),
        )
        self.db.commit()
        return purchase_order, items

    def receive_purchase_order(
        self,
        *,
        current_user: User,
        purchase_order_id: int,
        payload,
        request_meta: dict[str, str | None],
    ) -> tuple[PurchaseOrder, list[PurchaseOrderItem]]:
        purchase_order, items = self.get_purchase_order_for_user(current_user=current_user, purchase_order_id=purchase_order_id)
        if purchase_order.status == PurchaseOrderStatusEnum.CANCELLED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cancelled purchase orders cannot receive stock.")
        if purchase_order.status == PurchaseOrderStatusEnum.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Issue the purchase order before receiving stock.")
        if purchase_order.status == PurchaseOrderStatusEnum.RECEIVED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This purchase order is already fully received.")

        old_snapshot = self._purchase_order_snapshot(purchase_order, items)
        item_map = {item.id: item for item in items}
        receive_quantities: dict[int, int] = {}

        for receive_item in payload.items:
            order_item = item_map.get(receive_item.purchase_order_item_id)
            if order_item is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more purchase order items are invalid.")
            remaining_quantity = order_item.quantity_ordered - order_item.quantity_received
            if receive_item.quantity_received > remaining_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Received quantity cannot exceed the remaining quantity on a purchase order line.",
                )
            receive_quantities[order_item.id] = receive_quantities.get(order_item.id, 0) + receive_item.quantity_received
            if receive_quantities[order_item.id] > remaining_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Combined received quantity cannot exceed the remaining quantity on a purchase order line.",
                )

        for item in items:
            quantity_to_receive = receive_quantities.get(item.id)
            if not quantity_to_receive:
                continue

            product = self._get_active_product(tenant_id=purchase_order.tenant_id, product_id=item.product_id)
            warehouse = self._get_active_warehouse(tenant_id=purchase_order.tenant_id, warehouse_id=item.warehouse_id)
            stock = self._get_or_create_stock(
                tenant_id=purchase_order.tenant_id,
                warehouse_id=warehouse.id,
                product=product,
                lock=True,
            )
            stock_old = self._stock_snapshot(stock)
            self.stock_repository.update(
                stock,
                {
                    "quantity": stock.quantity + quantity_to_receive,
                    "available_quantity": stock.available_quantity + quantity_to_receive,
                },
            )
            item.quantity_received += quantity_to_receive
            self.db.add(item)

            self.transaction_repository.create(
                InventoryTransaction(
                    tenant_id=purchase_order.tenant_id,
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    source_warehouse_id=None,
                    destination_warehouse_id=None,
                    transaction_type=InventoryTransactionTypeEnum.PURCHASE_RECEIVE,
                    quantity=quantity_to_receive,
                    reference_type="purchase_order",
                    reference_id=purchase_order.id,
                    note=payload.notes or purchase_order.notes,
                    created_by=current_user.id,
                )
            )
            self.audit_repository.create(
                AuditLog(
                    tenant_id=purchase_order.tenant_id,
                    user_id=current_user.id,
                    action="inventory.purchase_receive",
                    entity_type="warehouse_stock",
                    entity_id=stock.id,
                    old_value_json=stock_old,
                    new_value_json={
                        "quantity": stock.quantity,
                        "reserved_quantity": stock.reserved_quantity,
                        "available_quantity": stock.available_quantity,
                        "product_id": product.id,
                        "warehouse_id": warehouse.id,
                        "purchase_order_id": purchase_order.id,
                    },
                    ip_address=request_meta.get("ip_address"),
                    user_agent=request_meta.get("user_agent"),
                )
            )

        self.db.flush()
        latest_items = self.item_repository.list_by_purchase_order(purchase_order.id)
        fully_received = all(item.quantity_received >= item.quantity_ordered for item in latest_items)
        purchase_order = self.purchase_order_repository.update(
            purchase_order,
            {
                "status": PurchaseOrderStatusEnum.RECEIVED if fully_received else PurchaseOrderStatusEnum.PARTIALLY_RECEIVED,
                "notes": payload.notes if payload.notes is not None else purchase_order.notes,
            },
        )
        self._log_purchase_order_action(
            actor=current_user,
            purchase_order=purchase_order,
            action="purchase_order.received",
            old_value=old_snapshot,
            new_value=self._purchase_order_snapshot(purchase_order, latest_items),
            request_meta=request_meta,
        )
        self.notification_service.notify_purchase_receive(
            tenant_id=purchase_order.tenant_id,
            po_number=purchase_order.po_number,
            actor_name=current_user.name,
        )
        self.db.commit()
        return purchase_order, latest_items

    def _validate_tenant_exists(self, tenant_id: int) -> None:
        if self.tenant_repository.get_by_id(tenant_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    def _ensure_unique_po_number(self, *, tenant_id: int, po_number: str, exclude_id: int | None = None) -> None:
        if self.purchase_order_repository.find_by_number(tenant_id=tenant_id, po_number=po_number, exclude_id=exclude_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="po_number must be unique within the tenant.")

    def _validate_vendor(self, *, tenant_id: int, vendor_id: int) -> Vendor:
        vendor = self.vendor_repository.get_by_id(vendor_id)
        if not vendor or vendor.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found for this tenant.")
        if vendor.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archived vendors cannot be used in purchase orders.")
        return vendor

    def _validate_items(self, *, tenant_id: int, items: list[Any]) -> list[dict[str, Any]]:
        validated_items: list[dict[str, Any]] = []
        seen_pairs: set[tuple[int, int]] = set()
        for item in items:
            product = self._get_active_product(tenant_id=tenant_id, product_id=item.product_id)
            warehouse = self._get_active_warehouse(tenant_id=tenant_id, warehouse_id=item.warehouse_id)
            pair = (product.id, warehouse.id)
            if pair in seen_pairs:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Each product and warehouse combination may appear only once per purchase order.",
                )
            seen_pairs.add(pair)

            quantity_ordered = int(item.quantity_ordered)
            unit_price = self._quantize(item.unit_price)
            tax_rate = self._quantize(item.tax_rate)
            line_subtotal = self._quantize(unit_price * quantity_ordered)
            tax_amount = self._quantize(line_subtotal * (tax_rate / Decimal("100")))
            total_price = self._quantize(line_subtotal + tax_amount)

            validated_items.append(
                {
                    "product_id": product.id,
                    "warehouse_id": warehouse.id,
                    "quantity_ordered": quantity_ordered,
                    "unit_price": unit_price,
                    "tax_rate": tax_rate,
                    "total_price": total_price,
                }
            )
        return validated_items

    def _build_order_totals(self, items: list[dict[str, Any]]) -> dict[str, Decimal]:
        subtotal = Decimal("0.00")
        tax_amount = Decimal("0.00")
        for item in items:
            line_subtotal = self._quantize(item["unit_price"] * item["quantity_ordered"])
            line_tax = self._quantize(line_subtotal * (item["tax_rate"] / Decimal("100")))
            subtotal += line_subtotal
            tax_amount += line_tax
        subtotal = self._quantize(subtotal)
        tax_amount = self._quantize(tax_amount)
        return {
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "total_amount": self._quantize(subtotal + tax_amount),
        }

    def _purchase_order_snapshot(self, purchase_order: PurchaseOrder, items: list[PurchaseOrderItem]) -> dict[str, Any]:
        return {
            "id": purchase_order.id,
            "tenant_id": purchase_order.tenant_id,
            "vendor_id": purchase_order.vendor_id,
            "po_number": purchase_order.po_number,
            "order_date": purchase_order.order_date.isoformat(),
            "expected_delivery_date": purchase_order.expected_delivery_date.isoformat() if purchase_order.expected_delivery_date else None,
            "status": purchase_order.status.value,
            "subtotal": str(purchase_order.subtotal),
            "tax_amount": str(purchase_order.tax_amount),
            "total_amount": str(purchase_order.total_amount),
            "notes": purchase_order.notes,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "warehouse_id": item.warehouse_id,
                    "quantity_ordered": item.quantity_ordered,
                    "quantity_received": item.quantity_received,
                    "unit_price": str(item.unit_price),
                    "tax_rate": str(item.tax_rate),
                    "total_price": str(item.total_price),
                }
                for item in items
            ],
        }

    def _log_purchase_order_action(
        self,
        *,
        actor: User,
        purchase_order: PurchaseOrder,
        action: str,
        old_value: dict[str, Any] | None,
        new_value: dict[str, Any] | None,
        request_meta: dict[str, str | None] | None = None,
    ) -> None:
        self.audit_repository.create(
            AuditLog(
                tenant_id=purchase_order.tenant_id,
                user_id=actor.id,
                action=action,
                entity_type="purchase_order",
                entity_id=purchase_order.id,
                old_value_json=old_value,
                new_value_json=new_value,
                ip_address=(request_meta or {}).get("ip_address"),
                user_agent=(request_meta or {}).get("user_agent"),
            )
        )

    def _get_active_product(self, *, tenant_id: int, product_id: int) -> Product:
        product = self.product_repository.get_by_id(product_id)
        if not product or product.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found for this tenant.")
        if product.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archived products cannot be used in purchase orders.")
        return product

    def _get_active_warehouse(self, *, tenant_id: int, warehouse_id: int) -> Warehouse:
        warehouse = self.warehouse_repository.get_by_id(warehouse_id)
        if not warehouse or warehouse.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found for this tenant.")
        if warehouse.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archived warehouses cannot be used in purchase orders.")
        return warehouse

    def _get_or_create_stock(self, *, tenant_id: int, warehouse_id: int, product: Product, lock: bool) -> WarehouseStock:
        stock = self.stock_repository.get_for_update(
            tenant_id=tenant_id,
            product_id=product.id,
            warehouse_id=warehouse_id,
        ) if lock else None
        if stock is None:
            stock = self.stock_repository.create(
                WarehouseStock(
                    tenant_id=tenant_id,
                    product_id=product.id,
                    warehouse_id=warehouse_id,
                    quantity=0,
                    reserved_quantity=0,
                    available_quantity=0,
                    reorder_level=product.reorder_level,
                )
            )
        return stock

    def _stock_snapshot(self, stock: WarehouseStock) -> dict[str, int | None]:
        return {
            "quantity": stock.quantity,
            "reserved_quantity": stock.reserved_quantity,
            "available_quantity": stock.available_quantity,
            "reorder_level": stock.reorder_level,
        }

    def _quantize(self, value: Decimal | int | float) -> Decimal:
        return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
