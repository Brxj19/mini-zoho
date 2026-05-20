from __future__ import annotations

import logging
from io import BytesIO
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
logger = logging.getLogger(__name__)


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
        return self._html_to_pdf(
            html,
            fallback_title=f"Invoice {invoice.invoice_number}",
            counterpart_name=customer.name if customer else "Customer",
            document_meta=[
                ("Invoice Number", invoice.invoice_number),
                ("Invoice Date", str(invoice.invoice_date)),
                ("Due Date", str(invoice.due_date or "-")),
                ("Sales Order", sales_order.so_number if sales_order else "-"),
            ],
            line_headers=["Item", "Warehouse", "Qty", "Rate", "Tax", "Amount"],
            line_rows=[
                [
                    str(item["product_name"]),
                    str(item["warehouse_name"]),
                    str(item["quantity"]),
                    str(item["unit_price"]),
                    f'{item["tax_rate"]}%',
                    str(item["total_price"]),
                ]
                for item in item_rows
            ],
            totals=[
                ("Subtotal", str(invoice.subtotal)),
                ("Tax", str(invoice.tax_amount)),
                ("Discount", str(invoice.discount_amount)),
                ("Total", str(invoice.total_amount)),
            ],
            notes=invoice.notes,
            tenant=tenant,
        )

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
        return self._html_to_pdf(
            html,
            fallback_title=f"Bill {bill.bill_number}",
            counterpart_name=vendor.name if vendor else "Vendor",
            document_meta=[
                ("Bill Number", bill.bill_number),
                ("Bill Date", str(bill.bill_date)),
                ("Due Date", str(bill.due_date or "-")),
                ("Purchase Order", purchase_order.po_number if purchase_order else "-"),
            ],
            line_headers=["Item", "Warehouse", "Qty", "Rate", "Tax", "Amount"],
            line_rows=[
                [
                    str(item["product_name"]),
                    str(item["warehouse_name"]),
                    str(item["quantity_ordered"]),
                    str(item["unit_price"]),
                    f'{item["tax_rate"]}%',
                    str(item["total_price"]),
                ]
                for item in item_rows
            ],
            totals=[
                ("Subtotal", str(bill.subtotal)),
                ("Tax", str(bill.tax_amount)),
                ("Total", str(bill.total_amount)),
            ],
            notes=bill.notes,
            tenant=tenant,
        )

    def _html_to_pdf(
        self,
        html: str,
        *,
        fallback_title: str,
        counterpart_name: str,
        document_meta: list[tuple[str, str]],
        line_headers: list[str],
        line_rows: list[list[str]],
        totals: list[tuple[str, str]],
        notes: str | None,
        tenant: Tenant,
    ) -> bytes:
        try:
            from weasyprint import HTML

            return HTML(string=html).write_pdf()
        except Exception as exc:
            logger.warning("weasyprint_unavailable_using_reportlab_fallback error=%s", exc)
            return self._fallback_pdf(
                title=fallback_title,
                counterpart_name=counterpart_name,
                document_meta=document_meta,
                line_headers=line_headers,
                line_rows=line_rows,
                totals=totals,
                notes=notes,
                tenant=tenant,
            )

    def _fallback_pdf(
        self,
        *,
        title: str,
        counterpart_name: str,
        document_meta: list[tuple[str, str]],
        line_headers: list[str],
        line_rows: list[list[str]],
        totals: list[tuple[str, str]],
        notes: str | None,
        tenant: Tenant,
    ) -> bytes:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=16 * mm,
            rightMargin=16 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
        )

        styles = getSampleStyleSheet()
        story = [
            Paragraph(f"<b>{tenant.company_name}</b>", styles["Title"]),
            Paragraph(tenant.contact_email, styles["Normal"]),
        ]

        if tenant.phone:
            story.append(Paragraph(tenant.phone, styles["Normal"]))
        if tenant.address:
            story.append(Paragraph(tenant.address, styles["Normal"]))

        story.extend(
            [
                Spacer(1, 10),
                Paragraph(f"<b>{title}</b>", styles["Heading2"]),
                Paragraph(f"<b>For:</b> {counterpart_name}", styles["Normal"]),
            ]
        )

        for label, value in document_meta:
            story.append(Paragraph(f"<b>{label}:</b> {value}", styles["Normal"]))

        story.append(Spacer(1, 12))

        table_data = [line_headers, *line_rows] if line_rows else [line_headers, ["—"] + [""] * (len(line_headers) - 1)]
        line_table = Table(table_data, repeatRows=1)
        line_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2ff")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(line_table)
        story.append(Spacer(1, 12))

        totals_table = Table([[label, value] for label, value in totals], colWidths=[90 * mm, 35 * mm])
        totals_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("LINEABOVE", (0, -1), (-1, -1), 0.75, colors.HexColor("#9ca3af")),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(totals_table)

        if notes:
            story.extend([Spacer(1, 10), Paragraph("<b>Notes</b>", styles["Heading4"]), Paragraph(notes, styles["BodyText"])])

        document.build(story)
        return buffer.getvalue()

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
