# SOFF API Backend

SOFF API is a modular Django RESTful backend for a furniture e-commerce platform. It provides endpoints for user authentication, product management, shopping carts, categories, manufacturers, and more. The project is designed for scalability, security, and ease of integration with frontend clients.

## Features

- **User Management**: Registration, login, JWT authentication, email confirmation via OTP, password reset, profile management, and favorites.
- **Product Catalog**: CRUD operations for products, advanced filtering, search, AR model support, and manufacturer/category relations.
- **Shopping Cart**: Add, update, and remove products; view cart details; checkout integration ready.
- **Categories & Manufacturers**: Manage product categories, room categories, and manufacturers with images and slugs.
- **API Documentation**: Auto-generated OpenAPI/Swagger docs via [drf-spectacular](https://drf-spectacular.readthedocs.io/).
- **Security**: JWT authentication, password validation, CORS, and rate limiting.
- **Logging & Monitoring**: Configurable logging, Silk profiling, and Redis caching.

## Technologies

- Python 3.12+
- Django 5.1+
- Django REST Framework
- drf-spectacular (OpenAPI docs)
- SimpleJWT (auth)
- Redis (cache)
- Silk (profiling)

## Setup & Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/your-org/soff-api.git
   cd soff-api
   ```

2. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
    Create a `.env` file in the parent directory. See the example below:

    ```ini
    SECRET_KEY=secret-key
    DEBUG=True
    ALLOWED_HOSTS=allowed hosts seperated by comma (host1,host2,...)
    CORS_ALLOWED_ORIGINS=allowed origins seperated by comma (origin1,origin2,...)

    # Database settings
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=db_name
    DB_USER=db_user
    DB_PASSWORD=db_password
    DB_HOST=db_host
    DB_PORT=db_port

    # Redis cache
    REDIS_CACHE_URL=redis_url

    # Email settings
    EMAIL_HOST_USER=your-email
    EMAIL_HOST_PASSWORD=your-email-password
    ```

4. **Apply migrations:**

   ```sh
   python manage.py migrate
   ```

5. **Create superuser (optional):**

   ```sh
   python manage.py createsuperuser
   ```

6. **Run the development server:**

   ```sh
   python manage.py runserver
   ```

## API Endpoints

All endpoints are versioned under `/api/v1/`.

### User Endpoints (`/api/v1/user/`)

- `POST /register` — Register a new user
- `POST /register/confirm` — Confirm email with OTP
- `POST /login` — Login and obtain JWT tokens
- `POST /logout` — Logout user
- `POST /token/refresh` — Refresh JWT token
- `POST /otp/resend` — Resend OTP
- `POST /otp/verify` — Verify OTP
- `POST /password/change` — Change password
- `POST /password/reset` — Request password reset
- `POST /password/reset/confirm` — Confirm password reset
- `GET /profile` — Get user profile
- `PUT /profile` — Update user profile
- `GET /favorites` — List favorite products
- `POST /favorites` — Add product to favorites
- `DELETE /favorites` — Remove all favorites
- `GET /favorites/<slug:product_slug>` — Get favorite product detail
- `DELETE /favorites/<slug:product_slug>` — Remove product from favorites

### Product Endpoints (`/api/v1/product/`)

- `GET /` — List products (paginated)
- `POST /` — Create product
- `GET /<slug:product_slug>` — Get product detail
- `PUT /<slug:product_slug>` — Update product
- `DELETE /<slug:product_slug>` — Delete product
- `GET /filter/` — Filter products
- `GET /search/` — Search products

### Cart Endpoints (`/api/v1/cart/`)

- `GET /` — Get current user's cart
- `POST /` — Add product to cart
- `GET /<slug:product_slug>` — Get cart item detail
- `PUT /<slug:product_slug>` — Update cart item quantity
- `DELETE /<slug:product_slug>` — Remove product from cart
- `DELETE /clear/` — Clear cart

### Category Endpoints (`/api/v1/category/`)

- `GET /product/` — List product categories
- `POST /product/` — Create product category
- `GET /product/<slug:slug>` — Get product category detail
- `PUT /product/<slug:slug>` — Update product category
- `DELETE /product/<slug:slug>` — Delete product category
- `GET /room/` — List room categories
- `POST /room/` — Create room category
- `GET /room/<slug:slug>` — Get room category detail
- `PUT /room/<slug:slug>` — Update room category
- `DELETE /room/<slug:slug>` — Delete room category

### Manufacturer Endpoints (`/api/v1/manufacturer/`)

- `GET /` — List manufacturers
- `POST /` — Create manufacturer
- `GET /<slug:slug>` — Get manufacturer detail
- `PUT /<slug:slug>` — Update manufacturer
- `DELETE /<slug:slug>` — Delete manufacturer

See [Swagger UI](http://localhost:8000/swagger/) or [Redoc](http://localhost:8000/redoc/) for full interactive API docs.

### API Documentation

- Use the Swagger UI at `http://localhost:8000/swagger/` for interactive API exploration.
- Attach the token in the `Authorization` header for authenticated requests:

  ```text
  Authorization: Bearer <your_token>
  ```

## Contact & Support

For questions or support, open an issue or contact the maintainers via GitHub.
