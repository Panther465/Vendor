# StreetEats Connect - Django Backend

A B2B platform connecting street food vendors with verified suppliers for raw materials, packaging, and supplies.

## Project Structure

```
streeteats_backend/
├── manage.py
├── requirements.txt
├── README.md
├── venv/                    # Virtual environment
├── static/                  # Static files (CSS, JS, Images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/               # HTML templates
├── streeteats_backend/      # Main project settings
├── core/                    # Core app (home page, etc.)
├── accounts/                # User authentication
├── suppliers/               # Supplier management
├── orders/                  # Order management
└── quality/                 # Quality assurance
```

## Setup Instructions

1. **Activate Virtual Environment:**
   ```bash
   .\venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Start Development Server:**
   ```bash
   python manage.py runserver
   ```

5. **Access the Application:**
   Open your browser and go to `http://127.0.0.1:8000/`

## Features

- **Home Page**: Landing page with features and testimonials
- **User Authentication**: Login/Signup system
- **Supplier Discovery**: Search and browse suppliers
- **Shopping Cart**: Full-featured cart with quantity controls, delivery options ⭐ **NEW**
- **Order Management**: Order creation and management
- **Quality Assurance**: Quality control and feedback system

## Apps Overview

- **core**: Main landing page and core functionality
- **accounts**: User registration, login, logout
- **suppliers**: Supplier listing, search, and details
- **orders**: Shopping cart, order creation and management
- **quality**: Quality assurance and reporting

## Next Steps

1. Create Django models for each app
2. Implement user authentication system
3. Add supplier search functionality
4. Implement order management system
5. Add quality assurance features
6. Integrate with external APIs (Google Places, Payment gateways)