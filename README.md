# KitchenSmartInventory API

Welcome to the KitchenSmartInventory project. This is a back-end API built with FastAPI to manage kitchen inventory (fridge, pantry, etc.) and generate smart shopping lists.

This project is developed following the own framework, focusing on clean architecture, testability, and step-by-step learning.

---

## 🚀 v0.1: Core Logic (MVP)

The goal of version 0.1 is to build the fundamental business logic for the application, assuming a single-user context.

### Features (v0.1)

- **Product Definitions:** Define base products (e.g., "Milk 3.2%").
- **Locations:** Manage different storage locations (e.g., "Fridge", "Pantry", "Freezer").
- **Stores:** Manage stores where items are purchased (e.g., "Lidl", "Local Market").
- **Inventory Management:** Track items in specific locations (what, how much, where).
  - Includes timestamps (`created_at`, `updated_at`) for future analysis.
  - Includes the store where the item was last purchased.
- **Shopping List:** Manually manage a shopping list (add/remove items).

### Features (v0.2 - Planned)

- **User Authentication:** Full user login, registration, and password management (JWT).
- **Automated Lists:** Automatically move items to the shopping list when inventory is low.
- **Analytics:** Basic patterns on user consumption.

---

## 🛠️ Technology Stack

- **Framework:** **FastAPI**
- **Database:** **SQLite** (for v0.1, suitable for development)
- **ORM / Validation:** **SQLModel** (combines Pydantic and SQLAlchemy)
- **Server:** **Uvicorn**
- **Linting/Formatting:** **Flake8** & **Black**

## ⚙️ Project Setup

1.  Clone the repository:
    `git clone [YOUR_REPO_URL]`
2.  Navigate to the project directory:
    `cd KitchenSmartInventory`
3.  Create a virtual environment:
    `python -m venv .venv`
4.  Activate the environment:
    `.venv\Scripts\activate`
5.  Install dependencies:
    `pip install -r requirements.txt` (Note: We will create this file soon)
