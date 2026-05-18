from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import assert_tenant_access, resolve_tenant_scope
from app.models.brand import Brand
from app.models.category import Category
from app.models.enums import RecordStatusEnum, RoleEnum
from app.models.product import Product
from app.models.user import User
from app.models.vendor import Vendor
from app.repositories.master_data_repository import MasterDataRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.tenant_repository import TenantRepository


class ProductService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ProductRepository(db)
        self.tenant_repository = TenantRepository(db)
        self.category_repository = MasterDataRepository(db, Category)
        self.brand_repository = MasterDataRepository(db, Brand)
        self.vendor_repository = MasterDataRepository(db, Vendor)

    def list_products(
        self,
        *,
        current_user: User,
        page: int,
        page_size: int,
        search: str | None = None,
        status_filter: RecordStatusEnum | None = None,
        category_id: int | None = None,
        brand_id: int | None = None,
        vendor_id: int | None = None,
        tenant_id: int | None = None,
    ) -> tuple[list[Product], int]:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, allow_all_for_super_admin=True)
        return self.repository.list(
            page=page,
            page_size=page_size,
            tenant_id=scoped_tenant_id,
            search=search,
            status_filter=status_filter,
            category_id=category_id,
            brand_id=brand_id,
            vendor_id=vendor_id,
        )

    def get_product_or_404(self, product_id: int) -> Product:
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
        return product

    def get_product_for_user(self, *, current_user: User, product_id: int) -> Product:
        product = self.get_product_or_404(product_id)
        if current_user.role != RoleEnum.SUPER_ADMIN:
            assert_tenant_access(current_user, product.tenant_id)
        return product

    def create_product(self, *, current_user: User, payload, tenant_id: int | None = None) -> Product:
        scoped_tenant_id = resolve_tenant_scope(current_user, tenant_id, require_for_super_admin=True)
        self._validate_tenant_exists(scoped_tenant_id)
        data = payload.model_dump(exclude_none=True)
        data["tenant_id"] = scoped_tenant_id
        self._validate_unique_fields(tenant_id=scoped_tenant_id, data=data)
        self._validate_master_data_refs(tenant_id=scoped_tenant_id, data=data)
        product = Product(**data)
        self.repository.create(product)
        self.db.commit()
        return self.get_product_or_404(product.id)

    def update_product(self, *, current_user: User, product_id: int, payload) -> Product:
        product = self.get_product_for_user(current_user=current_user, product_id=product_id)
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return product
        self._validate_unique_fields(tenant_id=product.tenant_id, data=updates, exclude_id=product.id)
        self._validate_master_data_refs(tenant_id=product.tenant_id, data=updates)
        self.repository.update(product, updates)
        self.db.commit()
        return self.get_product_or_404(product.id)

    def archive_product(self, *, current_user: User, product_id: int) -> Product:
        product = self.get_product_for_user(current_user=current_user, product_id=product_id)
        self.repository.update(product, {"status": RecordStatusEnum.ARCHIVED})
        self.db.commit()
        return self.get_product_or_404(product.id)

    def get_stock_summary(self, *, current_user: User, product_id: int) -> dict:
        product = self.get_product_for_user(current_user=current_user, product_id=product_id)
        return self.repository.get_stock_summary(product_id=product.id, tenant_id=product.tenant_id)

    def _validate_tenant_exists(self, tenant_id: int) -> None:
        if not self.tenant_repository.get_by_id(tenant_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")

    def _validate_unique_fields(self, *, tenant_id: int, data: dict, exclude_id: int | None = None) -> None:
        sku = data.get("sku")
        if sku:
            existing = self.repository.find_by_sku(tenant_id=tenant_id, sku=sku, exclude_id=exclude_id)
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already exists in this tenant.")
        barcode = data.get("barcode")
        if barcode:
            existing = self.repository.find_by_barcode(tenant_id=tenant_id, barcode=barcode, exclude_id=exclude_id)
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Barcode already exists in this tenant.")

    def _validate_master_data_refs(self, *, tenant_id: int, data: dict) -> None:
        self._validate_ref(repository=self.category_repository, ref_id=data.get("category_id"), tenant_id=tenant_id, name="Category")
        self._validate_ref(repository=self.brand_repository, ref_id=data.get("brand_id"), tenant_id=tenant_id, name="Brand")
        self._validate_ref(repository=self.vendor_repository, ref_id=data.get("vendor_id"), tenant_id=tenant_id, name="Vendor")

    def _validate_ref(self, *, repository: MasterDataRepository, ref_id: int | None, tenant_id: int, name: str) -> None:
        if ref_id is None:
            return
        entity = repository.get_by_id(ref_id)
        if not entity or entity.tenant_id != tenant_id or entity.status != RecordStatusEnum.ACTIVE:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} not found for this tenant.")
