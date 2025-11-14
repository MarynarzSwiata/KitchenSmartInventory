from fastapi import Depends
from sqlmodel import Session, select, func
from typing import Optional
from database import get_session
from models import Product


class ProductService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def create_product(self, product_data: Product) -> Product:
        self.session.add(product_data)
        self.session.commit()
        self.session.refresh(product_data)
        return product_data

    def get_all_products(
        self,
        name: Optional[str] = None,
        brand: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> dict:
        # Build two separate queries with shared filters
        items_query = select(Product)
        count_query = select(func.count()).select_from(Product)

        # Apply filters to both queries
        if name is not None:
            filter_name = Product.name.ilike(f"%{name}%")  # type: ignore
            items_query = items_query.where(filter_name)
            count_query = count_query.where(filter_name)

        if brand is not None:
            filter_brand = Product.brand.ilike(f"%{brand}%")  # type: ignore
            items_query = items_query.where(filter_brand)
            count_query = count_query.where(filter_brand)

        # Execute optimized count query (no subquery)
        total = self.session.exec(count_query).one()

        # Apply pagination and execute items query
        items_query = items_query.offset(offset).limit(limit)
        items = self.session.exec(items_query).all()

        return {"total": total, "items": list(items)}
