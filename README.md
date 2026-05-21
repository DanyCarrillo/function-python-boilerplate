# Azure Function Python Boilerplate

Boilerplate para Azure Functions con Python siguiendo **arquitectura hexagonal (ports & adapters)**, código limpio (PEP8) y cobertura de pruebas unitarias configurable (mínimo 80%).

Incluye integración lista para usar con los siguientes servicios de Azure y Microsoft:

| Integración | Paquete |
|---|---|
| Azure Blob Storage | `azure-storage-blob` |
| Azure CosmosDB | `azure-cosmos` |
| Azure AI Search | `azure-search-documents` |
| Azure OpenAI | `openai` |
| Azure Document Intelligence | `azure-ai-documentintelligence` |
| Azure AI Foundry | `azure-ai-inference` |
| Azure Communication Service (Email + SMS) | `azure-communication-email`, `azure-communication-sms` |
| Microsoft Graph API | `msal`, `requests` |

---

## Prerequisitos

### Herramientas

| Herramienta | Versión mínima | Instalación |
|---|---|---|
| Python | 3.11 | [python.org](https://www.python.org/downloads/) |
| Azure Functions Core Tools | v4 | `npm install -g azure-functions-core-tools@4` |
| Azure CLI | Última | [docs.microsoft.com](https://learn.microsoft.com/cli/azure/install-azure-cli) |
| Azurite (emulador local) | Última | `npm install -g azurite` |

### Extensiones de VS Code recomendadas

- Azure Functions
- Python
- Pylance

---

## Configuración local

### 1. Clonar el repositorio e instalar dependencias

```bash
git clone <repo-url>
cd function-python-boilerplate

python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt -r requirements-dev.txt
```

### 2. Configurar variables de entorno

```bash
cp local.settings.json.example local.settings.json
# Editar local.settings.json con los valores reales de cada servicio
```

> `local.settings.json` está en `.gitignore`. Nunca lo subas al repositorio.

### 3. Iniciar el emulador de Storage (Azurite)

```bash
azurite --silent --location .azurite --debug .azurite/debug.log
```

### 4. Ejecutar la función en local

```bash
func start
```

La función estará disponible en `http://localhost:7071/api/boilerplate`.

### 5. Ejecutar las pruebas

```bash
pytest --cov-report=html
```

El reporte de cobertura se genera en `coverage.xml` y se muestra en consola. La cobertura mínima aceptada es **80%** (configurable en `pytest.ini` → `--cov-fail-under`).

---

## Estructura del proyecto

```
function-python-boilerplate/
├── function_app.py              # Entry point de Azure Function (HTTP trigger)
├── host.json                    # Configuración del runtime de Azure Functions
├── local.settings.json.example  # Plantilla de variables de entorno locales
├── .env.example                 # Plantilla alternativa de variables de entorno
├── requirements.txt             # Dependencias de producción
├── requirements-dev.txt         # Dependencias de desarrollo y testing
├── pytest.ini                   # Configuración de pytest y cobertura
├── setup.cfg                    # Configuración de flake8 (linting PEP8)
├── .gitlab-ci.yml               # Pipeline CI/CD: lint → test → deploy
└── src/
    ├── domain/                  # Capa de dominio
    ├── ports/                   # Puertos (contratos abstractos)
    ├── adapters/                # Adaptadores (implementaciones)
    ├── application/             # Capa de aplicación (casos de uso)
    └── infrastructure/          # Configuración e inyección de dependencias
```

---

## Arquitectura hexagonal: guía de capas

### `src/domain/` — Dominio

Es el **núcleo de la aplicación**. Contiene la lógica de negocio pura, sin ninguna dependencia hacia servicios externos, frameworks ni SDKs de Azure.

**Qué va aquí:**
- **`entities/`** — Objetos del dominio que representan conceptos del negocio (ej. `DocumentEntity`). Usan `dataclass` o clases simples. No heredan de ningún framework.
- **`exceptions/`** — Excepciones propias del dominio (ej. `EntityNotFoundException`, `ValidationException`). Permiten comunicar errores de negocio sin exponer detalles de infraestructura.

**Qué NO va aquí:**
- Llamadas a SDKs de Azure, bases de datos, HTTP o cualquier servicio externo.
- Lógica de serialización/deserialización de protocolos específicos.

---

### `src/ports/` — Puertos

Define los **contratos (interfaces abstractas)** que la capa de aplicación necesita para interactuar con el mundo exterior. Cada puerto es una clase abstracta (`ABC`) con métodos abstractos.

**Qué va aquí:**
- Una clase abstracta por cada servicio externo (ej. `BlobStoragePort`, `CosmosdbPort`).
- Solo la firma de los métodos — sin implementación.
- Tipos del dominio o tipos primitivos de Python como parámetros y retornos.

**Qué NO va aquí:**
- Imports de SDKs de Azure u otras librerías externas.
- Lógica condicional ni implementaciones concretas.

**Por qué importa:** permiten reemplazar cualquier adaptador (ej. cambiar CosmosDB por Postgres) sin tocar la capa de aplicación, y facilitan el mock en pruebas unitarias.

---

### `src/adapters/` — Adaptadores

Contiene las **implementaciones concretas** de cada puerto. Cada adaptador hereda del puerto correspondiente e integra el SDK real del servicio.

**Qué va aquí:**
- Una clase concreta por puerto (ej. `CosmosdbAdapter(CosmosdbPort)`).
- Toda la lógica de conexión, inicialización del cliente y manejo de errores del SDK.
- Logging de errores antes de re-lanzar excepciones.

**Qué NO va aquí:**
- Lógica de negocio — el adaptador solo traduce entre el contrato del puerto y la API del SDK.
- Estado compartido entre requests (los clientes se instancian en `__init__`).

---

### `src/application/` — Aplicación (Casos de uso)

Orquesta el flujo de negocio **coordinando el dominio y los puertos**. Es la capa que implementa los casos de uso concretos de la función.

**Qué va aquí:**
- Servicios de aplicación (ej. `BoilerplateService`) que reciben los puertos por inyección de dependencias en `__init__`.
- Métodos que representan casos de uso (ej. `process_document`, `send_notification`).
- Transformación de datos entre capas cuando es necesario.

**Qué NO va aquí:**
- Imports de SDKs ni adaptadores concretos — solo tipos de los puertos.
- Lógica HTTP (status codes, parsing de requests) — eso va en `function_app.py`.

---

### `src/infrastructure/` — Infraestructura

Contiene el **pegamento** que conecta todas las capas: configuración y ensamblado de dependencias.

**Qué va aquí:**
- **`config.py`** — Lee todas las variables de entorno al inicio. Falla rápido con `KeyError` si falta alguna, evitando errores silenciosos en runtime.
- **`container.py`** — Instancia los adaptadores de forma lazy (singleton) y los ensambla en los servicios de aplicación. Es el único lugar donde se importan adaptadores concretos.

**Qué NO va aquí:**
- Lógica de negocio ni llamadas a servicios externos directamente.

---

### `function_app.py` — Entry point

Es la **puerta de entrada HTTP** de Azure Functions. Su única responsabilidad es parsear el request, llamar al servicio de aplicación y formatear la respuesta.

**Qué va aquí:**
- Decoradores de Azure Functions (`@app.route`, `@app.timer_trigger`, etc.).
- Validación básica de parámetros de entrada.
- Formateo de respuestas HTTP (status codes, JSON).
- Instanciación del `Container` (una sola vez al arrancar la función, fuera del handler).

**Qué NO va aquí:**
- Lógica de negocio — delega siempre al servicio de aplicación del container.

---

## Variables de entorno

| Variable | Descripción |
|---|---|
| `BLOB_CONNECTION_STRING` | Connection string de Azure Blob Storage |
| `COSMOS_CONNECTION_STRING` | Connection string de Azure CosmosDB |
| `COSMOS_DATABASE` | Nombre de la base de datos en CosmosDB |
| `COSMOS_CONTAINER` | Nombre del contenedor en CosmosDB |
| `SEARCH_ENDPOINT` | URL del servicio Azure AI Search |
| `SEARCH_API_KEY` | API Key de Azure AI Search |
| `SEARCH_INDEX` | Nombre del índice de búsqueda |
| `OPENAI_ENDPOINT` | URL del recurso Azure OpenAI |
| `OPENAI_API_KEY` | API Key de Azure OpenAI |
| `OPENAI_API_VERSION` | Versión de la API (default: `2024-02-01`) |
| `OPENAI_CHAT_MODEL` | Nombre del deployment del modelo de chat |
| `OPENAI_EMBEDDING_MODEL` | Nombre del deployment del modelo de embeddings |
| `DOC_INTELLIGENCE_ENDPOINT` | URL de Azure Document Intelligence |
| `DOC_INTELLIGENCE_API_KEY` | API Key de Azure Document Intelligence |
| `AI_FOUNDRY_ENDPOINT` | URL del endpoint de Azure AI Foundry |
| `AI_FOUNDRY_API_KEY` | API Key de Azure AI Foundry |
| `AI_FOUNDRY_MODEL` | Nombre del modelo desplegado en AI Foundry |
| `ACS_CONNECTION_STRING` | Connection string de Azure Communication Service |
| `GRAPH_TENANT_ID` | Tenant ID de Azure AD para Microsoft Graph |
| `GRAPH_CLIENT_ID` | Client ID de la app registrada en Azure AD |
| `GRAPH_CLIENT_SECRET` | Client Secret de la app registrada en Azure AD |

---

## Pipeline CI/CD

El archivo `.gitlab-ci.yml` define tres etapas:

| Etapa | Descripción |
|---|---|
| `lint` | Ejecuta `flake8` sobre `src/` y `function_app.py` |
| `test` | Ejecuta `pytest` con reporte de cobertura (mínimo 80%) |
| `deploy-dev` | Deploy automático a Azure al hacer push a `develop` |
| `deploy-prod` | Deploy manual a Azure al hacer push a `main` |

Para el deploy, configurar las variables de CI/CD `AZURE_FUNCTION_APP_NAME_DEV` y `AZURE_FUNCTION_APP_NAME_PROD` en GitLab.
