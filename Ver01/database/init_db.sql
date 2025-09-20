-- YMV 비즈니스 관리 시스템 데이터베이스 스키마
-- PostgreSQL/Supabase 용

-- 1. 사용자 및 권한 관리
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    position VARCHAR(50),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    is_master BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_permissions (
    permission_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    menu_name VARCHAR(50) NOT NULL,
    can_access BOOLEAN DEFAULT false,
    can_create BOOLEAN DEFAULT false,
    can_edit BOOLEAN DEFAULT false,
    can_delete BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. 제품 카테고리 (6단계)
CREATE TABLE product_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    category_code VARCHAR(20) UNIQUE NOT NULL,
    category_level INTEGER NOT NULL CHECK (category_level BETWEEN 1 AND 6),
    parent_category_id INTEGER REFERENCES product_categories(category_id),
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. 제품 관리
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_name_en VARCHAR(200),
    product_name_vi VARCHAR(200),
    category_id INTEGER REFERENCES product_categories(category_id),
    description TEXT,
    unit VARCHAR(20) DEFAULT 'EA',
    unit_price DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    supplier_info TEXT,
    specifications TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. 고객 관리
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_code VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Vietnam',
    tax_id VARCHAR(50),
    business_type VARCHAR(100),
    payment_terms INTEGER DEFAULT 30,
    credit_limit DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. 견적서 관리
CREATE TABLE quotations (
    quotation_id SERIAL PRIMARY KEY,
    quotation_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(customer_id),
    quotation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_until DATE,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'approved', 'rejected', 'expired')),
    subtotal DECIMAL(15,2) DEFAULT 0,
    tax_rate DECIMAL(5,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    notes TEXT,
    terms_conditions TEXT,
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE quotation_items (
    item_id SERIAL PRIMARY KEY,
    quotation_id INTEGER REFERENCES quotations(quotation_id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(product_id),
    item_description VARCHAR(500),
    quantity DECIMAL(10,3) NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    line_total DECIMAL(15,2) NOT NULL,
    notes TEXT
);

-- 6. 주문 관리
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    quotation_id INTEGER REFERENCES quotations(quotation_id),
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    delivery_date DATE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')),
    subtotal DECIMAL(15,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    shipping_address TEXT,
    notes TEXT,
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. 구매 관리
CREATE TABLE purchase_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    category_code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE purchases (
    purchase_id SERIAL PRIMARY KEY,
    purchase_number VARCHAR(50) UNIQUE NOT NULL,
    category_id INTEGER REFERENCES purchase_categories(category_id),
    vendor_name VARCHAR(200) NOT NULL,
    purchase_date DATE NOT NULL DEFAULT CURRENT_DATE,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    amount_usd DECIMAL(15,2) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'paid')),
    receipt_file_url TEXT,
    requested_by INTEGER REFERENCES users(user_id),
    approved_by INTEGER REFERENCES users(user_id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. 현금 흐름 관리
CREATE TABLE cash_flows (
    flow_id SERIAL PRIMARY KEY,
    transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    amount_usd DECIMAL(15,2) NOT NULL,
    description TEXT,
    reference_number VARCHAR(100),
    account VARCHAR(100),
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. 월별 예산 관리
CREATE TABLE monthly_budgets (
    budget_id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    category VARCHAR(100) NOT NULL,
    budgeted_amount DECIMAL(15,2) NOT NULL,
    actual_amount DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month, category)
);

-- 10. 환율 관리
CREATE TABLE exchange_rates (
    rate_id SERIAL PRIMARY KEY,
    currency_code VARCHAR(3) NOT NULL,
    rate_to_usd DECIMAL(15,6) NOT NULL,
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(currency_code, effective_date)
);

-- 11. 직원 휴가 관리
CREATE TABLE employee_leaves (
    leave_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    leave_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_count INTEGER NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    approved_by INTEGER REFERENCES users(user_id),
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP WITH TIME ZONE
);

-- 12. 시스템 설정
CREATE TABLE system_settings (
    setting_id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 13. 회사 정보
CREATE TABLE company_info (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    tax_id VARCHAR(50),
    website VARCHAR(255),
    logo_url TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 14. 번역 관리
CREATE TABLE translations (
    translation_id SERIAL PRIMARY KEY,
    language_code VARCHAR(5) NOT NULL,
    translation_key VARCHAR(100) NOT NULL,
    translation_value TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(language_code, translation_key)
);

-- 15. 문서 번호 시퀀스 관리
CREATE TABLE document_sequences (
    sequence_id SERIAL PRIMARY KEY,
    document_type VARCHAR(50) NOT NULL,
    date_prefix VARCHAR(10) NOT NULL,
    last_number INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_type, date_prefix)
);

-- 16. 감사 로그
CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER,
    action VARCHAR(20) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_code ON products(product_code);
CREATE INDEX idx_customers_code ON customers(customer_code);
CREATE INDEX idx_quotations_number ON quotations(quotation_number);
CREATE INDEX idx_quotations_date ON quotations(quotation_date);
CREATE INDEX idx_purchases_date ON purchases(purchase_date);
CREATE INDEX idx_cash_flows_date ON cash_flows(transaction_date);
CREATE INDEX idx_exchange_rates_date ON exchange_rates(effective_date);

-- 기본 데이터 삽입

-- Master 사용자 (비밀번호: 1023, bcrypt 해시)
INSERT INTO users (username, email, password_hash, full_name, department, position, is_master) 
VALUES ('Master', 'master@ymv.com', '$2b$12$xvz.5yK5z5mF5UoJ5tD.Vu7qJ5K5tD.Vu7qJ5K5tD.Vu7qJ5K5tD.', 'System Master', 'IT', 'Administrator', true);

-- 기본 구매 카테고리
INSERT INTO purchase_categories (category_name, category_code, description) VALUES
('사무용품', 'OFFICE', '사무실 운영을 위한 용품'),
('현장용품', 'FIELD', '현장 작업을 위한 용품'),
('기타', 'OTHER', '기타 구매 항목');

-- 기본 환율 (2025년 기준)
INSERT INTO exchange_rates (currency_code, rate_to_usd, effective_date) VALUES
('VND', 0.000041, '2025-01-01'),
('KRW', 0.000769, '2025-01-01'),
('CNY', 0.137931, '2025-01-01'),
('THB', 0.028986, '2025-01-01');

-- 기본 시스템 설정
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('company_currency', 'USD', '기본 통화'),
('tax_rate', '10', '기본 세율 (%)'),
('quotation_validity_days', '30', '견적서 유효 기간 (일)'),
('language_default', 'ko', '기본 언어');

-- 기본 회사 정보
INSERT INTO company_info (company_name, address, phone, email) VALUES
('YMV Company', '베트남 하노이', '+84-xxx-xxx-xxxx', 'info@ymv.com');

-- 기본 번역 데이터
INSERT INTO translations (language_code, translation_key, translation_value) VALUES
('ko', 'dashboard', '대시보드'),
('ko', 'system_management', '시스템 관리'),
('ko', 'customer_management', '고객 관리'),
('ko', 'quotation_management', '견적서 관리'),
('ko', 'purchase_management', '구매 관리'),
('ko', 'cash_flow_management', '현금 흐름 관리'),
('en', 'dashboard', 'Dashboard'),
('en', 'system_management', 'System Management'),
('en', 'customer_management', 'Customer Management'),
('en', 'quotation_management', 'Quotation Management'),
('en', 'purchase_management', 'Purchase Management'),
('en', 'cash_flow_management', 'Cash Flow Management'),
('vi', 'dashboard', 'Bảng điều khiển'),
('vi', 'system_management', 'Quản lý hệ thống'),
('vi', 'customer_management', 'Quản lý khách hàng'),
('vi', 'quotation_management', 'Quản lý báo giá'),
('vi', 'purchase_management', 'Quản lý mua hàng'),
('vi', 'cash_flow_management', 'Quản lý dòng tiền');