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
├── ruff.toml                    # Configuración de ruff (linting rápido)
├── .github/
│   └── workflows/
│       ├── ci.yml               # Pipeline CI: lint → security → tests
│       └── cd.yml               # Pipeline CD: build → deploy por ambiente
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

El proyecto usa **GitHub Actions** con dos pipelines independientes: `ci.yml` para validación continua y `cd.yml` para despliegue por ambiente.

### Estrategia de ramas

| Rama | Ambiente | Aprobación manual |
|---|---|---|
| `develop` | Dev | No |
| `staging` | Staging | Sí |
| `main` | Production | Sí |

---

### Pipeline CI (`ci.yml`)

Se ejecuta en **pull requests** y en **pushes a ramas de feature** (cualquier rama que no sea `main`, `staging` ni `develop`). Sirve como gate de calidad antes de hacer merge.

```
push / PR
    ├── lint       (paralelo)
    ├── security   (paralelo)
    └── test       (paralelo)
```

#### Job: `lint`

Ejecuta [`ruff`](https://docs.astral.sh/ruff/) sobre todo el código fuente.

- **Qué verifica:** estilo PEP8, imports no usados, variables sin referenciar, y otras reglas de calidad configuradas en `ruff.toml` (line-length 120).
- **Falla si:** hay alguna violación de estilo. La salida se formatea con anotaciones nativas de GitHub para que aparezcan en línea en el PR.

#### Job: `security`

Ejecuta dos herramientas en secuencia:

1. **`bandit`** — análisis estático de seguridad del código Python. Detecta patrones inseguros como uso de `eval`, `subprocess` sin sanitizar, hardcoded passwords, etc. Solo reporta severidad media-alta (`-ll`).
2. **`pip-audit`** — audita las dependencias de `requirements.txt` contra la base de datos de vulnerabilidades de PyPI (OSV). Falla si alguna dependencia tiene un CVE conocido.

#### Job: `test`

Ejecuta la suite completa de pruebas unitarias con `pytest`.

- Instala dependencias de producción y desarrollo.
- Genera tres reportes de cobertura: consola, `coverage.xml` (para integraciones) y `htmlcov/` (navegable).
- **Falla si:** algún test no pasa o la cobertura cae por debajo del **80%** (configurado en `pytest.ini`).
- Sube los reportes como artefactos de GitHub Actions (disponibles 1 día para descarga).

---

### Pipeline CD (`cd.yml`)

Se ejecuta solo en **push a `develop`, `staging` o `main`**. Primero repite los jobs de CI como gate y luego construye y despliega.

```
push a develop / staging / main
    ├── lint     ─┐
    ├── security  ├─ (paralelo, mismas validaciones que CI)
    ├── test     ─┘
    │
    └── build (solo si los 3 anteriores pasan)
         │
         ├── deploy-dev      (solo si rama = develop)
         ├── deploy-staging  (solo si rama = staging,  con aprobación)
         └── deploy-prod     (solo si rama = main,     con aprobación)
```

#### Job: `build`

Prepara el artefacto de despliegue que luego comparten los tres jobs de deploy.

1. Instala las dependencias de producción en `.python_packages/lib/site-packages/` — el directorio que Azure Functions espera para encontrar los paquetes sin ejecutar `pip install` en el servidor.
2. Empaqueta el código fuente excluyendo carpetas innecesarias (`.venv`, `.git`, `htmlcov`, `tests`, `__pycache__`).
3. Sube el artefacto comprimido a GitHub Actions (`function-app`) con retención de 1 día.

#### Jobs: `deploy-dev` / `deploy-staging` / `deploy-prod`

Los tres jobs siguen el mismo proceso; solo difieren en el ambiente de GitHub que referencian:

1. **Descarga el artefacto** generado en el job `build`.
2. **Autentica con Azure** usando `azure/login@v2` con las credenciales del Service Principal almacenadas en el secret `AZURE_CREDENTIALS` del ambiente correspondiente.
3. **Despliega a Azure Functions** con `azure/functions-action@v1`. El parámetro `scm-do-build-during-deployment: false` indica que los paquetes ya están instalados en `.python_packages/` y no es necesario que el servidor los reinstale (despliegue más rápido y predecible).

Los ambientes `staging` y `production` tienen **protection rules** en GitHub que exigen aprobación manual antes de ejecutar el deploy.

---

### Configuración inicial en GitHub

Sigue estos pasos una sola vez para dejar el pipeline funcional.

#### Paso 1 — Crear el Service Principal en Azure

Por cada ambiente, crea un Service Principal con permisos sobre el Resource Group donde vive la Function App:

```bash
az ad sp create-for-rbac \
  --name "github-actions-<proyecto>-<ambiente>" \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP> \
  --json-auth
```

Guarda el JSON completo que devuelve el comando — ese es el valor de `AZURE_CREDENTIALS`.

> Crea un Service Principal separado por ambiente para seguir el principio de mínimo privilegio. El de `dev` solo tiene acceso al RG de dev, el de `prod` solo al de producción.

#### Paso 2 — Crear los Environments en GitHub

En el repositorio, ve a **Settings → Environments** y crea tres environments:

| Environment | Protection rules |
|---|---|
| `dev` | Ninguna — el deploy es automático |
| `staging` | Activar **Required reviewers** y agregar al menos un aprobador |
| `production` | Activar **Required reviewers** y agregar al menos un aprobador |

#### Paso 3 — Agregar Secrets en cada Environment

Dentro de cada environment, agrega estos dos secrets:

| Secret | Valor |
|---|---|
| `AZURE_CREDENTIALS` | JSON completo del `az ad sp create-for-rbac` del ambiente correspondiente.|
| `AZURE_FUNCTIONAPP_NAME` | Nombre de la Function App en Azure para ese ambiente (ej. `func-boilerplate-dev`) |

 
```bash
Ejemplo de JSON para AZURE_CREDENTIALS:

{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "..."
}
```

> Los secrets se configuran **por environment**, no a nivel de repositorio, para que las credenciales de producción nunca sean accesibles desde un job de dev.


#### Paso 4 — Verificar el primer despliegue

1. Crea una rama desde `develop`, haz un cambio y abre un PR → el pipeline `ci.yml` debe ejecutarse y pasar.
2. Haz merge del PR a `develop` → el pipeline `cd.yml` debe ejecutarse y desplegar a dev automáticamente.
3. Para staging y producción, el pipeline quedará en estado **"Waiting"** hasta que un aprobador autorice el deploy desde la UI de GitHub Actions.
