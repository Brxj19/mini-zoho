from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import resolve_tenant_scope
from app.models.enums import InventorySerialStatusEnum, InventoryTransactionTypeEnum, RecordStatusEnum, RoleEnum
from app.models.inventory_batch import InventoryBatch
from app.models.inventory_serial import InventorySerial
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock
from app.repositories.inventory_repository import InventoryTransactionRepository, WarehouseStockRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.tracked_inventory_repository import InventoryBatchRepository, InventorySerialRepository
from app.services.governance_service import GovernanceService
from app.services.inventory_engine import InventoryEngine
from app.services.notification_service import NotificationService


class InventoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.product_repository = ProductRepository(db)
        self.stock_repository = WarehouseStockRepository(db)
        self.transaction_repository = InventoryTransactionRepository(db)
        self.batch_repository = InventoryBatchRepository(db)
        self.serial_repository = InventorySerialRepository(db)
        self.governance_service = GovernanceService(db)
        self.notification_service = NotificationService(db)
        self.inventory_engine = InventoryEngine(db)

    def generate_barcode(self, *, current_user: User) -> str:
        tenant_id = current_user.tenant_id
        if tenant_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A tenant context is required to generate barcodes.")
        self.governance_service.assert_feature_enabled(tenant_id=tenant_id, feature_attr="barcode_enabled", feature_label="Barcode tools")

        while True:
            barcode = f"89{tenant_id:04d}{int(datetime.utcnow().timestamp() * 1000) % 100000000:08d}"
            if not self.product_repository.find_by_barcode(tenant_id=tenant_id, barcode=barcode):
                return barcode

    def search_product_by_barcode(self, *, current_user: User, barcode: str) -> Product:
        tenant_id = current_user.tenant_id
        if tenant_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A tenant context is required to search by barcode.")
        self.governance_service.assert_feature_enabled(tenant_id=tenant_id, feature_attr="barcode_enabled", feature_label="Barcode tools")
        product = self.product_repository.find_by_barcode(tenant_id=tenant_id, barcode=barcode)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No product matches this barcode.")
        return product

    def stock_in(self, *, current_user: User, payload, request_meta: dict[str, str | None]) -> InventoryTransaction:
        product = self._get_product_for_inventory(current_user=current_user, product_id=payload.product_id)
        warehouse = self._get_warehouse_for_inventory(current_user=current_user, warehouse_id=payload.warehouse_id, tenant_id=product.tenant_id)
        self._apply_tracking_for_stock_in(product=product, warehouse=warehouse, payload=payload)
        transaction = self.inventory_engine.stock_in(
            current_user=current_user,
            product=product,
            warehouse=warehouse,
            quantity=payload.quantity,
            note=payload.note,
            reference_type=payload.reference_type,
            reference_id=payload.reference_id,
            request_meta=request_meta,
        )
        self.db.commit()
        return transaction

    def stock_out(self, *, current_user: User, payload, request_meta: dict[str, str | None]) -> InventoryTransaction:
        product = self._get_product_for_inventory(current_user=current_user, product_id=payload.product_id)
        warehouse = self._get_warehouse_for_inventory(current_user=current_user, warehouse_id=payload.warehouse_id, tenant_id=product.tenant_id)
        self._apply_tracking_for_stock_out(product=product, warehouse=warehouse, payload=payload)
        transaction = self.inventory_engine.stock_out(
            current_user=current_user,
            product=product,
            warehouse=warehouse,
            quantity=payload.quantity,
            note=payload.note,
            reference_type=payload.reference_type,
            reference_id=payload.reference_id,
            request_meta=request_meta,
        )
        self.db.commit()
        return transaction

    def adjust_stock(self, *, current_user: User, payload, request_meta: dict[str, str | None]) -> InventoryTransaction:
        if payload.quantity_delta == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="quantity_delta cannot be zero.")
        product = self._get_product_for_inventory(current_user=current_user, product_id=payload.product_id)
        warehouse = self._get_warehouse_for_inventory(current_user=current_user, warehouse_id=payload.warehouse_id, tenant_id=product.tenant_id)
        if product.serial_tracking_enabled or product.batch_tracking_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tracked inventory adjustments must use stock in or stock out so serial and batch ledgers stay consistent.",
            )
        transaction = self.inventory_engine.adjust(
            current_user=current_user,
            product=product,
            warehouse=warehouse,
            signed_qty=payload.quantity_delta,
            note=payload.note,
            reference_type=payload.reference_type,
            reference_id=payload.reference_id,
            request_meta=request_meta,
        )
        self.db.commit()
        return transaction

    def list_transactions(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        product_id: int | None = None,
        warehouse_id: int | None = None,
        transaction_type: InventoryTransactionTypeEnum | None = None,
        created_by: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[InventoryTransaction], int]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        return self.transaction_repository.list(
            page=page,
            page_size=page_size,
            tenant_id=scoped_tenant_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type=transaction_type,
            created_by=created_by,
            date_from=date_from,
            date_to=date_to,
        )

    def list_product_transactions(self, *, current_user: User, product_id: int, page: int, page_size: int) -> tuple[list[InventoryTransaction], int]:
        product = self._get_product_for_inventory(current_user=current_user, product_id=product_id)
        return self.transaction_repository.list_by_product(
            page=page,
            page_size=page_size,
            tenant_id=product.tenant_id,
            product_id=product.id,
        )

    def get_product_stock_breakdown(self, *, current_user: User, product_id: int) -> tuple[Product, dict[str, int], list[WarehouseStock]]:
        product = self._get_product_for_inventory(current_user=current_user, product_id=product_id)
        summary = self.product_repository.get_stock_summary(product_id=product.id, tenant_id=product.tenant_id)
        warehouses = self.stock_repository.list_by_product(tenant_id=product.tenant_id, product_id=product.id)
        return product, summary, warehouses

    def low_stock(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        warehouse_id: int | None = None,
        product_id: int | None = None,
    ):
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        return self.stock_repository.list_low_stock(
            tenant_id=scoped_tenant_id,
            page=page,
            page_size=page_size,
            warehouse_id=warehouse_id,
            product_id=product_id,
        )

    def list_batches(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        product_id: int | None = None,
        warehouse_id: int | None = None,
    ) -> tuple[list[InventoryBatch], int]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        return self.batch_repository.list(
            tenant_id=scoped_tenant_id,
            page=page,
            page_size=page_size,
            product_id=product_id,
            warehouse_id=warehouse_id,
        )

    def list_serials(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        product_id: int | None = None,
        warehouse_id: int | None = None,
        status_filter: InventorySerialStatusEnum | None = None,
    ) -> tuple[list[InventorySerial], int]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        return self.serial_repository.list(
            tenant_id=scoped_tenant_id,
            page=page,
            page_size=page_size,
            product_id=product_id,
            warehouse_id=warehouse_id,
            status_filter=status_filter,
        )

    def _apply_tracking_for_stock_in(self, *, product: Product, warehouse: Warehouse, payload) -> None:
        if product.serial_tracking_enabled or product.batch_tracking_enabled or product.expiry_tracking_enabled or product.warranty_tracking_enabled:
            self.governance_service.assert_feature_enabled(
                tenant_id=product.tenant_id,
                feature_attr="advanced_inventory_enabled",
                feature_label="Advanced inventory tracking",
            )
        if product.batch_tracking_enabled and not payload.batch:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tracked batch items require a batch number for stock in.")
        if product.serial_tracking_enabled and len(payload.serial_numbers) != payload.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tracked serial items require one serial number per received unit.")
        if not product.batch_tracking_enabled and payload.batch:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This product does not use batch tracking.")
        if not product.serial_tracking_enabled and payload.serial_numbers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This product does not use serial tracking.")

        batch = None
        if payload.batch:
            batch = self.batch_repository.get_by_scope(
                tenant_id=product.tenant_id,
                product_id=product.id,
                warehouse_id=warehouse.id,
                batch_number=payload.batch.batch_number,
            )
            if batch is None:
                batch = self.batch_repository.create(
                    InventoryBatch(
                        tenant_id=product.tenant_id,
                        product_id=product.id,
                        warehouse_id=warehouse.id,
                        batch_number=payload.batch.batch_number,
                        expiry_date=payload.batch.expiry_date,
                        warranty_until=payload.batch.warranty_until,
                        quantity=payload.quantity,
                        available_quantity=payload.quantity,
                    )
                )
            else:
                self.batch_repository.update(
                    batch,
                    {
                        "quantity": batch.quantity + payload.quantity,
                        "available_quantity": batch.available_quantity + payload.quantity,
                        "expiry_date": payload.batch.expiry_date or batch.expiry_date,
                        "warranty_until": payload.batch.warranty_until or batch.warranty_until,
                    },
                )

        if payload.serial_numbers:
            serials = []
            for serial_number in payload.serial_numbers:
                if self.serial_repository.get_by_serial(tenant_id=product.tenant_id, serial_number=serial_number):
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Serial number {serial_number} already exists in this tenant.")
                serials.append(
                    InventorySerial(
                        tenant_id=product.tenant_id,
                        product_id=product.id,
                        warehouse_id=warehouse.id,
                        batch_id=batch.id if batch else None,
                        serial_number=serial_number,
                        expires_on=payload.batch.expiry_date if payload.batch else None,
                        warranty_until=payload.batch.warranty_until if payload.batch else None,
                        status=InventorySerialStatusEnum.IN_STOCK,
                    )
                )
            self.serial_repository.create_many(serials)

    def _apply_tracking_for_stock_out(self, *, product: Product, warehouse: Warehouse, payload) -> None:
        if product.serial_tracking_enabled or product.batch_tracking_enabled:
            self.governance_service.assert_feature_enabled(
                tenant_id=product.tenant_id,
                feature_attr="advanced_inventory_enabled",
                feature_label="Advanced inventory tracking",
            )
        if product.batch_tracking_enabled:
            if not payload.batch_number:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tracked batch items require a batch number for stock out.")
            batch = self.batch_repository.get_by_scope(
                tenant_id=product.tenant_id,
                product_id=product.id,
                warehouse_id=warehouse.id,
                batch_number=payload.batch_number,
            )
            if not batch or batch.available_quantity < payload.quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient quantity in the requested batch.")
            self.batch_repository.update(
                batch,
                {
                    "quantity": batch.quantity - payload.quantity,
                    "available_quantity": batch.available_quantity - payload.quantity,
                },
            )
        elif payload.batch_number:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This product does not use batch tracking.")

        if product.serial_tracking_enabled:
            if len(payload.serial_numbers) != payload.quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tracked serial items require one serial number per issued unit.")
            for serial_number in payload.serial_numbers:
                serial = self.serial_repository.get_by_serial(tenant_id=product.tenant_id, serial_number=serial_number)
                if not serial or serial.product_id != product.id or serial.warehouse_id != warehouse.id:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Serial number {serial_number} is not available in this warehouse.")
                if serial.status != InventorySerialStatusEnum.IN_STOCK:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Serial number {serial_number} is not currently available.")
                self.serial_repository.update(serial, {"status": InventorySerialStatusEnum.SOLD})
        elif payload.serial_numbers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This product does not use serial tracking.")

    def _get_product_for_inventory(self, *, current_user: User, product_id: int) -> Product:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
        if current_user.role != RoleEnum.SUPER_ADMIN and product.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-tenant access is not allowed.")
        if product.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archived products cannot be used in stock operations.")
        return product

    def _get_warehouse_for_inventory(self, *, current_user: User, warehouse_id: int, tenant_id: int) -> Warehouse:
        from app.repositories.master_data_repository import MasterDataRepository

        warehouse = MasterDataRepository(self.db, Warehouse).get_by_id(warehouse_id)
        if not warehouse or warehouse.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found for this tenant.")
        if warehouse.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archived warehouses cannot be used in stock operations.")
        return warehouse
