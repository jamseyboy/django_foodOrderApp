# Django Food Order App

A modern, RESTful API-based food ordering application built with Django and Django Ninja. This application manages customers, food items, and orders with JWT-based authentication and CORS support.

## 📋 Features

- **Customer Management**: Create and manage customer profiles
- **Food Inventory**: Manage food items with pricing information
- **Order Management**: Create orders, add items, and track order status
- **Order Tracking**: View today's orders organized by customer
- **JWT Authentication**: Secure endpoints with JWT-based authentication
- **REST API**: Full-featured REST API using Django Ninja
- **CORS Support**: Built-in CORS support for cross-origin requests
- **Docker Ready**: Containerized deployment with Docker and Gunicorn
- **Database Flexibility**: Supports both SQLite (development) and PostgreSQL (production)

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- PostgreSQL (optional, for production)
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jamseyboy/django_foodOrderApp.git
   cd django_foodOrderApp
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3  # For development
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
   ```

5. **Run migrations**
   ```bash
   cd src
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

## 📦 Project Structure

```
django_foodOrderApp/
├── src/
│   ├── customer/                 # Customer app
│   │   ├── models.py            # Customer, Order, and OrderItem models
│   │   ├── api.py               # API endpoints for customer operations
│   │   ├── schemas.py           # Pydantic schemas for validation
│   │   ├── views.py
│   │   ├── admin.py
│   │   ├── migrations/          # Database migrations
│   │   └── tests.py
│   │
│   ├── food/                     # Food app
│   │   ├── models.py            # Food model
│   │   ├── api.py               # API endpoints for food operations
│   │   ├── schemas.py           # Pydantic schemas
│   │   └── migrations/
│   │
│   ├── foodOrderApp/             # Main project configuration
│   │   ├── settings.py          # Django settings
│   │   ├── urls.py              # URL routing
│   │   ├── api.py               # Main API configuration
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   ├── manage.py                # Django management script
│   └── db.sqlite3               # SQLite database (development)
│
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── railway.toml                  # Railway.app deployment config
├── rav.yaml                      # RAV configuration
└── README.md                     # This file
```

## 🔌 API Endpoints

### Health Check
- `GET /api/hello` - Check if API is running

### Authentication
- `POST /api/token` - Obtain JWT tokens
- `POST /api/token/refresh` - Refresh JWT token
- `GET /api/me` - Get current user information (requires JWT auth)

### Food Management
- `GET /api/food/food_info_all` - Get all food items
- `GET /api/food/...` - Additional food endpoints (check `food/api.py`)

### Customer Management
- `GET /api/customer/customer_info_all` - Get all customers
- `POST /api/customer/create_customer` - Create a new customer
  ```json
  {
    "username": "john_doe"
  }
  ```

### Order Management
- `GET /api/customer/orderslist` - Get all orders
- `POST /api/customer/create_orders` - Create a new order
  ```json
  {
    "customer_id": 1,
    "order_status": "pending"
  }
  ```

- `POST /api/customer/create_order_item` - Add items to an order
  ```json
  {
    "order_id": 1,
    "order_status": "confirmed",
    "items": [
      {
        "food_id": 1,
        "food_quantity": 2
      }
    ]
  }
  ```

- `POST /api/customer/update_order_status` - Update order status
  ```json
  {
    "id": 1,
    "order_status": "delivered"
  }
  ```

- `GET /api/customer/todays_detail_order_list` - Get today's orders organized by customer
  ```json
  {
    "todayOrderDetails": {
      "customer_name": [
        {
          "item_id": 1,
          "order_id": 1,
          "order_status": "confirmed",
          "food_name": "Pizza",
          "food_price": 500,
          "food_quantity": 2,
          "total_amount": 1000,
          "timestamp": "2024-06-20T10:30:00Z"
        }
      ]
    }
  }
  ```

## 📊 Data Models

### Customer Model
```python
- username (CharField, max_length=100)
- orders (Related OrderModel)
```

### Food Model
```python
- food_name (CharField, max_length=100)
- food_price (IntegerField)
- timestamp (DateTimeField, auto_now=True)
```

### Order Model
```python
- customer_info (ForeignKey to Customer)
- order_status (CharField, max_length=50)
- timestamp (DateTimeField, auto_now=True)
- items (Related OrderItemModel)
```

### OrderItem Model
```python
- order_info (ForeignKey to Order)
- food_info (ForeignKey to Food)
- food_quantity (IntegerField)
- total_amount (IntegerField)
- timestamp (DateTimeField, auto_now=True)
```

## 🔐 Security

- **JWT Authentication**: Uses `django-ninja-jwt` for secure token-based authentication
- **CSRF Protection**: Django's built-in CSRF middleware
- **CORS Configuration**: Configurable CORS origins for production
- **Secret Key Management**: Uses environment variables for sensitive configuration

### Environment Variables
- `DJANGO_SECRET_KEY` - Secret key for session encryption
- `DJANGO_DEBUG` - Debug mode (False in production)
- `DATABASE_URL` - Database connection string
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed origins

## 🐳 Docker Deployment

### Build the Docker image
```bash
docker build -t django-food-order-app .
```

### Run the container
```bash
docker run -e DJANGO_SECRET_KEY=your-secret-key \
           -e DJANGO_DEBUG=False \
           -e DATABASE_URL=postgresql://user:password@host:5432/db \
           -p 8000:8000 \
           django-food-order-app
```

## 🚢 Production Deployment

The application is configured for deployment on Railway.app with PostgreSQL database support:

1. Set up environment variables on Railway.app:
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG=False`
   - `DATABASE_URL` (PostgreSQL connection string)
   - `CORS_ALLOWED_ORIGINS`

2. The application uses Gunicorn as the WSGI server
3. Database migrations run automatically on startup
4. Supports dynamic port configuration via `PORT` environment variable

## 📝 Dependencies

- **Django 5.1+** - Web framework
- **django-ninja** - Modern REST API framework for Django
- **django-ninja-jwt** - JWT authentication for Django Ninja
- **django-cors-headers** - CORS support
- **python-decouple** - Environment variable management
- **gunicorn** - Production WSGI server
- **dj-database-url** - Database URL parsing
- **psycopg[binary]** - PostgreSQL adapter for Python
- **rav** - Additional utilities

See `requirements.txt` for complete list and versions.

## 🧪 Testing

Run tests using Django's test runner:
```bash
cd src
python manage.py test
```

## 🔧 Development

### Apply migrations
```bash
cd src
python manage.py makemigrations
python manage.py migrate
```

### Access Django Admin
Navigate to `http://localhost:8000/admin/` with your superuser credentials.

### Environment: India Standard Time (IST)
The application is configured to use Asia/Kolkata timezone.

## 📚 Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Ninja Documentation](https://django-ninja.rest-framework.com/)
- [Django Ninja JWT](https://eadwulf.github.io/django-ninja-jwt/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**jamseyboy** - [GitHub Profile](https://github.com/jamseyboy)

## 📞 Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/jamseyboy/django_foodOrderApp/issues).

---

**Note**: This is a backend API application. For a complete food ordering system, you'll need to pair this with a frontend application (e.g., React, Vue, or Next.js).
