"""
SQLAlchemy models for the Agnes supplement database.

This module defines ORM models for the 6-table structure:
- Company: Supplement companies
- Product: Products (finished goods + raw materials)
- BOM: Bill of Materials for finished goods
- BOMComponent: Components used in BOMs (M:N relationship)
- Supplier: Suppliers
- SupplierProduct: Product-Supplier mappings (M:N relationship)

The models are designed to work with the existing SQLite database schema
and maintain all existing relationships and constraints.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

# Create the declarative base
Base = declarative_base()


class Company(Base):
    """
    Supplement company model.

    Represents companies that manufacture supplements like Caltrate, Centrum, etc.
    """
    __tablename__ = 'Company'

    Id = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)

    # Relationships
    products = relationship("Product", back_populates="company")

    def __repr__(self):
        return f"<Company(Id={self.Id}, Name='{self.Name}')>"


class Product(Base):
    """
    Product model for both finished goods and raw materials.

    Contains SKUs following the pattern:
    RM-C{company_id}-{substance}-{variant}-{hash}
    Example: RM-C1-vitamin-d3-cholecalciferol-1000iu-15a7d2b1
    """
    __tablename__ = 'Product'

    Id = Column(Integer, primary_key=True)
    SKU = Column(String, nullable=False)
    CompanyId = Column(Integer, ForeignKey('Company.Id'), nullable=False)
    Type = Column(String, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="products")

    # BOM relationships
    produced_by_boms = relationship("BOM", back_populates="produced_product")
    consumed_in_bom_components = relationship("BOMComponent", back_populates="consumed_product")

    # Supplier relationships
    supplier_products = relationship("SupplierProduct", back_populates="product")

    def __repr__(self):
        return f"<Product(Id={self.Id}, SKU='{self.SKU}', Type='{self.Type}')>"


class BOM(Base):
    """
    Bill of Materials model.

    Represents the production recipe for finished goods, linking a produced
    product to its component raw materials.
    """
    __tablename__ = 'BOM'

    Id = Column(Integer, primary_key=True)
    ProducedProductId = Column(Integer, ForeignKey('Product.Id'), nullable=False)

    # Relationships
    produced_product = relationship("Product", back_populates="produced_by_boms")
    components = relationship("BOMComponent", back_populates="bom")

    def __repr__(self):
        return f"<BOM(Id={self.Id}, ProducedProductId={self.ProducedProductId})>"


class BOMComponent(Base):
    """
    BOM Component model (M:N relationship between BOM and consumed Products).

    Links a BOM to the raw material products it consumes.
    Composite primary key of (BOMId, ConsumedProductId).
    """
    __tablename__ = 'BOM_Component'

    BOMId = Column(Integer, ForeignKey('BOM.Id'), primary_key=True, nullable=False)
    ConsumedProductId = Column(Integer, ForeignKey('Product.Id'), primary_key=True, nullable=False)

    # Relationships
    bom = relationship("BOM", back_populates="components")
    consumed_product = relationship("Product", back_populates="consumed_in_bom_components")

    def __repr__(self):
        return f"<BOMComponent(BOMId={self.BOMId}, ConsumedProductId={self.ConsumedProductId})>"


class Supplier(Base):
    """
    Supplier model.

    Represents suppliers that provide raw materials and products.
    """
    __tablename__ = 'Supplier'

    Id = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)

    # Relationships
    supplier_products = relationship("SupplierProduct", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(Id={self.Id}, Name='{self.Name}')>"


class SupplierProduct(Base):
    """
    Supplier-Product mapping model (M:N relationship).

    Links suppliers to the products they supply.
    Composite primary key of (SupplierId, ProductId).
    """
    __tablename__ = 'Supplier_Product'

    SupplierId = Column(Integer, ForeignKey('Supplier.Id'), primary_key=True, nullable=False)
    ProductId = Column(Integer, ForeignKey('Product.Id'), primary_key=True, nullable=False)

    # Relationships
    supplier = relationship("Supplier", back_populates="supplier_products")
    product = relationship("Product", back_populates="supplier_products")

    def __repr__(self):
        return f"<SupplierProduct(SupplierId={self.SupplierId}, ProductId={self.ProductId})>"