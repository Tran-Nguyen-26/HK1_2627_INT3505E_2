-- Dump Cơ sở dữ liệu SQLite cho Bài tập 1
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    amount REAL DEFAULT 0.0,
    status TEXT DEFAULT 'pending'
);

INSERT INTO orders (id, title, author, amount, status) VALUES 
(1, 'Clean Code', 'Robert C. Martin', 45.0, 'completed'),
(2, 'Clean Architecture', 'Robert C. Martin', 50.0, 'completed'),
(3, '1984', 'Orwell', 25.0, 'pending'),
(4, 'Animal Farm', 'Orwell', 20.0, 'shipped');