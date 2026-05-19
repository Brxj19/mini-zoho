from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.core.dependencies import resolve_tenant_scope
from app.models.audit_log import AuditLog
from app.models.bill import Bill
from app.models.customer import Customer
from app.models.enums import (
    BillStatusEnum,
    InventoryTransactionTypeEnum,
    InvoiceStatusEnum,
    PackageStatusEnum,
    PurchaseOrderStatusEnum,
    PurchaseReceiveStatusEnum,
    RecordStatusEnum,
    RoleEnum,
    SalesOrderStatusEnum,
    SalesReturnStatusEnum,
)
from app.models.inventory_transaction import InventoryTransaction
from app.models.invoice import Invoice
from app.models.package import Package
from app.models.package_item import PackageItem
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.purchase_receive import PurchaseReceive
from app.models.purchase_receive_item import PurchaseReceiveItem
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.sales_return import SalesReturn
from app.models.sales_return_item import SalesReturnItem
from app.models.user import User
from app.models.vendor import Vendor
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock


class BusinessWorkflowService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_packages(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        status_filter: PackageStatusEnum | None = None,
        sales_order_id: int | None = None,
        search: str | None = None,
    ) -> tuple[list[Package], int]:
        stmt = select(Package)
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        stmt = stmt.where(Package.tenant_id == scoped_tenant_id)
        if status_filter:
            stmt = stmt.where(Package.status == status_filter)
        if sales_order_id:
            stmt = stmt.where(Package.sales_order_id == sales_order_id)
        if search:
            stmt = stmt.where(Package.package_number.ilike(f"%{search}%"))
        return self._paginate(stmt.order_by(Package.created_at.desc()), page=page, page_size=page_size)

    def get_package_for_user(self, *, current_user: User, package_id: int) -> tuple[Package, list[PackageItem]]:
        package = self.db.get(Package, package_id)
        self._ensure_record_access(current_user=current_user, record=package, label="Package")
        items = list(self.db.scalars(select(PackageItem).where(PackageItem.package_id == package.id)).all())
        return package, items

    def create_package(self, *, current_user: User, payload, tenant_id: int | None = None) -> tuple[Package, list[PackageItem]]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=True)
        sales_order, order_items = self._get_sales_order_with_items(tenant_id=scoped_tenant_id, sales_order_id=payload.sales_order_id)
        if sales_order.status in {SalesOrderStatusEnum.DRAFT, SalesOrderStatusEnum.CANCELLED}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only active sales orders can be packaged.")
        self._ensure_unique(Package, "package_number", payload.package_number, scoped_tenant_id)

        packaged_quantities = self._existing_package_quantities(sales_order.id)
        order_item_map = {item.id: item for item in order_items}
        items: list[PackageItem] = []

        package = Package(
            tenant_id=scoped_tenant_id,
            sales_order_id=sales_order.id,
            package_number=payload.package_number,
            status=PackageStatusEnum.DRAFT,
            notes=payload.notes,
            created_by=current_user.id,
        )
        self.db.add(package)
        self.db.flush()

        for line in payload.items:
            sales_order_item = order_item_map.get(line.sales_order_item_id)
            if sales_order_item is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more package lines are invalid.")
            remaining = sales_order_item.quantity - packaged_quantities.get(sales_order_item.id, 0)
            if line.quantity > remaining:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pack quantity exceeds remaining shippable quantity on the sales order.")
            item = PackageItem(
                package_id=package.id,
                sales_order_item_id=sales_order_item.id,
                product_id=sales_order_item.product_id,
                warehouse_id=sales_order_item.warehouse_id,
                quantity=line.quantity,
            )
            self.db.add(item)
            items.append(item)

        self.db.commit()
        return package, items

    def transition_package(self, *, current_user: User, package_id: int, next_status: PackageStatusEnum, notes: str | None = None) -> tuple[Package, list[PackageItem]]:
        package, items = self.get_package_for_user(current_user=current_user, package_id=package_id)
        allowed = {
            PackageStatusEnum.DRAFT: {PackageStatusEnum.PACKED, PackageStatusEnum.CANCELLED},
            PackageStatusEnum.PACKED: {PackageStatusEnum.SHIPPED, PackageStatusEnum.CANCELLED},
            PackageStatusEnum.SHIPPED: {PackageStatusEnum.DELIVERED},
        }
        if next_status not in allowed.get(package.status, set()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This package transition is not allowed.")
        package.status = next_status
        if notes is not None:
            package.notes = notes
        self.db.add(package)
        self.db.commit()
        return package, items

    def list_invoices(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        status_filter: InvoiceStatusEnum | None = None,
        customer_id: int | None = None,
        search: str | None = None,
    ) -> tuple[list[Invoice], int]:
        stmt = select(Invoice)
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        stmt = stmt.where(Invoice.tenant_id == scoped_tenant_id)
        if status_filter:
            stmt = stmt.where(Invoice.status == status_filter)
        if customer_id:
            stmt = stmt.where(Invoice.customer_id == customer_id)
        if search:
            stmt = stmt.where(Invoice.invoice_number.ilike(f"%{search}%"))
        return self._paginate(stmt.order_by(Invoice.created_at.desc()), page=page, page_size=page_size)

    def get_invoice_for_user(self, *, current_user: User, invoice_id: int) -> Invoice:
        invoice = self.db.get(Invoice, invoice_id)
        self._ensure_record_access(current_user=current_user, record=invoice, label="Invoice")
        return invoice

    def create_invoice(self, *, current_user: User, payload, tenant_id: int | None = None) -> Invoice:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=True)
        sales_order, _ = self._get_sales_order_with_items(tenant_id=scoped_tenant_id, sales_order_id=payload.sales_order_id)
        if sales_order.status == SalesOrderStatusEnum.CANCELLED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cancelled sales orders cannot be invoiced.")
        self._ensure_unique(Invoice, "invoice_number", payload.invoice_number, scoped_tenant_id)
        invoice = Invoice(
            tenant_id=scoped_tenant_id,
            sales_order_id=sales_order.id,
            customer_id=sales_order.customer_id,
            invoice_number=payload.invoice_number,
            invoice_date=payload.invoice_date,
            due_date=payload.due_date,
            status=InvoiceStatusEnum.DRAFT,
            subtotal=sales_order.subtotal,
            tax_amount=sales_order.tax_amount,
            discount_amount=sales_order.discount_amount,
            total_amount=sales_order.total_amount,
            notes=payload.notes,
            created_by=current_user.id,
        )
        self.db.add(invoice)
        self.db.commit()
        return invoice

    def transition_invoice(self, *, current_user: User, invoice_id: int, next_status: InvoiceStatusEnum, notes: str | None = None) -> Invoice:
        invoice = self.get_invoice_for_user(current_user=current_user, invoice_id=invoice_id)
        allowed = {
            InvoiceStatusEnum.DRAFT: {InvoiceStatusEnum.SENT, InvoiceStatusEnum.VOID},
            InvoiceStatusEnum.SENT: {InvoiceStatusEnum.PAID, InvoiceStatusEnum.VOID},
        }
        if next_status not in allowed.get(invoice.status, set()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This invoice transition is not allowed.")
        invoice.status = next_status
        if notes is not None:
            invoice.notes = notes
        self.db.add(invoice)
        self.db.commit()
        return invoice

    def list_sales_returns(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        status_filter: SalesReturnStatusEnum | None = None,
        customer_id: int | None = None,
        search: str | None = None,
    ) -> tuple[list[SalesReturn], int]:
        stmt = select(SalesReturn)
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        stmt = stmt.where(SalesReturn.tenant_id == scoped_tenant_id)
        if status_filter:
            stmt = stmt.where(SalesReturn.status == status_filter)
        if customer_id:
            stmt = stmt.where(SalesReturn.customer_id == customer_id)
        if search:
            stmt = stmt.where(SalesReturn.return_number.ilike(f"%{search}%"))
        return self._paginate(stmt.order_by(SalesReturn.created_at.desc()), page=page, page_size=page_size)

    def get_sales_return_for_user(self, *, current_user: User, sales_return_id: int) -> tuple[SalesReturn, list[SalesReturnItem]]:
        sales_return = self.db.get(SalesReturn, sales_return_id)
        self._ensure_record_access(current_user=current_user, record=sales_return, label="Sales return")
        items = list(self.db.scalars(select(SalesReturnItem).where(SalesReturnItem.sales_return_id == sales_return.id)).all())
        return sales_return, items

    def create_sales_return(self, *, current_user: User, payload, tenant_id: int | None = None) -> tuple[SalesReturn, list[SalesReturnItem]]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=True)
        sales_order, order_items = self._get_sales_order_with_items(tenant_id=scoped_tenant_id, sales_order_id=payload.sales_order_id)
        if sales_order.status != SalesOrderStatusEnum.DELIVERED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only delivered sales orders can be returned.")
        self._ensure_unique(SalesReturn, "return_number", payload.return_number, scoped_tenant_id)

        already_returned = self._existing_sales_return_quantities(sales_order.id)
        order_item_map = {item.id: item for item in order_items}
        sales_return = SalesReturn(
            tenant_id=scoped_tenant_id,
            sales_order_id=sales_order.id,
            customer_id=sales_order.customer_id,
            return_number=payload.return_number,
            return_date=payload.return_date,
            status=SalesReturnStatusEnum.DRAFT,
            notes=payload.notes,
            created_by=current_user.id,
        )
        self.db.add(sales_return)
        self.db.flush()

        items: list[SalesReturnItem] = []
        for line in payload.items:
            order_item = order_item_map.get(line.sales_order_item_id)
            if order_item is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more sales return lines are invalid.")
            returned = already_returned.get(order_item.id, 0)
            if line.quantity > max(order_item.quantity - returned, 0):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Return quantity exceeds the remaining delivered quantity for a sales order line.")
            warehouse = self._get_active_warehouse(tenant_id=scoped_tenant_id, warehouse_id=line.warehouse_id)
            item = SalesReturnItem(
                sales_return_id=sales_return.id,
                sales_order_item_id=order_item.id,
                product_id=order_item.product_id,
                warehouse_id=warehouse.id,
                quantity=line.quantity,
                reason=line.reason,
                notes=line.notes,
            )
            self.db.add(item)
            items.append(item)

        self.db.commit()
        return sales_return, items

    def receive_sales_return(
        self,
        *,
        current_user: User,
        sales_return_id: int,
        notes: str | None,
        request_meta: dict[str, str | None],
    ) -> tuple[SalesReturn, list[SalesReturnItem]]:
        sales_return, items = self.get_sales_return_for_user(current_user=current_user, sales_return_id=sales_return_id)
        if sales_return.status != SalesReturnStatusEnum.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft sales returns can be received.")

        for item in items:
            product = self._get_active_product(tenant_id=sales_return.tenant_id, product_id=item.product_id)
            if product.serial_tracking_enabled or product.batch_tracking_enabled:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tracked item returns are not yet supported in the first-class returns module.")
            warehouse = self._get_active_warehouse(tenant_id=sales_return.tenant_id, warehouse_id=item.warehouse_id)
            stock = self._get_or_create_stock(tenant_id=sales_return.tenant_id, product=product, warehouse=warehouse)
            old_snapshot = self._stock_snapshot(stock)
            stock.quantity += item.quantity
            stock.available_quantity += item.quantity
            self.db.add(stock)
            self.db.add(
                InventoryTransaction(
                    tenant_id=sales_return.tenant_id,
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    source_warehouse_id=None,
                    destination_warehouse_id=None,
                    transaction_type=InventoryTransactionTypeEnum.RETURN_IN,
                    quantity=item.quantity,
                    reference_type="sales_return",
                    reference_id=sales_return.id,
                    note=notes or sales_return.notes or item.reason,
                    created_by=current_user.id,
                )
            )
            self.db.add(
                AuditLog(
                    tenant_id=sales_return.tenant_id,
                    user_id=current_user.id,
                    action="inventory.return_in",
                    entity_type="warehouse_stock",
                    entity_id=stock.id,
                    old_value_json=old_snapshot,
                    new_value_json=self._stock_snapshot(stock),
                    ip_address=request_meta.get("ip_address"),
                    user_agent=request_meta.get("user_agent"),
                )
            )

        sales_return.status = SalesReturnStatusEnum.RECEIVED
        if notes is not None:
            sales_return.notes = notes
        self.db.add(sales_return)
        self.db.commit()
        return sales_return, items

    def refund_sales_return(self, *, current_user: User, sales_return_id: int, notes: str | None) -> tuple[SalesReturn, list[SalesReturnItem]]:
        sales_return, items = self.get_sales_return_for_user(current_user=current_user, sales_return_id=sales_return_id)
        if sales_return.status != SalesReturnStatusEnum.RECEIVED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only received sales returns can be refunded.")
        sales_return.status = SalesReturnStatusEnum.REFUNDED
        if notes is not None:
            sales_return.notes = notes
        self.db.add(sales_return)
        self.db.commit()
        return sales_return, items

    def cancel_sales_return(self, *, current_user: User, sales_return_id: int, notes: str | None) -> tuple[SalesReturn, list[SalesReturnItem]]:
        sales_return, items = self.get_sales_return_for_user(current_user=current_user, sales_return_id=sales_return_id)
        if sales_return.status != SalesReturnStatusEnum.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft sales returns can be cancelled.")
        sales_return.status = SalesReturnStatusEnum.CANCELLED
        if notes is not None:
            sales_return.notes = notes
        self.db.add(sales_return)
        self.db.commit()
        return sales_return, items

    def list_purchase_receives(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        purchase_order_id: int | None = None,
        vendor_id: int | None = None,
        search: str | None = None,
    ) -> tuple[list[PurchaseReceive], int]:
        stmt = select(PurchaseReceive)
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        stmt = stmt.where(PurchaseReceive.tenant_id == scoped_tenant_id)
        if purchase_order_id:
            stmt = stmt.where(PurchaseReceive.purchase_order_id == purchase_order_id)
        if vendor_id:
            stmt = stmt.where(PurchaseReceive.vendor_id == vendor_id)
        if search:
            stmt = stmt.where(PurchaseReceive.receive_number.ilike(f"%{search}%"))
        return self._paginate(stmt.order_by(PurchaseReceive.created_at.desc()), page=page, page_size=page_size)

    def get_purchase_receive_for_user(self, *, current_user: User, purchase_receive_id: int) -> tuple[PurchaseReceive, list[PurchaseReceiveItem]]:
        purchase_receive = self.db.get(PurchaseReceive, purchase_receive_id)
        self._ensure_record_access(current_user=current_user, record=purchase_receive, label="Purchase receive")
        items = list(self.db.scalars(select(PurchaseReceiveItem).where(PurchaseReceiveItem.purchase_receive_id == purchase_receive.id)).all())
        return purchase_receive, items

    def create_purchase_receive(
        self,
        *,
        current_user: User,
        payload,
        request_meta: dict[str, str | None],
        tenant_id: int | None = None,
    ) -> tuple[PurchaseReceive, list[PurchaseReceiveItem]]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=True)
        purchase_order, order_items = self._get_purchase_order_with_items(tenant_id=scoped_tenant_id, purchase_order_id=payload.purchase_order_id)
        if purchase_order.status == PurchaseOrderStatusEnum.CANCELLED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cancelled purchase orders cannot receive stock.")
        if purchase_order.status == PurchaseOrderStatusEnum.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Issue the purchase order before receiving stock.")
        self._ensure_unique(PurchaseReceive, "receive_number", payload.receive_number, scoped_tenant_id)

        order_item_map = {item.id: item for item in order_items}
        purchase_receive = PurchaseReceive(
            tenant_id=scoped_tenant_id,
            purchase_order_id=purchase_order.id,
            vendor_id=purchase_order.vendor_id,
            receive_number=payload.receive_number,
            received_at=payload.received_at,
            status=PurchaseReceiveStatusEnum.POSTED,
            notes=payload.notes,
            created_by=current_user.id,
        )
        self.db.add(purchase_receive)
        self.db.flush()

        receive_items: list[PurchaseReceiveItem] = []
        requested_quantities: dict[int, int] = {}
        for line in payload.items:
            order_item = order_item_map.get(line.purchase_order_item_id)
            if order_item is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more purchase receipt lines are invalid.")
            remaining = order_item.quantity_ordered - order_item.quantity_received
            requested_quantities[order_item.id] = requested_quantities.get(order_item.id, 0) + line.quantity_received
            if requested_quantities[order_item.id] > remaining:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Received quantity cannot exceed the remaining quantity on a purchase order line.")

            product = self._get_active_product(tenant_id=scoped_tenant_id, product_id=order_item.product_id)
            warehouse = self._get_active_warehouse(tenant_id=scoped_tenant_id, warehouse_id=order_item.warehouse_id)
            stock = self._get_or_create_stock(tenant_id=scoped_tenant_id, product=product, warehouse=warehouse)
            old_snapshot = self._stock_snapshot(stock)
            stock.quantity += line.quantity_received
            stock.available_quantity += line.quantity_received
            self.db.add(stock)
            self.db.add(
                InventoryTransaction(
                    tenant_id=scoped_tenant_id,
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    source_warehouse_id=None,
                    destination_warehouse_id=None,
                    transaction_type=InventoryTransactionTypeEnum.PURCHASE_RECEIVE,
                    quantity=line.quantity_received,
                    reference_type="purchase_receive",
                    reference_id=purchase_receive.id,
                    note=payload.notes or purchase_order.notes,
                    created_by=current_user.id,
                )
            )
            self.db.add(
                AuditLog(
                    tenant_id=scoped_tenant_id,
                    user_id=current_user.id,
                    action="inventory.purchase_receive",
                    entity_type="warehouse_stock",
                    entity_id=stock.id,
                    old_value_json=old_snapshot,
                    new_value_json=self._stock_snapshot(stock),
                    ip_address=request_meta.get("ip_address"),
                    user_agent=request_meta.get("user_agent"),
                )
            )
            order_item.quantity_received += line.quantity_received
            self.db.add(order_item)
            receive_item = PurchaseReceiveItem(
                purchase_receive_id=purchase_receive.id,
                purchase_order_item_id=order_item.id,
                product_id=order_item.product_id,
                warehouse_id=order_item.warehouse_id,
                quantity_received=line.quantity_received,
            )
            self.db.add(receive_item)
            receive_items.append(receive_item)

        latest_items = self._get_purchase_order_items(purchase_order.id)
        fully_received = all(item.quantity_received >= item.quantity_ordered for item in latest_items)
        purchase_order.status = PurchaseOrderStatusEnum.RECEIVED if fully_received else PurchaseOrderStatusEnum.PARTIALLY_RECEIVED
        if payload.notes is not None:
            purchase_order.notes = payload.notes
        self.db.add(purchase_order)
        self.db.commit()
        return purchase_receive, receive_items

    def list_bills(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        tenant_id: int | None = None,
        status_filter: BillStatusEnum | None = None,
        vendor_id: int | None = None,
        search: str | None = None,
    ) -> tuple[list[Bill], int]:
        stmt = select(Bill)
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        stmt = stmt.where(Bill.tenant_id == scoped_tenant_id)
        if status_filter:
            stmt = stmt.where(Bill.status == status_filter)
        if vendor_id:
            stmt = stmt.where(Bill.vendor_id == vendor_id)
        if search:
            stmt = stmt.where(Bill.bill_number.ilike(f"%{search}%"))
        return self._paginate(stmt.order_by(Bill.created_at.desc()), page=page, page_size=page_size)

    def get_bill_for_user(self, *, current_user: User, bill_id: int) -> Bill:
        bill = self.db.get(Bill, bill_id)
        self._ensure_record_access(current_user=current_user, record=bill, label="Bill")
        return bill

    def create_bill(self, *, current_user: User, payload, tenant_id: int | None = None) -> Bill:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=True)
        purchase_order, _ = self._get_purchase_order_with_items(tenant_id=scoped_tenant_id, purchase_order_id=payload.purchase_order_id)
        if purchase_order.status == PurchaseOrderStatusEnum.CANCELLED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cancelled purchase orders cannot be billed.")
        self._ensure_unique(Bill, "bill_number", payload.bill_number, scoped_tenant_id)
        bill = Bill(
            tenant_id=scoped_tenant_id,
            purchase_order_id=purchase_order.id,
            vendor_id=purchase_order.vendor_id,
            bill_number=payload.bill_number,
            bill_date=payload.bill_date,
            due_date=payload.due_date,
            status=BillStatusEnum.DRAFT,
            subtotal=purchase_order.subtotal,
            tax_amount=purchase_order.tax_amount,
            total_amount=purchase_order.total_amount,
            notes=payload.notes,
            created_by=current_user.id,
        )
        self.db.add(bill)
        self.db.commit()
        return bill

    def transition_bill(self, *, current_user: User, bill_id: int, next_status: BillStatusEnum, notes: str | None = None) -> Bill:
        bill = self.get_bill_for_user(current_user=current_user, bill_id=bill_id)
        allowed = {
            BillStatusEnum.DRAFT: {BillStatusEnum.POSTED, BillStatusEnum.VOID},
            BillStatusEnum.POSTED: {BillStatusEnum.PAID, BillStatusEnum.VOID},
        }
        if next_status not in allowed.get(bill.status, set()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This bill transition is not allowed.")
        bill.status = next_status
        if notes is not None:
            bill.notes = notes
        self.db.add(bill)
        self.db.commit()
        return bill

    def _paginate(self, stmt: Select[Any], *, page: int, page_size: int):
        total = self.db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
        rows = list(self.db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all())
        return rows, total

    def _ensure_record_access(self, *, current_user: User, record, label: str) -> None:
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{label} not found.")
        if current_user.role != RoleEnum.SUPER_ADMIN and record.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cross-tenant access is not allowed.")

    def _ensure_unique(self, model, field_name: str, value: str, tenant_id: int) -> None:
        stmt = select(model).where(getattr(model, field_name) == value, model.tenant_id == tenant_id)
        if self.db.scalar(stmt):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{field_name.replace('_', ' ').title()} already exists for this tenant.")

    def _get_sales_order_with_items(self, *, tenant_id: int, sales_order_id: int) -> tuple[SalesOrder, list[SalesOrderItem]]:
        sales_order = self.db.scalar(select(SalesOrder).where(SalesOrder.id == sales_order_id, SalesOrder.tenant_id == tenant_id))
        if not sales_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found.")
        items = list(self.db.scalars(select(SalesOrderItem).where(SalesOrderItem.sales_order_id == sales_order.id)).all())
        return sales_order, items

    def _get_purchase_order_with_items(self, *, tenant_id: int, purchase_order_id: int) -> tuple[PurchaseOrder, list[PurchaseOrderItem]]:
        purchase_order = self.db.scalar(select(PurchaseOrder).where(PurchaseOrder.id == purchase_order_id, PurchaseOrder.tenant_id == tenant_id))
        if not purchase_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase order not found.")
        items = self._get_purchase_order_items(purchase_order.id)
        return purchase_order, items

    def _get_purchase_order_items(self, purchase_order_id: int) -> list[PurchaseOrderItem]:
        return list(self.db.scalars(select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == purchase_order_id)).all())

    def _existing_package_quantities(self, sales_order_id: int) -> dict[int, int]:
        rows = self.db.execute(
            select(PackageItem.sales_order_item_id, func.coalesce(func.sum(PackageItem.quantity), 0))
            .join(Package, Package.id == PackageItem.package_id)
            .where(Package.sales_order_id == sales_order_id, Package.status != PackageStatusEnum.CANCELLED)
            .group_by(PackageItem.sales_order_item_id)
        ).all()
        return {item_id: int(quantity or 0) for item_id, quantity in rows}

    def _existing_sales_return_quantities(self, sales_order_id: int) -> dict[int, int]:
        rows = self.db.execute(
            select(SalesReturnItem.sales_order_item_id, func.coalesce(func.sum(SalesReturnItem.quantity), 0))
            .join(SalesReturn, SalesReturn.id == SalesReturnItem.sales_return_id)
            .where(SalesReturn.sales_order_id == sales_order_id, SalesReturn.status != SalesReturnStatusEnum.CANCELLED)
            .group_by(SalesReturnItem.sales_order_item_id)
        ).all()
        return {item_id: int(quantity or 0) for item_id, quantity in rows}

    def _get_active_product(self, *, tenant_id: int, product_id: int) -> Product:
        product = self.db.scalar(select(Product).where(Product.id == product_id, Product.tenant_id == tenant_id))
        if not product or product.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A referenced product is inactive or missing.")
        return product

    def _get_active_warehouse(self, *, tenant_id: int, warehouse_id: int) -> Warehouse:
        warehouse = self.db.scalar(select(Warehouse).where(Warehouse.id == warehouse_id, Warehouse.tenant_id == tenant_id))
        if not warehouse or warehouse.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A referenced warehouse is inactive or missing.")
        return warehouse

    def _get_or_create_stock(self, *, tenant_id: int, product: Product, warehouse: Warehouse) -> WarehouseStock:
        stock = self.db.scalar(
            select(WarehouseStock).where(
                WarehouseStock.tenant_id == tenant_id,
                WarehouseStock.product_id == product.id,
                WarehouseStock.warehouse_id == warehouse.id,
            )
        )
        if stock is None:
            stock = WarehouseStock(
                tenant_id=tenant_id,
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity=0,
                reserved_quantity=0,
                available_quantity=0,
                reorder_level=product.reorder_level,
            )
            self.db.add(stock)
            self.db.flush()
        return stock

    @staticmethod
    def _stock_snapshot(stock: WarehouseStock) -> dict[str, Any]:
        return {
            "quantity": stock.quantity,
            "reserved_quantity": stock.reserved_quantity,
            "available_quantity": stock.available_quantity,
            "product_id": stock.product_id,
            "warehouse_id": stock.warehouse_id,
        }
