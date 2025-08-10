-- AKeeON-T SNoP 매출 데이터 스키마
-- PostgreSQL

-- 날짜 차원 테이블
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    week INTEGER NOT NULL,
    dow INTEGER NOT NULL -- Day of week (1-7, 1=월요일)
);

-- 제품 차원 테이블
CREATE TABLE IF NOT EXISTS dim_product (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE
);

-- 고객 차원 테이블
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    segment VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL
);

-- 매출 팩트 테이블
CREATE TABLE IF NOT EXISTS fact_sales (
    sales_id INTEGER PRIMARY KEY,
    date_key INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    revenue DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'KRW',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_fact_sales_date_key ON fact_sales(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product_id ON fact_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_customer_id ON fact_sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_created_at ON fact_sales(created_at);

CREATE INDEX IF NOT EXISTS idx_dim_date_date ON dim_date(date);
CREATE INDEX IF NOT EXISTS idx_dim_date_year ON dim_date(year);
CREATE INDEX IF NOT EXISTS idx_dim_date_quarter ON dim_date(quarter);
CREATE INDEX IF NOT EXISTS idx_dim_date_month ON dim_date(month);

CREATE INDEX IF NOT EXISTS idx_dim_product_category ON dim_product(category);
CREATE INDEX IF NOT EXISTS idx_dim_product_subcategory ON dim_product(subcategory);
CREATE INDEX IF NOT EXISTS idx_dim_product_sku ON dim_product(sku);

CREATE INDEX IF NOT EXISTS idx_dim_customer_segment ON dim_customer(segment);
CREATE INDEX IF NOT EXISTS idx_dim_customer_region ON dim_customer(region);

-- 뷰 생성 (자주 사용되는 조인)
CREATE OR REPLACE VIEW v_sales_summary AS
SELECT 
    f.sales_id,
    d.date,
    d.year,
    d.quarter,
    d.month,
    d.week,
    p.product_name,
    p.category,
    p.subcategory,
    p.sku,
    c.customer_name,
    c.segment,
    c.region,
    f.quantity,
    f.unit_price,
    f.revenue,
    f.currency
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_customer c ON f.customer_id = c.customer_id;

-- 채팅 기록 테이블
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    message_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    message_type VARCHAR(10) NOT NULL CHECK (message_type IN ('user', 'ai')),
    content TEXT NOT NULL,
    sql_query TEXT,
    execution_time DECIMAL(10,3),
    cached BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
);

-- 채팅 관련 인덱스
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at);

-- 권한 설정
GRANT SELECT ON ALL TABLES IN SCHEMA public TO PUBLIC;
GRANT SELECT ON v_sales_summary TO PUBLIC;
GRANT INSERT, UPDATE, DELETE ON chat_sessions TO PUBLIC;
GRANT INSERT, UPDATE, DELETE ON chat_messages TO PUBLIC;
