from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class DimDate(Base):
    """날짜 차원 테이블"""
    __tablename__ = "dim_date"
    
    date_key = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    dow = Column(Integer, nullable=False)  # Day of week (1-7)
    
    # 관계
    sales = relationship("FactSales", back_populates="date")

class DimProduct(Base):
    """제품 차원 테이블"""
    __tablename__ = "dim_product"
    
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100), nullable=False, index=True)
    sku = Column(String(50), nullable=False, unique=True, index=True)
    
    # 관계
    sales = relationship("FactSales", back_populates="product")

class DimCustomer(Base):
    """고객 차원 테이블"""
    __tablename__ = "dim_customer"
    
    customer_id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(255), nullable=False)
    segment = Column(String(100), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    
    # 관계
    sales = relationship("FactSales", back_populates="customer")

class FactSales(Base):
    """매출 팩트 테이블"""
    __tablename__ = "fact_sales"
    
    sales_id = Column(Integer, primary_key=True, index=True)
    date_key = Column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("dim_product.product_id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("dim_customer.customer_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    revenue = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="KRW")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    date = relationship("DimDate", back_populates="sales")
    product = relationship("DimProduct", back_populates="sales")
    customer = relationship("DimCustomer", back_populates="sales")
