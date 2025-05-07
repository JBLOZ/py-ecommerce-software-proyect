CREATE DATABASE IF NOT EXISTS ecommerce;
USE ecommerce;

CREATE TABLE IF NOT EXISTS categories (
    id INT PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2),
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

INSERT INTO categories (id, name) VALUES 
    (1, 'Camisetas'),
    (2, 'Teléfonos'),
    (3, 'Pantalones'),
    (4, 'Zapatos'),
    (5, 'Portátiles'),
    (6, 'Otros');

INSERT INTO products (name, description, category_id, price) VALUES 
    ('Camiseta deportiva azul', 'Camiseta deportiva de color azul, talla M', 1, 19.99),
    ('Camiseta blanca básica', 'Camiseta de algodón color blanco, talla L', 1, 15.99),
    ('Smartphone XY123', 'Teléfono móvil de gama media con 64GB de almacenamiento', 2, 299.99),
    ('Teléfono Omega', 'Teléfono móvil de alta gama con cámara 108MP', 2, 799.99),
    ('Pantalones vaqueros', 'Jeans de corte recto, talla 32', 3, 49.99),
    ('Pantalones cortos deportivos', 'Shorts deportivos, talla M', 3, 29.99),
    ('Zapatillas Running X', 'Zapatos deportivos para correr, talla 40', 4, 59.99),
    ('Zapatillas Running Pro', 'Zapatos deportivos para correr, talla 42', 4, 69.99),
    ('Tenis Casual Modelo X', 'Zapatos casuales unisex, talla 40', 4, 49.99),
    ('Ordenador Ultraligera 14"', 'Portátil ultraligero con 8GB RAM, 256GB SSD', 5, 1099.99),
    ('Notebook Gamer Z5', 'Portátil con GPU dedicada, 16GB RAM', 5, 1599.99),
    ('Tarjeta de Regalo', 'Tarjeta de regalo electrónica válida en tienda', 6, 50.00);