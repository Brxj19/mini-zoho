from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bill import Bill
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.product import Product
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.tenant import Tenant
from app.models.vendor import Vendor
from app.models.warehouse import Warehouse

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates" / "pdf"


class PdfService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.environment = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_invoice_pdf(self, invoice: Invoice) -> bytes:
        tenant = self._get_tenant(invoice.tenant_id)
        customer = self.db.get(Customer, invoice.customer_id)
        sales_order = self.db.get(SalesOrder, invoice.sales_order_id)
        items = list(
            self.db.scalars(
                select(SalesOrderItem).where(SalesOrderItem.sales_order_id == invoice.sales_order_id)
            ).all()
        )
        item_rows = self._build_sales_item_rows(items)
        html = self.environment.get_template("invoice.html").render(
            tenant=tenant,
            invoice=invoice,
            customer=customer,
            sales_order=sales_order,
            items=item_rows,
        )
        return self._html_to_pdf(html)

    def render_bill_pdf(self, bill: Bill) -> bytes:
        tenant = self._get_tenant(bill.tenant_id)
        vendor = self.db.get(Vendor, bill.vendor_id)
        purchase_order = self.db.get(PurchaseOrder, bill.purchase_order_id)
        items = list(
            self.db.scalars(
                select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == bill.purchase_order_id)
            ).all()
        )
        item_rows = self._build_purchase_item_rows(items)
        html = self.environment.get_template("bill.html").render(
            tenant=tenant,
            bill=bill,
            vendor=vendor,
            purchase_order=purchase_order,
            items=item_rows,
        )
        return self._html_to_pdf(html)

    def _html_to_pdf(self, html: str) -> bytes:
        from weasyprint import HTML

        return HTML(string=html).write_pdf()

    def _get_tenant(self, tenant_id: int) -> Tenant:
        tenant = self.db.get(Tenant, tenant_id)
        if not tenant:
            raise ValueError("Tenant not found for PDF generation.")
        return tenant

    def _build_sales_item_rows(self, items: list[SalesOrderItem]) -> list[dict]:
        product_map = {
            product.id: product
            for product in self.db.scalars(select(Product).where(Product.id.in_([item.product_id for item in items]))).all()
        } if items else {}
        warehouse_map = {
            warehouse.id: warehouse
            for warehouse in self.db.scalars(select(Warehouse).where(Warehouse.id.in_([item.warehouse_id for item in items]))).all()
        } if items else {}
        return [
            {
                "product_name": product_map.get(item.product_id).name if product_map.get(item.product_id) else f"Product #{item.product_id}",
                "warehouse_name": warehouse_map.get(item.warehouse_id).name if warehouse_map.get(item.warehouse_id) else f"Warehouse #{item.warehouse_id}",
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "tax_rate": item.tax_rate,
                "total_price": item.total_price,
            }
            for item in items
        ]

    def _build_purchase_item_rows(self, items: list[PurchaseOrderItem]) -> list[dict]:
        product_map = {
            product.id: product
            for product in self.db.scalars(select(Product).where(Product.id.in_([item.product_id for item in items]))).all()
        } if items else {}
        warehouse_map = {
            warehouse.id: warehouse
            for warehouse in self.db.scalars(select(Warehouse).where(Warehouse.id.in_([item.warehouse_id for item in items]))).all()
        } if items else {}
        return [
            {
                "product_name": product_map.get(item.product_id).name if product_map.get(item.product_id) else f"Product #{item.product_id}",
                "warehouse_name": warehouse_map.get(item.warehouse_id).name if warehouse_map.get(item.warehouse_id) else f"Warehouse #{item.warehouse_id}",
                "quantity_ordered": item.quantity_ordered,
                "unit_price": item.unit_price,
                "tax_rate": item.tax_rate,
                "total_price": item.total_price,
            }
            for item in items
        ]
