# Memoria del uso de Inteligencia Artificial — Práctica 2

> Asignatura: Programación Web II — Curso 2025/2026
> Autor: Neco Martínez
> Backend: FastAPI + SQLAlchemy + Pydantic

Este documento recoge **cómo se ha usado la IA** durante el desarrollo del
backend de la práctica 2, qué prompts fueron clave, cómo se refinaron y
qué errores o alucinaciones se detectaron y corrigieron manualmente.

La herramienta principal utilizada como asistente de programación fue
**Cursor + Claude / GPT** dentro del IDE, y en momentos puntuales
**ChatGPT** (sesión web) para contrastar dudas concretas. La IA se
empleó **como copiloto crítico**, no como generador ciego: cada
sugerencia se revisó, se contrastó con la documentación oficial y se
adaptó al contexto del proyecto (Svelte 5 + contrato JSON existente).

---

## 1. Prompts clave e iteraciones

A continuación se detallan los prompts que dispararon decisiones
importantes en el código, agrupados por tema.

### 1.1 Arquitectura limpia en FastAPI

**Prompt inicial (insuficiente):**

> "Hazme una API REST en FastAPI para productos y usuarios con
> autenticación JWT."

**Resultado de la IA:** un único archivo `main.py` con todas las rutas,
la conexión a BD, la creación del token JWT y los modelos Pydantic
mezclados. Funcional, pero exactamente lo que la práctica **prohíbe**:
toda la lógica centralizada.

**Prompt refinado (con contexto y restricciones):**

> "Necesito un backend FastAPI con **separación estricta de
> responsabilidades** en cuatro capas: `routers/` (solo manejan HTTP y
> validación con Pydantic), `services/` (lógica de negocio, lanzan
> excepciones de dominio), `repositories/` (acceso a datos con
> SQLAlchemy 2.0 estilo `select(...)`) y `models/` (ORM declarativo).
> La capa HTTP nunca debe importar SQLAlchemy directamente. La
> autenticación JWT se inyecta como dependencia (`Depends`) y devuelve
> un `CurrentUser` inmutable. La factoría de la app vive en
> `app.main:create_app()`. Genera la estructura de carpetas, no el
> código aún."

**Resultado:** un árbol de carpetas razonable que sirvió de base para
la organización final. Igualmente hubo que mover cosas a mano (p.ej.,
la IA propuso `app/db/` y `app/auth/`; preferí `app/core/` para
agrupar configuración, seguridad y BD porque son piezas
transversales).

### 1.2 Manejo global de excepciones

**Prompt inicial:**

> "¿Cómo capturo todas las excepciones en FastAPI y devuelvo un JSON
> unificado?"

**Resultado:** la IA propuso un único `@app.exception_handler(Exception)`
que devolvía siempre `500`. Era demasiado tosco: no diferenciaba
errores de validación, conflictos de integridad ni reglas de negocio.

**Prompt refinado:**

> "Diseña una jerarquía de excepciones de dominio (`DomainError`,
> `NotFoundError`, `ValidationError`, `ConflictError`,
> `AuthenticationError`, `AuthorizationError`) y registra manejadores
> en FastAPI que las traduzcan a códigos HTTP coherentes
> (404/422/409/401/403). Maneja también
> `RequestValidationError` para 422 estructurado y `IntegrityError`
> de SQLAlchemy para 409. Devuelve siempre el formato
> `{ \"error\": str, \"details\"?: list }` que ya consume el frontend
> Svelte (campo `error`)."

**Resultado:** primera versión utilizable de `app/core/exceptions.py`.
Aun así, hubo que corregir manualmente dos detalles (ver sección 2).

### 1.3 Compatibilidad de contrato con el frontend Svelte

**Prompt:**

> "El frontend Svelte ya en producción espera identificadores estilo
> Mongo (`_id`, `createdAt`, `updatedAt`) y campos en castellano
> (`nombre`, `precio`, `descripcion`). El nuevo backend usa SQLite con
> identificadores UUID en columna `id` y `created_at` / `updated_at`.
> ¿Cómo expongo el contrato anterior **sin romper el cliente** y sin
> contaminar los modelos ORM?"

**Resultado:** la IA propuso usar `alias` de Pydantic en los esquemas
de salida (`Field(alias=\"_id\")`, `Field(alias=\"createdAt\")`) con
`populate_by_name=True`. Esto resultó ser exactamente la solución
limpia: el ORM mantiene la convención Python (`snake_case`) y la capa
de presentación traduce a la convención del cliente. Quedó plasmado en
`app/schemas/common.py` con las clases base `MongoCompatModel` y
`TimestampedModel`.

### 1.4 Hash de contraseñas

**Prompt inicial:**

> "Implementa hashing de contraseñas con passlib + bcrypt en FastAPI."

**Resultado:** la IA generó código basado en `passlib.context.CryptContext`
con `schemes=["bcrypt"]`. Funcionaba, pero al ejecutar pip salía un
*warning* conocido (`AttributeError: module 'bcrypt' has no attribute
'__about__'`) por la incompatibilidad entre `passlib 1.7.4` y `bcrypt
>= 4.x`.

**Corrección manual:** sustituí `passlib` por el uso directo del
módulo `bcrypt` (ver `app/core/security.py`). Es más simple, una
dependencia menos y elimina el warning. Esta es una de las
**alucinaciones documentadas** en la sección 2.

### 1.5 Validación estricta vs. login

**Prompt:**

> "Quiero validación estricta con Pydantic (`min_length=6` en
> contraseñas, `min_length=3` en username) en el registro, pero el
> endpoint de login no debe rechazar contraseñas cortas con 422
> (debe devolver siempre 401 con mensaje genérico para no filtrar si
> existe el usuario)."

**Resultado:** la IA propuso dos esquemas distintos
(`RegisterCredentials`, `LoginCredentials`). Solución correcta y
adoptada tal cual.

---

## 2. Análisis crítico: errores y alucinaciones detectados

### 2.1 Alucinación: `passlib` + `bcrypt 4.x`

**Lo que generó la IA:**

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd_context.hash(p)
```

**Por qué era incorrecto:**

1. `passlib 1.7.4` (la versión "estable" desde 2020) **no es
   compatible** con `bcrypt >= 4.x`. Al cargar el módulo dispara un
   *warning* y, en algunos entornos, un fallo silencioso. Es un caso
   muy documentado en GitHub y Stack Overflow.
2. La IA recomendó pinear `bcrypt<4` para evitarlo, lo cual significa
   quedarse en una versión sin parches de seguridad. Eso convierte la
   "solución" en un fallo de **seguridad**: un alumno copiando
   ciegamente el snippet acabaría con una dependencia obsoleta sin
   saberlo.

**Cómo se corrigió:**

Eliminé `passlib` y usé el paquete `bcrypt 4.x` directamente:

```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
```

Es la API oficial del paquete `bcrypt`, una dependencia menos y resuelve
el problema. La salt aleatoria por contraseña sigue garantizada (lo
hace `gensalt`), y `checkpw` es *constant-time*.

### 2.2 Error de separación de responsabilidades: validar en el router

En la primera iteración, la IA puso la regla "no puedes cambiar tu
propio rol" directamente dentro del *router* de usuarios:

```python
@router.put("/{user_id}/role")
def update_role(user_id, payload, current=Depends(get_current_admin)):
    if user_id == current.id:
        raise HTTPException(400, "No puedes cambiar tu propio rol")
    ...
```

**Por qué era subóptimo:**

- Esa regla es **lógica de negocio**, no manejo HTTP. Pertenece a la
  capa de servicios, no a la capa de presentación.
- Mezclar reglas en el router obliga a duplicarla si mañana hay otro
  endpoint (CLI, GraphQL, tarea programada) que toque el mismo caso de
  uso.
- El router empieza a saber demasiado sobre el dominio (concepto de
  "el usuario que pide" vs "el usuario que se modifica").

**Cómo se corrigió:**

La regla se movió a `UserService.update_role`, que lanza una
`ValidationError` del dominio. El router solo traduce la petición HTTP
y delega:

```python
def update_role(self, *, user_id, role, requester_id):
    if user_id == requester_id:
        raise ValidationError("No puedes cambiar tu propio rol")
    ...
```

Y el manejador global `_handle_domain_error` traduce la excepción a
`422` automáticamente.

### 2.3 Alucinación menor: `from sqlalchemy.ext.declarative import declarative_base`

La IA, por inercia con tutoriales antiguos, sugirió usar
`declarative_base()` y `Column(Integer, primary_key=True)` como en
SQLAlchemy 1.4.

**Por qué no era óptimo:** SQLAlchemy 2.0 introdujo
`DeclarativeBase` + `Mapped[...]` + `mapped_column(...)` con tipado
estricto (`PEP 484`). Es la API recomendada actualmente y se integra
mucho mejor con Pydantic y con el chequeo estático.

**Corrección manual:** todos los modelos (`User`, `Product`, `Cart`,
`Order`) se reescribieron con el estilo 2.0, p.ej.:

```python
class User(Base):
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_id)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum=False))
```

Esto da autocompletado correcto en el IDE y permite a `mypy` detectar
errores de tipo antes de ejecutar.

### 2.4 Alucinación: `@app.on_event("startup")` deprecado

La IA usó `@app.on_event("startup")` para crear las tablas. Funciona,
pero está **deprecado** desde FastAPI 0.93. Lo correcto es usar el
parámetro `lifespan` con un context manager async, que además garantiza
ejecución correcta de la fase de apagado.

**Corrección manual:** ver `app/main.py`, función `lifespan`.

### 2.5 Alucinación: tipo de retorno equivocado en dependencia

La IA primero escribió la dependencia de sesión así:

```python
def get_db_session() -> Session:
    yield from get_db()
```

Esto no funciona en FastAPI: una dependencia con `yield` debe ser
**ella misma** un generador (no llamar a `yield from`). El tipo de
retorno además debería ser `Generator[Session, None, None]`. Lo
identifiqué al pasar el linter / al pensar que la firma era
incoherente y eliminé la función redundante (basta con `get_db`).

---

## 3. Lecciones extraídas

1. **Dar contexto y restricciones explícitas multiplica la calidad
   del código generado.** El primer prompt "hazme una API" produjo
   código no aceptable; el prompt detallado (capas, contrato JSON,
   estilo SQLAlchemy 2.0, política de errores) produjo una base sólida.
2. **La IA tira a soluciones populares pero no necesariamente
   actuales.** Repetidamente sugirió `passlib`, `declarative_base`,
   `@app.on_event` — todos válidos en 2021, todos subóptimos en 2026.
   Hay que contrastar siempre con la documentación oficial del año en
   curso.
3. **La separación de responsabilidades es responsabilidad del
   humano.** La IA tiende a "resolver" cada caso de uso de forma
   imperativa donde está pisando código. Hay que insistirle en mover
   reglas a la capa correcta.
4. **Lo más útil de la IA fue acelerar tareas mecánicas**: generar el
   boilerplate de los esquemas Pydantic con alias, escribir el primer
   borrador del manejador global de excepciones, traducir comentarios.
   Las decisiones de diseño y la verificación funcional fueron mías.
