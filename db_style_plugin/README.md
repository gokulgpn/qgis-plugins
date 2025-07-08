# Apply DB Layer Style Plugin

This QGIS plugin allows you to apply vector layer styles directly from a PostGIS database. It works with the `layer_styles` table located in the **public schema** of your database.

## 🔧 Features
- Lists all vector layers in your QGIS project
- Connects to a PostGIS database
- Fetches available QML styles from `public.layer_styles`
- Applies the selected style to the selected layer

## 🧪 Requirements
- QGIS 3.10 or newer
- psycopg2 Python package

## 🗂 Database Notes
Ensure your PostGIS database contains a `layer_styles` table in the **public schema** with columns like:
- `f_table_schema`
- `f_table_name`
- `stylename`
- `styleqml`

## 📂 Installation
1. Copy the `db_style_plugin` folder into your QGIS plugin directory:
2. Restart QGIS  
3. Enable the plugin via **Plugins → Manage and Install Plugins**

## ✍️ Author
**Gokul Gopan**  
📧 gokul.gopan@plan4better.de

## 🔐 Database Configuration

The plugin connects to your PostGIS database using the credentials hardcoded in `apply_style.py`.

To make the plugin work:
- Open `apply_style.py`
- Locate the `fetch_styles()` method
- Replace the following values with your actual database info:

```python
conn = psycopg2.connect(
    dbname='your_database_name',
    user='your_username',
    password='your_password',
    host='your_host',
    port='5432'
)
