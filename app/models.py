from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, func, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Category(Base):
    __tablename__ = 'Category'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    slug = Column(String, index=True)


class Product(Base):
    __tablename__ = 'Product'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Numeric(10, 2), index=True)
    stock = Column(Integer, index=True)
    image = Column(String)
    categoryId = Column(Integer, ForeignKey('Category.id'))
    orders = relationship("OrderProducts", back_populates="product")


class Order(Base):
    __tablename__ = 'Order'  # Asegurándonos que este es el nombre correcto de la tabla en la base de datos
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(Boolean, default=False, nullable=False)
    orderReadyAt = Column(DateTime(timezone=True), nullable=True)
    chatID = Column(String, nullable=True)
    table = Column(String, nullable=True)
    order_products = relationship("OrderProducts", back_populates="order")


class OrderProducts(Base):
    __tablename__ = 'OrderProducts'
    id = Column(Integer, primary_key=True)
    orderId = Column(Integer, ForeignKey('Order.id'), nullable=False)  # Cambiado de 'orders.id' a 'Order.id'
    productId = Column(Integer, ForeignKey('Product.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    order = relationship("Order", back_populates="order_products")
    product = relationship("Product", back_populates="orders")
