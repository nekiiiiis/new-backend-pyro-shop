# PyroShop — Práctica 2 (FastAPI + Svelte 5)

> Programación Web II — curso 2025/2026
>
> Reemplazo del backend Node.js/Express/MongoDB de la práctica 1 por un
> **backend Python** desarrollado con **FastAPI**, arquitectura limpia
> en capas, persistencia real con **SQLAlchemy + SQLite**, validación
> estricta con **Pydantic** y autenticación **JWT**.
> El frontend Svelte 5 sigue funcionando sin cambios porque se respeta
> el contrato JSON original.

---

## 🚀 Cómo desplegar / ejecutar (lectura rápida para el profesor)

### Requisitos previos

- **Python 3.10+** (probado en 3.10.12)
- **Node.js 18+** y **npm**
- `python3-venv` (en Debian/Ubuntu: `sudo apt install python3-venv`)
  o `virtualenv` (`pip3 install --user virtualenv`)

### 1️⃣ Backend (terminal 1)

```bash
cd backend

# Crear y activar entorno virtual
python3 -m venv .venv            # o:  virtualenv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Variables de entorno (mínimo: JWT_SECRET)
cp .env.example .env

# Arrancar el servidor (con autoreload)
python run.py
# Alternativa equivalente:
# uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

El servidor crea automáticamente las tablas SQLite en
`backend/data/pyroshop.db` y siembra datos demo si la base de datos
está vacía.

**Backend listo en:** http://localhost:3000

- Swagger UI → http://localhost:3000/docs
- Healthcheck → http://localhost:3000/health

### 2️⃣ Frontend (terminal 2)

```bash
cd frontend
npm install
npm run dev
```

**Frontend listo en:** http://localhost:5173 (Vite proxea `/auth`,
`/productos` y `/api` al backend, sin problemas de CORS).

### 3️⃣ Credenciales de prueba (usuarios semilla)

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `123456` | `admin` |
| `usuarioPrueba` | `123456` | `user` |

> Los datos se cargan automáticamente al primer arranque mientras
> `SEED_ON_STARTUP=true` (valor por defecto en `.env.example`).

### 4️⃣ Verificación rápida con `curl` (opcional)

```bash
# Healthcheck
curl http://localhost:3000/health

# Login admin → JWT
curl -X POST http://localhost:3000/auth/login \
     -H 'Content-Type: application/json' \
     -d '{"username":"admin","password":"123456"}'

# Listar productos (público)
curl http://localhost:3000/productos
```

### 📂 Documentos clave de la entrega

| Archivo | Contenido |
|---------|-----------|
| [`README.md`](./README.md) | Este documento (despliegue + descripción técnica) |
| [`backend/AI_USAGE.md`](./backend/AI_USAGE.md) | Memoria del uso de IA (prompts, iteraciones y análisis crítico) |
| [`backend/.env.example`](./backend/.env.example) | Plantilla de variables de entorno |
| [`backend/requirements.txt`](./backend/requirements.txt) | Dependencias Python |

---

## Tabla de contenidos

1. [Cambios respecto a la práctica 1](#cambios-respecto-a-la-práctica-1)
2. [Tecnologías](#tecnologías)
3. [Arquitectura y estructura del proyecto](#arquitectura-y-estructura-del-proyecto)
4. [API REST](#api-rest)
5. [Modelo de datos](#modelo-de-datos)
6. [Validación y errores](#validación-y-errores)
7. [Seguridad](#seguridad)
8. [Uso de Inteligencia Artificial](#uso-de-inteligencia-artificial)
9. [Frontend (resumen rápido)](#frontend-resumen-rápido)
10. [Endpoints utilizados por el frontend](#endpoints-utilizados-por-el-frontend)

---

## Cambios respecto a la práctica 1

| Aspecto | Práctica 1 (Node) | Práctica 2 (Python) |
|---------|-------------------|---------------------|
| Lenguaje | Node.js (CommonJS) | Python 3.10+ |
| Framework | Express | FastAPI |
| ORM / BD | Mongoose + MongoDB | SQLAlchemy 2.0 + SQLite |
| Validación | Manual en cada ruta | Pydantic v2 (422 estructurado) |
| Manejo de errores | `try/catch` por ruta | Excepciones de dominio + handlers globales |
| Auth | `jsonwebtoken` + bcrypt | PyJWT + bcrypt |
| Arquitectura | Routes + Models | Routers / Services / Repositories / Models |
| Tiempo real | Socket.IO (chat) | *Fuera del alcance de la práctica 2* |

El **contrato HTTP** (URLs, métodos, formato JSON con `_id`, `createdAt`,
`nombre`, `precio`, etc.) se conserva intacto. El frontend Svelte 5
arranca contra el nuevo backend sin tocar ni una línea.

---

## Tecnologías

| Capa | Tecnología |
|------|------------|
| Frontend | Svelte 5, Vite 6 |
| Backend | Python 3.10+, FastAPI 0.115, Uvicorn |
| ORM | SQLAlchemy 2.0 (estilo `Mapped[...]`) |
| Base de datos | SQLite (por defecto) — sustituible por cualquier dialecto soportado |
| Validación | Pydantic v2 + Pydantic Settings |
| Autenticación | JWT (PyJWT) + bcrypt 4.x |

---

## Arquitectura y estructura del proyecto

El backend sigue una **arquitectura en capas** estricta. Cada capa
solo conoce a la inmediatamente inferior. La capa HTTP **nunca** habla
con SQLAlchemy directamente; siempre pasa por un servicio, que a su vez
delega en un repositorio.

```
┌────────────────────────────────────────────────────────┐
│ Routers (app/api/routers)                              │
│   - Validan input con Pydantic                         │
│   - Inyectan CurrentUser / sesión BD vía Depends       │
│   - Delegan al servicio y serializan la respuesta      │
└─────────────────────────┬──────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────┐
│ Services (app/services)                                │
│   - Casos de uso y reglas de negocio                   │
│   - Lanzan excepciones de dominio                      │
│   - Orquestan varios repositorios                      │
└─────────────────────────┬──────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────┐
│ Repositories (app/repositories)                        │
│   - Acceso a datos con SQLAlchemy 2.0                  │
│   - Encapsulan select/insert/update/delete             │
└─────────────────────────┬──────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────┐
│ Models (app/models)                                    │
│   - Mapping ORM (Base declarativa, Mapped[...])        │
└────────────────────────────────────────────────────────┘
```

Estructura de carpetas:

```
Practica2/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # Factoría FastAPI + lifespan
│   │   ├── core/
│   │   │   ├── config.py            # Settings (Pydantic Settings)
│   │   │   ├── database.py          # Engine, SessionLocal, get_db, init_db
│   │   │   ├── security.py          # bcrypt + JWT
│   │   │   └── exceptions.py        # DomainError + handlers globales
│   │   ├── models/                  # ORM SQLAlchemy (User, Product, Cart, Order)
│   │   ├── schemas/                 # Pydantic (entrada/salida)
│   │   ├── repositories/            # Acceso a datos
│   │   ├── services/                # Lógica de negocio
│   │   ├── api/
│   │   │   ├── deps.py              # get_current_user, get_current_admin, get_db
│   │   │   └── routers/             # auth, products, users, cart, orders
│   │   └── seeds/seed_data.py       # Datos iniciales de desarrollo
│   ├── requirements.txt
│   ├── .env.example
│   ├── run.py                       # Entrypoint de desarrollo
│   └── AI_USAGE.md                  # Memoria del uso de IA (entregable)
├── frontend/                        # Svelte 5 + Vite (sin cambios)
└── README.md
```

---

## API REST

> Convenciones:
> - Las rutas marcadas como **Auth** requieren cabecera
>   `Authorization: Bearer <token>`.
> - Las rutas **Admin** además exigen que el token corresponda a un
>   usuario con rol `admin`.
> - Los IDs son cadenas hexadecimales de 32 caracteres (UUID4 sin
>   guiones) y se exponen como `_id` para mantener el contrato anterior.

### Autenticación

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `POST` | `/auth/register` | Registra un usuario (siempre rol `user`) | — |
| `POST` | `/auth/login` | Inicia sesión y devuelve JWT | — |
| `GET`  | `/auth/me` | Datos del usuario autenticado | Auth |
| `PUT`  | `/auth/change-password` | Cambia la contraseña actual | Auth |

### Productos

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET`    | `/productos` | Lista todos los productos | — |
| `POST`   | `/productos` | Crea un producto | Admin |
| `PUT`    | `/productos/{id}` | Edita un producto | Admin |
| `DELETE` | `/productos/{id}` | Elimina un producto | Admin |

### Usuarios

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET`    | `/api/users` | Lista de usuarios | Admin |
| `GET`    | `/api/users/{id}` | Detalle de un usuario | Admin |
| `PUT`    | `/api/users/{id}/role` | Cambia el rol (no puede ser el propio) | Admin |
| `DELETE` | `/api/users/{id}` | Elimina (no puede ser el propio) | Admin |

### Carrito

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET`    | `/api/cart` | Carrito del usuario actual | Auth |
| `POST`   | `/api/cart/add` | Añade un producto (cantidad 1–999) | Auth |
| `PUT`    | `/api/cart/update` | Actualiza la cantidad | Auth |
| `DELETE` | `/api/cart/remove/{productId}` | Elimina un ítem | Auth |
| `DELETE` | `/api/cart/clear` | Vacía el carrito | Auth |

### Pedidos

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET`    | `/api/orders` | Lista todos los pedidos (`?status=pending`/`completed`) | Admin |
| `GET`    | `/api/orders/my-orders` | Pedidos del usuario actual | Auth |
| `GET`    | `/api/orders/{id}` | Detalle (dueño o admin) | Auth |
| `POST`   | `/api/orders` | Crea un pedido desde el carrito | Auth |
| `PUT`    | `/api/orders/{id}/status` | Cambia el estado | Admin |
| `DELETE` | `/api/orders/{id}` | Cancela un pedido pendiente | Auth |

---

## Modelo de datos

Todos los modelos viven en `backend/app/models/` y usan SQLAlchemy 2.0
con anotaciones `Mapped[...]`.

### User
- `id`: string (UUID4 hex, PK)
- `username`: string, único, ≥ 3 caracteres
- `password_hash`: bcrypt
- `role`: `user` | `admin`
- `created_at` / `updated_at`

### Product
- `id`: string (UUID4 hex, PK)
- `nombre`: string ≤ 120
- `precio`: float ≥ 0
- `descripcion`: text
- `imagen`: string opcional (URL)
- `categoria`: `fuegos-artificiales` | `petardos` | `bengalas` | `cohetes` | `otros`
- `created_at` / `updated_at`

### Cart (+ CartItem)
- `Cart`: 1-1 con `User`. `total` se calcula como propiedad de instancia.
- `CartItem`: snapshot desnormalizado del producto en el momento de
  añadirlo al carrito (`nombre`, `precio`, `imagen`).

### Order (+ OrderItem)
- `Order`: pertenece a un `User`, contiene `total`, `status`
  (`pending`/`completed`) y `OrderItem[]`.
- `OrderItem`: snapshot inmutable de la línea de pedido con `subtotal`
  precalculado.

> **Desnormalización intencionada**: tanto `CartItem` como `OrderItem`
> almacenan `nombre`, `precio` e `imagen` del producto. Esto preserva
> el precio en el momento de la compra y evita joins constantes para
> mostrar listas.

---

## Validación y errores

### Validación estricta (Pydantic v2)

Cada payload de entrada se valida con un esquema en
`backend/app/schemas/`. Si los datos no cumplen las reglas, FastAPI
responde con `422 Unprocessable Entity` y un cuerpo unificado:

```json
{
  "error": "precio: Input should be greater than or equal to 0",
  "details": [
    {
      "type": "greater_than_equal",
      "loc": ["body", "precio"],
      "msg": "Input should be greater than or equal to 0",
      "input": -1,
      "ctx": { "ge": 0.0 }
    }
  ]
}
```

### Manejador global de excepciones

`backend/app/core/exceptions.py` define una jerarquía de excepciones de
dominio y registra los siguientes manejadores en FastAPI:

| Excepción capturada | Status HTTP | Origen típico |
|---------------------|-------------|---------------|
| `NotFoundError` | 404 | Recurso inexistente (servicios) |
| `ValidationError` | 422 | Regla de negocio rota |
| `ConflictError` | 409 | Usuario duplicado, etc. |
| `AuthenticationError` | 401 | Token ausente/expirado, credenciales inválidas |
| `AuthorizationError` | 403 | Token válido pero sin permisos |
| `RequestValidationError` (FastAPI) | 422 | Payload no cumple esquema Pydantic |
| `IntegrityError` (SQLAlchemy) | 409 | Restricciones UNIQUE/FK |
| `SQLAlchemyError` | 500 | Otros errores de BD (mensaje genérico en prod) |
| `Exception` | 500 | Catch-all (mensaje genérico en prod) |

La capa HTTP **no usa `try/except`**: simplemente delega y deja que el
manejador global formatee la respuesta.

---

## Seguridad

| Medida | Implementación |
|--------|----------------|
| Hashing de contraseñas | `bcrypt` 4.x con salt aleatorio (10 rondas) |
| Tokens | JWT HS256 con `iat`/`exp`, sin fallback de secret |
| Autorización | Dependencias `get_current_user` y `get_current_admin` |
| Escalada de privilegios | El registro siempre asigna rol `user` |
| Auto-eliminación / auto-degradación | Bloqueada en `UserService` |
| CORS | Restringido a `CORS_ORIGINS` |
| Errores | Mensajes genéricos en producción (`APP_ENV=production`) |
| Validación | Pydantic v2 rechaza tipos, longitudes y rangos inválidos |
| Inyección SQL | SQLAlchemy parametriza todas las consultas |

---

## Uso de Inteligencia Artificial

La memoria completa del uso de IA — prompts clave, iteraciones,
errores/alucinaciones detectados y correcciones manuales — está en
[`backend/AI_USAGE.md`](backend/AI_USAGE.md).

Resumen ejecutivo:

- Se usó **Cursor + Claude/GPT** como copiloto crítico, no como
  generador ciego.
- Se documentan al menos **cinco alucinaciones o errores** detectados
  (passlib obsoleto con bcrypt 4, separación de responsabilidades en
  routers, SQLAlchemy 1.4 vs 2.0, `@app.on_event` deprecado y
  dependencias con `yield from`) y cómo se corrigieron a mano.
- Se distingue claramente entre lo aportado por la IA (boilerplate,
  alias Pydantic, primera versión del manejador de errores) y las
  decisiones de diseño hechas por mí (estructura de carpetas, política
  de seguridad en login, contrato de IDs, validación login vs
  registro).

---

## Frontend (resumen rápido)

El frontend es la SPA Svelte 5 desarrollada en la práctica 1, sin
cambios. Vive en `frontend/` y se conecta al backend Python a través
del proxy de Vite (puerto 5173 → 3000).

Páginas principales: `Login`, `Register`, `Products`, `Cart`, `Orders`,
`Profile`, `AdminPanel`. Usa runes de Svelte 5 (`$state`, `$derived`,
`$effect`) y un store de auth basado en `localStorage`.

---

## Endpoints utilizados por el frontend

| Página / acción | Endpoint(s) | Roles |
|------------------|-------------|-------|
| Login / Registro | `POST /auth/login`, `POST /auth/register` | público |
| Perfil | `GET /auth/me`, `PUT /auth/change-password` | usuario |
| Catálogo (lectura) | `GET /productos` | público |
| Catálogo (CRUD) | `POST/PUT/DELETE /productos[/:id]` | admin |
| Carrito | `GET /api/cart`, `POST /api/cart/add`, `PUT /api/cart/update`, `DELETE /api/cart/remove/:id`, `DELETE /api/cart/clear` | usuario |
| Mis pedidos | `GET /api/orders/my-orders`, `DELETE /api/orders/:id` | usuario |
| Panel admin | `GET /api/users`, `PUT /api/users/:id/role`, `DELETE /api/users/:id`, `GET /api/orders`, `PUT /api/orders/:id/status` | admin |

---

## Autor

Neco Martínez — Programación Web II — Práctica 2 (FastAPI + Svelte 5)
