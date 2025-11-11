# KitchenSmartInventory API

Welcome to the KitchenSmartInventory API project. This is a backend API (built with FastAPI) to manage home kitchen inventory (fridge, pantry, etc.) and, in the future, generate smart shopping lists.

---

## 🛠️ Technology Stack

- **Framework:** **FastAPI**
- **Database:** **SQLite** (for development, `database.db`)
- **ORM / Validation:** **SQLModel** (combines Pydantic and SQLAlchemy)
- **Server:** **Uvicorn**
- **Linting/Formatting:** **Flake8** & **Black**
- **Project Management:** **`CONTEXT.md`** (as the "single source of truth")

---

## 🧭 Project Status (v0.2)

### ✅ v0.1: Foundations (Completed)

Version 0.1 focused on building the application's foundation, data models, and basic configuration modules.

- **[✓] Phase 1: Setup:** Environment, `venv`, `gitignore`, and dependencies.
- **[✓] Phase 2: Data Models:** Defined all tables in `src/models.py` (`Location`, `Store`, `Product`, `InventoryItem`).
- **[✓] Phase 3: `Location` Module:** Full CRUD (Service + API: `POST` & `GET /locations`).
- **[✓] Phase 4: `Store` Module:** Full CRUD (Service + API: `POST` & `GET /stores`).

### 🚀 v0.2: Core Features (In Progress)

Version 0.2 implements the core business logic of the application.

- **[ ] Phase 2.5 (Refactor):** Add timestamp fields (`created_at`, `updated_at`) to all models.
- **[ ] Phase 5 (Products):** Implement the product catalog management module (`/products`).
- **[ ] Phase 6 (Inventory):** Implement the inventory stock management module (`/inventory_items`).
- **[ ] Phase 7 (Shopping List):** Implement the manual shopping list module (`/shopping-list`).
- **[ ] Phase 8 (Technical Debt):** Clean up dependencies (`requirements.txt`).

---

## ⚙️ Running the Project

1.  Ensure you have Python 3.11+.
2.  Clone the repository.
3.  Create and activate a virtual environment:
    ```shell
    python -m venv .venv
    .\.venv\Scripts\activate
    ```
4.  Install dependencies (using the "polluted" file for now):
    ```shell
    pip install -r requirements.txt
    ```
5.  Run the development server from the root folder:
    ```shell
    uvicorn src.main:app --reload
    ```
6.  Open the auto-generated API documentation (Swagger UI) in your browser:
    **`http://127.0.0.1:8000/docs`**