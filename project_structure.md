# 📂 ERP System Project Structure

## Project Root Files
```
├─ .env                          # Environment variables
├─ .evn.example                  # Environment example
├─ .gitignore                    # Git ignore rules
├─ requirements.txt              # Python dependencies
├─ city_mapping.csv              # City mapping data
├─ city_mapping_full.csv         # Full city mapping
├─ Customer List_YUVN_VR02-1.csv # Customer data
├─ customers_20251010.csv        # Customer backup
└─ structure.txt                 # This structure file
```

## Directory Structure

### 📁 .streamlit/
```
└─ secrets.toml                  # Streamlit secrets configuration
```

### 📁 app/
Main application directory

#### Root Level
```
├─ main.py                       # Application entry point
├─ requirements_supabase.txt     # Supabase dependencies
├─ requirements_txt.txt          # Additional requirements
└─ __init__.py                   # Package initializer
```

#### 📁 app/assets/
```
└─ stamp.png                     # Company stamp image
```

#### 📁 app/components/
Business logic components organized by module

##### 📁 components/dashboard/
```
├─ dashboard.py                  # Main dashboard
└─ __init__.py
```

##### 📁 components/finance/
```
├─ expense_management.py         # Expense management (current)
├─ expense_management - 분리 및 승인 개선전.py  # Backup before improvements
├─ expense_management - 완성본 백업.py        # Complete backup
├─ profit_analysis.py            # Profit analysis
├─ reimbursement_management.py   # Reimbursement processing
└─ __init__.py
```

##### 📁 components/hr/
```
├─ employee_management.py        # Employee CRUD
└─ __init__.py
```

##### 📁 components/inventory/
```
├─ inventory_management.py       # Stock management
├─ purchase_order_management.py  # Purchase orders
└─ __init__.py
```

##### 📁 components/logistics/
```
├─ delay_reasons_management.py   # Delay tracking
├─ delivery_management.py        # Delivery processing
├─ fsc_rules_management.py       # FSC rules
├─ lead_time_management.py       # Lead time tracking
├─ rate_table_management.py      # Shipping rates
├─ trucking_rules_management.py  # Trucking rules
└─ __init__.py
```

##### 📁 components/product/
```
├─ product_code_management.py    # Product code management
├─ product_management.py         # Product master data
└─ __init__.py
```

##### 📁 components/sales/
```
├─ customer_management.py        # Customer CRUD
├─ quotation_conversion.py       # Quote to order conversion
├─ quotation_management.py       # Quotation management
├─ sales_order_management.py     # Sales order processing
├─ sales_process_dashboard.py   # Sales dashboard
├─ sales_process_main.py         # Sales main process
├─ sales_process_management-백업- 함수 분리전.py  # Backup before refactor
└─ __init__.py
```

##### 📁 components/specifications/
```
├─ customer_section.py           # Customer specs section
├─ gate_section.py               # Gate specs section
├─ hot_runner_order_sheet.py     # Hot runner order form
├─ language_config.py            # Multi-language config
├─ technical_section.py          # Technical specs section
└─ __init__.py
```

##### 📁 components/supplier/
```
├─ supplier_management.py        # Supplier CRUD
└─ __init__.py
```

##### 📁 components/system/
```
├─ code_management.py            # Generic code management
├─ code_management-코드 변경전.py  # Backup before code change
├─ code_management_ui.py         # Code management UI
├─ document_number.py            # Document numbering
├─ multilingual_input.py         # Multi-language input widget
└─ __init__.py
```

#### 📁 app/config/
```
├─ config_constants.py           # System constants
├─ config_init.py                # Config initialization
├─ config_settings.py            # Application settings
└─ __init__.py
```

#### 📁 app/images/
```
└─ Stemp-sign.png               # Signature stamp
```

#### 📁 app/modules/
```
└─ __init__.py                  # Future modules placeholder
```

#### 📁 app/pages/
```
└─ __init__.py                  # Future pages placeholder
```

#### 📁 app/shared/
```
├─ shared_database.py           # Shared database functions
├─ shared_init.py               # Shared initialization
├─ shared_utils.py              # Shared utility functions
└─ __init__.py
```

#### 📁 app/static/css/
```
└─ css_styles.css               # Custom CSS styles
```

#### 📁 app/templates/
```
├─ expense_print_template.html         # Current expense template
├─ expense_print_template - 원본.html   # Original expense template
├─ expense_print_template - 원본-2.html # Original expense template v2
├─ hot_runner_order_template.html      # Hot runner order template
└─ reimbursement_print_template.html   # Reimbursement template
```

#### 📁 app/utils/
```
├─ auth.py                      # Authentication utilities
├─ database.py                  # Database connection & queries
├─ database_logistics.py        # Logistics DB operations
├─ helpers.py                   # Helper functions
├─ html_templates.py            # HTML template generators
├─ init.py                      # Utils initialization
└─ language_config.py           # Language configuration
```

### 📁 data/
```
├─ employees.json               # Employee data backup
├─ expenses.json                # Expense data backup
└─ purchases.json               # Purchase data backup
```

### 📁 exports/
```
(Empty - For export files)
```

### 📁 fonts/
```
(Empty - For custom fonts)
```

### 📁 logs/
```
(Empty - For application logs)
```

### 📁 tests/
```
(Empty - For test files)
```

### 📁 uploads/
```
(Empty - For file uploads)
```

---

## 🔑 Key Components Summary

### Database Layer
- `app/utils/database.py` - Main DB connection
- `app/utils/database_logistics.py` - Logistics-specific DB

### Business Logic
- `app/components/product/` - Product & Code management
- `app/components/sales/` - Sales process
- `app/components/finance/` - Financial management
- `app/components/logistics/` - Logistics operations

### System
- `app/components/system/` - System-wide code management
- `app/config/` - Configuration settings
- `app/utils/` - Shared utilities

### UI/Templates
- `app/templates/` - HTML print templates
- `app/static/css/` - Custom styles

---

## 📊 Database Tables Referenced

### Product Management
- `product_codes` - Code templates (7-segment codes)
- `products` - Product master data
- `products_with_codes` - VIEW joining products + codes

### Key Relationships
```
product_codes (id) 1:N products (product_code_id)
     ↓
products_with_codes (VIEW)
```

---

**Last Updated:** October 17, 2025
**Version:** V11 Final