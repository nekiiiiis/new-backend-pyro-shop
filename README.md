# PyroShop — Práctica 2 (FastAPI + Svelte 5)
Repositorio: https://github.com/nekiiiiis/new-backend-pyro-shop

> Programación Web II — curso 2025/2026.
>
> El backend Node.js/Express/MongoDB de la práctica 1 se sustituye por
> un **backend Python** desarrollado con **FastAPI**, una arquitectura
> en capas, persistencia con **SQLAlchemy + SQLite**, validación
> estricta con **Pydantic** y autenticación mediante **JWT**.
> El frontend Svelte 5 se reutiliza sin modificaciones gracias a la
> preservación del contrato JSON original.

---

## Despliegue y ejecución

### Requisitos previos

- **Python 3.10 o superior** (probado en 3.10.12).
- **Node.js 18 o superior** y **npm**.
- `python3-venv` (en distribuciones basadas en Debian/Ubuntu se
  instala con `sudo apt install python3-venv`) o, en su defecto,
  `virtualenv` (`pip3 install --user virtualenv`).

### 1. Backend (terminal 1)

```bash
cd backend

# Crear y activar el entorno virtual
python3 -m venv .venv            # alternativa: virtualenv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (como mínimo: JWT_SECRET)
cp .env.example .env

# Arrancar el servidor (modo desarrollo con autoreload)
python run.py
# Equivalente:
# uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

Durante el primer arranque, el servidor crea automáticamente las
tablas SQLite en `backend/data/pyroshop.db` y carga los datos
iniciales de demostración si la base de datos se encuentra vacía.

**Backend disponible en:** http://localhost:3000

- Documentación interactiva (Swagger UI): http://localhost:3000/docs
- Endpoint de comprobación de estado: http://localhost:3000/health

### 2. Frontend (terminal 2)

```bash
cd frontend
npm install
npm run dev
```

**Frontend disponible en:** http://localhost:5173. Vite redirige
mediante proxy las rutas `/auth`, `/productos` y `/api` al backend,
por lo que no se requiere configuración adicional de CORS en
desarrollo.

### 3. Credenciales de prueba (usuarios precargados)

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `123456` | `admin` |
| `usuarioPrueba` | `123456` | `user` |

Estos usuarios se crean automáticamente en el primer arranque siempre
que la variable `SEED_ON_STARTUP` esté establecida en `true` (valor
predeterminado en `.env.example`).

### 4. Verificación rápida mediante `curl` (opcional)

```bash
# Comprobación de estado
curl http://localhost:3000/health

# Inicio de sesión como administrador (devuelve un token JWT)
curl -X POST http://localhost:3000/auth/login \
     -H 'Content-Type: application/json' \
     -d '{"username":"admin","password":"123456"}'

# Listado público de productos
curl http://localhost:3000/productos
```

### Documentos clave de la entrega

| Archivo | Contenido |
|---------|-----------|
| [`README.md`](./README.md) | Documento principal: despliegue y descripción técnica. |
| [`backend/AI_USAGE.md`](./backend/AI_USAGE.md) | Memoria del uso de IA: prompts, iteraciones y análisis crítico. |
| [`backend/.env.example`](./backend/.env.example) | Plantilla de variables de entorno. |
| [`backend/requirements.txt`](./backend/requirements.txt) | Dependencias del backend Python. |

---

## Tabla de contenidos

1. [Cambios respecto a la práctica 1](#cambios-respecto-a-la-práctica-1)
2. [Tecnologías](#tecnologías)
3. [Arquitectura y estructura del proyecto](#arquitectura-y-estructura-del-proyecto)
4. [API REST](#api-rest)
5. [Modelo de datos](#modelo-de-datos)
6. [Validación y manejo de errores](#validación-y-manejo-de-errores)
7. [Seguridad](#seguridad)
8. [Uso de Inteligencia Artificial](#uso-de-inteligencia-artificial)
9. [Frontend](#frontend)
10. [Endpoints utilizados por el frontend](#endpoints-utilizados-por-el-frontend)

---

## Cambios respecto a la práctica 1

| Aspecto | Práctica 1 (Node) | Práctica 2 (Python) |
|---------|-------------------|---------------------|
| Lenguaje | Node.js (CommonJS) | Python 3.10 o superior |
| Framework | Express | FastAPI |
| ORM / Base de datos | Mongoose + MongoDB | SQLAlchemy 2.0 + SQLite |
| Validación | Manual en cada ruta | Pydantic v2 (respuesta 422 estructurada) |
| Manejo de errores | `try/catch` por ruta | Excepciones de dominio con manejadores globales |
| Autenticación | `jsonwebtoken` + bcrypt | PyJWT + bcrypt |
| Arquitectura | Rutas y modelos | Routers / Services / Repositories / Models |
| Tiempo real | Socket.IO (chat) | Fuera del alcance de la práctica 2 |

El **contrato HTTP** (URLs, métodos y formato JSON con `_id`,
`createdAt`, `nombre`, `precio`, etc.) se conserva intacto. En
consecuencia, el frontend Svelte 5 funciona contra el nuevo backend
sin requerir modificación alguna.

---

## Tecnologías

| Capa | Tecnología |
|------|------------|
| Frontend | Svelte 5, Vite 6 |
| Backend | Python 3.10+, FastAPI 0.115, Uvicorn |
| ORM | SQLAlchemy 2.0 (estilo `Mapped[...]`) |
| Base de datos | SQLite por defecto, sustituible por cualquier dialecto compatible |
| Validación | Pydantic v2 y Pydantic Settings |
| Autenticación | JWT (PyJWT) y bcrypt 4.x |

---

## Arquitectura y estructura del proyecto

El backend sigue una **arquitectura en capas estricta**. Cada capa
únicamente conoce a la inmediatamente inferior; en particular, la capa
HTTP no accede directamente a SQLAlchemy, sino que delega siempre en
un servicio que, a su vez, utiliza el repositorio correspondiente.

```
┌────────────────────────────────────────────────────────┐
│ Routers (app/api/routers)                              │
│   - Validan la entrada con Pydantic                    │
│   - Inyectan CurrentUser y la sesión BD vía Depends    │
│   - Delegan en el servicio y serializan la respuesta   │
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
│   │   ├── main.py                  # Factoría FastAPI y lifespan
│   │   ├── core/
│   │   │   ├── config.py            # Configuración (Pydantic Settings)
│   │   │   ├── database.py          # Engine, SessionLocal, get_db, init_db
│   │   │   ├── security.py          # bcrypt y JWT
│   │   │   └── exceptions.py        # DomainError y manejadores globales
│   │   ├── models/                  # ORM SQLAlchemy (User, Product, Cart, Order)
│   │   ├── schemas/                 # Pydantic (entrada y salida)
│   │   ├── repositories/            # Acceso a datos
│   │   ├── services/                # Lógica de negocio
│   │   ├── api/
│   │   │   ├── deps.py              # get_current_user, get_current_admin, get_db
│   │   │   └── routers/             # auth, products, users, cart, orders
│   │   └── seeds/seed_data.py       # Datos iniciales de desarrollo
│   ├── requirements.txt
│   ├── .env.example
│   ├── run.py                       # Entrada del modo de desarrollo
│   └── AI_USAGE.md                  # Memoria del uso de IA (entregable)
├── frontend/                        # Svelte 5 + Vite (sin modificaciones)
└── README.md
```

---

## API REST

> Convenciones:
> - Las rutas marcadas como **Auth** requieren la cabecera
>   `Authorization: Bearer <token>`.
> - Las rutas **Admin** exigen, además, que el token corresponda a un
>   usuario con rol `admin`.
> - Los identificadores son cadenas hexadecimales de 32 caracteres
>   (UUID4 sin guiones) y se exponen como `_id` para mantener el
>   contrato del backend anterior.

### Autenticación

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `POST` | `/auth/register` | Registra un usuario (siempre rol `user`). | — |
| `POST` | `/auth/login` | Inicia sesión y devuelve un JWT. | — |
| `GET`  | `/auth/me` | Devuelve los datos del usuario autenticado. | Auth |
| `PUT`  | `/auth/change-password` | Modifica la contraseña actual. | Auth |

### Productos

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET`    | `/productos` | Lista todos los productos. | — |
| `POST`   | `/productos` | Crea un producto. | Admin |
| `PUT`    | `/productos/{id}` | Edita un producto existente. | Admin |
| `DELETE` | `/productos/{id}` | Elimina un producto. | Admin |

### Usuarios

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET`    | `/api/users` | Lista de usuarios. | Admin |
| `GET`    | `/api/users/{id}` | Detalle de un usuario. | Admin |
| `PUT`    | `/api/users/{id}/role` | Modifica el rol (un administrador no puede modificar el suyo). | Admin |
| `DELETE` | `/api/users/{id}` | Elimina un usuario (un administrador no puede eliminarse a sí mismo). | Admin |

### Carrito

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET`    | `/api/cart` | Carrito del usuario autenticado. | Auth |
| `POST`   | `/api/cart/add` | Añade un producto al carrito (cantidad entre 1 y 999). | Auth |
| `PUT`    | `/api/cart/update` | Actualiza la cantidad de un ítem. | Auth |
| `DELETE` | `/api/cart/remove/{productId}` | Elimina un ítem del carrito. | Auth |
| `DELETE` | `/api/cart/clear` | Vacía el carrito por completo. | Auth |

### Pedidos

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET`    | `/api/orders` | Lista todos los pedidos (filtrable mediante `?status=pending` o `?status=completed`). | Admin |
| `GET`    | `/api/orders/my-orders` | Pedidos del usuario autenticado. | Auth |
| `GET`    | `/api/orders/{id}` | Detalle de un pedido (visible para su propietario o un administrador). | Auth |
| `POST`   | `/api/orders` | Crea un pedido a partir del contenido del carrito. | Auth |
| `PUT`    | `/api/orders/{id}/status` | Actualiza el estado de un pedido. | Admin |
| `DELETE` | `/api/orders/{id}` | Cancela un pedido pendiente. | Auth |

---

## Modelo de datos

Todos los modelos se ubican en `backend/app/models/` y emplean
SQLAlchemy 2.0 con anotaciones `Mapped[...]`.

### User

- `id`: cadena (UUID4 hex, clave primaria).
- `username`: cadena, única, longitud mínima de 3 caracteres.
- `password_hash`: bcrypt.
- `role`: `user` o `admin`.
- `created_at` y `updated_at`.

### Product

- `id`: cadena (UUID4 hex, clave primaria).
- `nombre`: cadena de hasta 120 caracteres.
- `precio`: número en coma flotante, no negativo.
- `descripcion`: texto.
- `imagen`: cadena opcional (URL).
- `categoria`: `fuegos-artificiales`, `petardos`, `bengalas`,
  `cohetes` u `otros`.
- `created_at` y `updated_at`.

### Cart (con CartItem)

- `Cart`: relación uno a uno con `User`. La propiedad `total` se
  calcula en tiempo de ejecución.
- `CartItem`: copia desnormalizada de los campos del producto
  (`nombre`, `precio`, `imagen`) en el momento en que se incorpora al
  carrito.

### Order (con OrderItem)

- `Order`: pertenece a un `User` y contiene `total`, `status`
  (`pending` o `completed`) y una colección de `OrderItem`.
- `OrderItem`: registro inmutable de cada línea del pedido, con su
  `subtotal` precalculado.

> **Decisión de diseño: desnormalización intencionada.** Tanto
> `CartItem` como `OrderItem` almacenan `nombre`, `precio` e `imagen`
> del producto. De esta forma se preserva el precio en el instante de
> la compra y se evita la necesidad de realizar joins repetidamente
> al mostrar los listados.

---

## Validación y manejo de errores

### Validación estricta con Pydantic v2

Cada payload de entrada se valida frente al esquema correspondiente
de `backend/app/schemas/`. Si los datos no cumplen las restricciones,
FastAPI responde con `422 Unprocessable Entity` y un cuerpo
homogéneo:

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

`backend/app/core/exceptions.py` define una jerarquía de excepciones
de dominio y registra los siguientes manejadores en FastAPI:

| Excepción | Código HTTP | Origen habitual |
|-----------|-------------|-----------------|
| `NotFoundError` | 404 | Recurso inexistente (capa de servicios). |
| `ValidationError` | 422 | Regla de negocio incumplida. |
| `ConflictError` | 409 | Conflicto, por ejemplo un nombre de usuario duplicado. |
| `AuthenticationError` | 401 | Token ausente, expirado o credenciales incorrectas. |
| `AuthorizationError` | 403 | Token válido pero sin permisos suficientes. |
| `RequestValidationError` (FastAPI) | 422 | Payload no conforme al esquema Pydantic. |
| `IntegrityError` (SQLAlchemy) | 409 | Restricciones de unicidad o de clave foránea. |
| `SQLAlchemyError` | 500 | Otros errores de base de datos (mensaje genérico en producción). |
| `Exception` | 500 | Captura final genérica (mensaje genérico en producción). |

La capa HTTP **no contiene bloques `try`/`except`**: se limita a
delegar y permite que el manejador global componga la respuesta.

---

## Seguridad

| Medida | Implementación |
|--------|----------------|
| Hash de contraseñas | `bcrypt` 4.x con salt aleatorio (10 rondas). |
| Tokens | JWT HS256 con campos `iat` y `exp`, sin valor por defecto del secreto. |
| Autorización | Dependencias `get_current_user` y `get_current_admin`. |
| Escalada de privilegios | El registro público asigna siempre el rol `user`. |
| Auto-eliminación y auto-degradación | Bloqueadas en `UserService`. |
| CORS | Restringido a los orígenes definidos en `CORS_ORIGINS`. |
| Errores | Mensajes genéricos en producción (`APP_ENV=production`). |
| Validación | Pydantic v2 rechaza tipos, longitudes y rangos inválidos. |
| Inyección SQL | SQLAlchemy parametriza todas las consultas. |

---

## Uso de Inteligencia Artificial

La memoria completa del uso de IA —prompts clave, iteraciones,
errores y alucinaciones detectados y correcciones manuales— se
encuentra en [`backend/AI_USAGE.md`](backend/AI_USAGE.md).

Resumen ejecutivo:

- Se ha empleado **Cursor con Claude y GPT** como asistente de
  desarrollo, en ningún caso como mero generador de código.
- Se documentan **seis errores o alucinaciones** detectados durante
  el desarrollo: incompatibilidad de `passlib` con `bcrypt` 4.x,
  defectos en la separación de responsabilidades a nivel de routers,
  uso de la API de SQLAlchemy 1.4 frente a la 2.0, empleo del
  decorador `@app.on_event` ya deprecado, error en el parsing de
  `List[str]` en `pydantic-settings` que provocaba el fallo de
  arranque con un fichero `.env` real, y una dependencia con
  `yield from` con firma incorrecta. Para cada caso se justifica la
  causa raíz y se describe la corrección aplicada manualmente.
- Se distingue de forma explícita entre las contribuciones de la IA
  (código repetitivo, alias de Pydantic, primera versión del
  manejador de excepciones) y las decisiones de diseño tomadas por
  el autor (estructura de carpetas, política de seguridad en el
  login, contrato de identificadores y separación de los esquemas de
  validación entre login y registro).

---

## Frontend

El frontend es la SPA Svelte 5 desarrollada en la práctica 1, sin
modificaciones. Se ubica en `frontend/` y se conecta al backend
Python a través del proxy de Vite (puerto 5173 hacia el 3000).

Páginas principales: `Login`, `Register`, `Products`, `Cart`,
`Orders`, `Profile` y `AdminPanel`. Hace uso de las *runes* de
Svelte 5 (`$state`, `$derived` y `$effect`) y de un store de
autenticación basado en `localStorage`.

---

## Endpoints utilizados por el frontend

| Página o acción | Endpoint(s) | Roles |
|------------------|-------------|-------|
| Inicio de sesión y registro | `POST /auth/login`, `POST /auth/register` | Público |
| Perfil | `GET /auth/me`, `PUT /auth/change-password` | Usuario |
| Catálogo (lectura) | `GET /productos` | Público |
| Catálogo (CRUD) | `POST`, `PUT`, `DELETE /productos[/:id]` | Administrador |
| Carrito | `GET /api/cart`, `POST /api/cart/add`, `PUT /api/cart/update`, `DELETE /api/cart/remove/:id`, `DELETE /api/cart/clear` | Usuario |
| Pedidos propios | `GET /api/orders/my-orders`, `DELETE /api/orders/:id` | Usuario |
| Panel de administración | `GET /api/users`, `PUT /api/users/:id/role`, `DELETE /api/users/:id`, `GET /api/orders`, `PUT /api/orders/:id/status` | Administrador |

---

## Autor

Neco Martínez — Programación Web II — Práctica 2 (FastAPI y Svelte 5).
