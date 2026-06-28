# RB MySQL Mini Workbench Suite

The RB MySQL Mini Workbench Suite is a desktop-based administration tool for MySQL databases. Developed in Python using the PyQt6 graphical framework, it features a unique Neo-Brutalist user interface with custom layouts, zero-blur drop shadows, and high contrast styling. It functions as a lightweight management studio, offering local application user authentication, connection profile persistence, interactive database exploration, data table inspection, query snippet storage, query execution history, live logging, and user privilege administration.

## Core Features

### 1. Application Authentication and Security
*   **Access Control**: A local portal requires login credentials prior to entering the main dashboard.
*   **User Registration**: Support for new local user registration (storing full name, username, email, and password).
*   **Built-in Fallback**: Built-in default administration account (`admin` / `admin`) for initial configuration.
*   **Security Isolation**: The local app authentication is independent of target database authentication, providing a dual-layer security structure.

### 2. Database Connection Management
*   **Flexible Connection Configuration**: Connects to target database servers by specifying host, port, target database name, database username, and password.
*   **Connection Profile Persistence**: Saves settings locally to avoid re-entering credentials upon subsequent launches.
*   **Theme Selection**: Integrated dropdown selector allows users to choose from predefined themes (Light Mode, Purple Haze).

### 3. Interactive Database Explorer
*   **Live Schema Navigation**: A tree widget located in the sidebar pulls and renders databases, tables, and views in real-time.
*   **Context-Aware Selection**: Selecting tables or databases links directly to data viewing and command line interaction context.

### 4. Data Browser and Table Viewer
*   **Data Browsing**: View table data in an interactive tabular grid.
*   **Schema Inspection**: Review detailed column specifications including data types, nullability, keys, and default values.
*   **Metadata Statistics**: Inspect table metadata such as row counts, data length, index length, and creation timestamps.

### 5. Interactive SQL Console
*   **Interactive Input**: Command-line simulation terminal for running raw SQL statements directly.
*   **Dynamic Response Parsing**: Displays execution status, row updates, or query query outputs dynamically within a unified monospace terminal text block.

### 6. Saved Queries Repository
*   **Snippet Management**: Create, view, update, and delete reusable SQL queries.
*   **One-Click Execution**: Load any saved query directly into the execution context.
*   **Pre-Populated Diagnostics**: Ships with standard admin diagnostic queries such as `SHOW PROCESSLIST` and `SHOW DATABASES` pre-loaded.

### 7. MySQL Administration and Privilege Control
*   **User Management**: Retrieve and list database users and host origins.
*   **Privilege Granting/Revocation**: UI switches to execute standard SQL `GRANT` and `REVOKE` syntax easily.
*   **User Lifecycle Management**: Add new database users, update credentials, and drop database users directly from the workbench.

### 8. Session Logging and History Tracking
*   **Event Log Viewer**: Live, asynchronous terminal console rendering application log events.
*   **Event Severity Levels**: Categorization of actions under `SYSTEM`, `INFO`, `WARNING`, `ERROR`, and `QUERY` levels.
*   **Persistent Query History**: Automated logging of executed queries, execution durations in milliseconds, execution status, and detailed error tracking.

---

## Repository and Project Layout

The v1 project is organized into modular files separating visual presentation from configuration management and business logic:

```text
v1/
├── app/
│   ├── __init__.py
│   ├── config_helper.py
│   ├── connection_settings_dialog.py
│   ├── dashboard_page.py
│   ├── history_manager.py
│   ├── history_tab.py
│   ├── landing_page.py
│   ├── login_page.py
│   ├── logs_tab.py
│   ├── queries_manager.py
│   ├── queries_tab.py
│   ├── signup_page.py
│   ├── styles.py
│   ├── table_viewer.py
│   ├── user_manager.py
│   └── users_tab.py
├── .vscode/
│   └── settings.json
├── app_session.log
├── config.json
├── login.py
├── main.py
├── query_history.json
├── saved_queries.json
└── users
```

### Module Descriptions

*   [main.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/main.py): The primary entry point for the workbench. It initializes the `QApplication`, configures the central `QStackedWidget` container, registers view widgets, and coordinates transition logic between screens.
*   [login.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/login.py): Standalone prototype implementation of the Neo-Brutalist login card view using custom stylesheet instructions, shadow filters, and interactive widgets.
*   [app/styles.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/styles.py): The design system module containing theme definitions (`lightmode` and `purple-haze`), color variables, and the `DottedGridWidget` custom layout paint event.
*   [app/config_helper.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/config_helper.py): Manages parsing and persistence of database credentials and configuration preferences stored in `config.json`.
*   [app/user_manager.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/user_manager.py): Handles local authorization database reading and writing within the `users` credentials file.
*   [app/queries_manager.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/queries_manager.py): Handles file operations relating to saved SQL statement templates in `saved_queries.json`.
*   [app/history_manager.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/history_manager.py): Appends and loads database execution telemetry logs inside `query_history.json`.
*   [app/landing_page.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/landing_page.py): Home welcome screen welcoming application users, providing shortcuts to login or registration portals.
*   [app/login_page.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/login_page.py): Secure app login screen linked with local credentials database authentication.
*   [app/signup_page.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/signup_page.py): Account creation card supporting user registration validation rules.
*   [app/dashboard_page.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/dashboard_page.py): Central dashboard orchestrating the database explorer tree, connection handling logic, SQL terminal execution, sidebar tabs navigation, and connection dialogues.
*   [app/connection_settings_dialog.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/connection_settings_dialog.py): Configuration modal prompt to edit target MySQL database credentials, check server availability, and commit config updates.
*   [app/table_viewer.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/table_viewer.py): Displays table data records, handles pagination, inspects structural column data, and extracts server metadata stats.
*   [app/queries_tab.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/queries_tab.py): Panel to manage saved query snippets, load templates, and initiate executions.
*   [app/history_tab.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/history_tab.py): Renders historical executed queries in chronological order, showing runtimes and success margins.
*   [app/users_tab.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/users_tab.py): Interactive GUI for administering MySQL system accounts, passwords, and server privileges.
*   [app/logs_tab.py](file:///Users/benfranklin/.gemini/antigravity/scratch/RB-mini/v1/app/logs_tab.py): Asynchronous viewer logging framework reading and polling `app_session.log`.

---

## Technical Stack and Requirements

The application requires Python 3.8+ and dependencies listed below.

### Dependency Libraries

1.  **PyQt6**: Core UI library for window creation, layout management, event processing, widgets, and styles.
2.  **mysql-connector-python**: Official driver library to execute transactions, retrieve database structures, and run queries on target MySQL instances.

---

## Installation and Setup

### 1. Install Dependencies
Install the required packages using the Python Package Installer (pip):

```bash
pip install PyQt6 mysql-connector-python
```

### 2. Configure the MySQL Target Server
Ensure a target MySQL instance is running and accessible from the network host of the workbench application. The application will use local host configurations if no connection profile exists.

---

## Running the Application

1.  Navigate to the `v1` project root directory:
    ```bash
    cd v1
    ```
2.  Launch the main execution script:
    ```bash
    python main.py
    ```
3.  On the welcome landing page, choose **Login** (if you have an account) or **Sign Up** (to register).
    *   *Default Credentials*: If launching the workbench for the first time, use username `admin` and password `admin` to log in.
4.  Once in the dashboard, open the connection settings modal by clicking the gear icon (**Settings**). Input your target MySQL hostname, port, database name, and login credentials, then click **Connect** to initialize the database tree explorer.

---

## Data Models and State Persistence

The suite maintains application state, connection profiles, and metadata through local JSON files located in the project's root folder:

### config.json
Stores connection profiles and user settings.
```json
{
    "host": "localhost",
    "port": 3306,
    "database": "mysql",
    "user": "root",
    "password": "password",
    "theme": "lightmode"
}
```

### users
Stores registered local application users as list records.
```json
[
    {
        "fullname": "John Doe",
        "username": "johndoe",
        "email": "johndoe@domain.com",
        "password": "examplepassword"
    }
]
```

### saved_queries.json
Persists user-saved query definitions for future use.
```json
[
    {
        "name": "Show All Databases",
        "sql": "SHOW DATABASES;"
    }
]
```

### query_history.json
Contains history telemetry for query metrics.
```json
[
    {
        "timestamp": "2026-06-28 12:00:00",
        "sql": "SELECT * FROM mysql.user;",
        "execution_time_ms": 12,
        "status": "Success",
        "error_message": ""
    }
]
```

### app_session.log
Contains raw, time-stamped text log outputs tracking application operations and transaction warnings.