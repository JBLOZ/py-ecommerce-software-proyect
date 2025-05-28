CREATE DATABASE IF NOT EXISTS ecommerce;
USE ecommerce;

CREATE TABLE IF NOT EXISTS category (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    price DECIMAL(10, 2),
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES category(id)
);

INSERT INTO category (id, name) VALUES 
    (1, 'Camisetas'),
    (2, 'Teléfonos'),
    (3, 'Pantalones'),
    (4, 'Zapatos'),
    (5, 'Portátiles'),
    (6, 'Otros');

INSERT INTO product (name, description, category_id, price) VALUES 
    ('Camiseta deportiva azul', 'Camiseta deportiva de color azul, talla M', 1, 19.99),
    ('Camiseta blanca básica', 'Camiseta de algodón color blanco, talla L', 1, 15.99),
    ('Camiseta running pro', 'Camiseta técnica transpirable para running, talla S', 1, 24.99),
    ('Camiseta estampada verano', 'Camiseta con estampado floral, talla XL', 1, 17.99),
    ('Camiseta manga larga', 'Camiseta de manga larga para entretiempo, talla M', 1, 21.99),
    ('Smartphone XY123', 'Teléfono móvil de gama media con 64GB de almacenamiento', 2, 299.99),
    ('Teléfono Omega', 'Teléfono móvil de alta gama con cámara 108MP', 2, 799.99),
    ('Smartphone Mini', 'Teléfono compacto, 32GB, batería de larga duración', 2, 199.99),
    ('Smartphone Ultra', 'Pantalla AMOLED, 256GB, 5G', 2, 999.99),
    ('Teléfono Classic', 'Teléfono sencillo para personas mayores', 2, 89.99),
    ('Pantalones vaqueros', 'Jeans de corte recto, talla 32', 3, 49.99),
    ('Pantalones cortos deportivos', 'Shorts deportivos, talla M', 3, 29.99),
    ('Pantalón chino beige', 'Pantalón chino color beige, talla 40', 3, 39.99),
    ('Pantalón cargo', 'Pantalón cargo con bolsillos, talla L', 3, 44.99),
    ('Pantalón de vestir', 'Pantalón elegante para ocasiones formales, talla 38', 3, 59.99),
    ('Zapatillas Running X', 'Zapatos deportivos para correr, talla 40', 4, 59.99),
    ('Zapatillas Running Pro', 'Zapatos deportivos para correr, talla 42', 4, 69.99),
    ('Tenis Casual Modelo X', 'Zapatos casuales unisex, talla 40', 4, 49.99),
    ('Zapatos de vestir negros', 'Zapatos de piel para traje, talla 43', 4, 89.99),
    ('Botas montaña', 'Botas impermeables para senderismo, talla 41', 4, 109.99),
    ('Ordenador Ultraligera 14"', 'Portátil ultraligero con 8GB RAM, 256GB SSD', 5, 1099.99),
    ('Notebook Gamer Z5', 'Portátil con GPU dedicada, 16GB RAM', 5, 1599.99),
    ('Portátil convertible', 'Pantalla táctil, 2 en 1, 512GB SSD', 5, 1299.99),
    ('Portátil profesional', 'Procesador i7, 32GB RAM, 1TB SSD', 5, 1899.99),
    ('Mini laptop', 'Portátil compacto para viajes, 4GB RAM', 5, 499.99),
    ('Tarjeta de Regalo', 'Tarjeta de regalo electrónica válida en tienda', 6, 50.00),
    ('Auriculares Bluetooth', 'Auriculares inalámbricos con cancelación de ruido', 6, 79.99),
    ('Mochila urbana', 'Mochila resistente al agua, 20L', 6, 39.99),
    ('Gorra deportiva', 'Gorra transpirable para actividades al aire libre', 6, 14.99),
    ('Cinturón de piel', 'Cinturón clásico color marrón', 6, 24.99),
    ('Zapatos deportivos azul', 'Zapatos para correr de color azul, talla 42', 4, 74.99),
    ('Portátil Azul', 'Ordenador portátil color azul, 8GB RAM', 5, 899.99),
    ('Pantalón azul', 'Pantalón de vestir color azul, talla 40', 3, 54.99),
    ('Camiseta Classic', 'Camiseta modelo Classic, talla L', 1, 18.99),
    ('Teléfono Classic', 'Teléfono móvil modelo Classic, 64GB', 2, 159.99),
    ('Zapatos Classic', 'Zapatos de vestir modelo Classic, talla 43', 4, 99.99),
    ('Portátil Classic', 'Portátil modelo Classic, 16GB RAM', 5, 1299.99),
    ('Pantalón Classic', 'Pantalón modelo Classic, talla 38', 3, 44.99);