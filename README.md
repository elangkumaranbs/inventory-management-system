# Inventory Management System

A comprehensive Flask-based inventory management system for tracking products, locations, and stock movements with real-time reporting capabilities.

## 🚀 Features

### Core Functionality
- **Product Management**: Create, edit, and delete products with unique IDs and descriptions
- **Location Management**: Manage storage locations and warehouses
- **Movement Tracking**: Track inventory movements between locations with detailed history
- **Real-time Inventory**: Automatic calculation of stock levels across all locations
- **Comprehensive Reports**: Visual reports with charts showing inventory distribution

### Key Capabilities
- ✅ **Real-time Stock Calculation**: Automatic calculation of product balances at each location
- ✅ **Movement History**: Complete audit trail of all inventory movements
- ✅ **Multi-location Support**: Manage inventory across multiple warehouses/locations
- ✅ **Data Validation**: Prevents negative stock and invalid movements
- ✅ **Responsive Design**: Works on desktop and mobile devices
- ✅ **Interactive Charts**: Visual representation of inventory data using Chart.js

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Charts**: Chart.js for data visualization
- **Icons**: Bootstrap Icons

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/inventory-management-system.git
   cd inventory-management-system
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\\Scripts\\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your web browser and navigate to `http://localhost:5000`

## 📱 Application Screens

> **Note**: Screenshots will be added to the `/screenshots` folder to showcase the application interface. To add screenshots, run the application and capture images of each screen, then place them in the `screenshots` directory and update this README to reference them.

### Dashboard
The main dashboard provides an overview of your inventory system with key statistics:
- Total number of products
- Number of storage locations
- Total inventory movements
- Count of items currently in stock

<!-- Screenshot placeholder: ![Dashboard](screenshots/dashboard.png) -->

### Products Management
- **Add Products**: Create new products with unique IDs, names, and descriptions
- **Edit Products**: Modify existing product information
- **Delete Products**: Remove products (with safety checks for existing movements)
- **View All Products**: List all products with current stock levels

<!-- Screenshot placeholders:
![Products List](screenshots/products.png)
![Add Product](screenshots/add-product.png)
![Edit Product](screenshots/edit-product.png)
-->

### Locations Management
- **Add Locations**: Create new storage locations and warehouses
- **Edit Locations**: Modify location details
- **Delete Locations**: Remove locations (with safety checks)
- **View All Locations**: List all storage locations

<!-- Screenshot placeholders:
![Locations List](screenshots/locations.png)
![Add Location](screenshots/add-location.png)
![Edit Location](screenshots/edit-location.png)
-->

### Movements Management
- **Add Movements**: Record inventory movements between locations
- **Edit Movements**: Modify existing movement records
- **Delete Movements**: Remove movement records
- **Movement History**: Complete audit trail of all inventory transactions
- **Clear All Movements**: Bulk delete option with confirmation

<!-- Screenshot placeholders:
![Movements List](screenshots/movements.png)
![Add Movement](screenshots/add-movement.png)
![Edit Movement](screenshots/edit-movement.png)
-->

### Reports
- **Inventory Distribution**: Visual charts showing product distribution across locations
- **Stock Levels**: Current stock levels for all products
- **Location Summary**: Inventory summary by location

<!-- Screenshot placeholder: ![Reports](screenshots/reports.png) -->

## 🗄️ Database Schema

### Products Table
- `product_id` (Primary Key): Unique product identifier
- `name`: Product name
- `description`: Product description
- `total_qty`: Total quantity across all locations

### Locations Table
- `location_id` (Primary Key): Unique location identifier
- `name`: Location name
- `description`: Location description

### Product Movements Table
- `movement_id` (Primary Key): Auto-increment ID
- `product_id`: Foreign key to Products
- `from_location`: Source location (nullable for incoming stock)
- `to_location`: Destination location (nullable for outgoing stock)
- `qty`: Movement quantity
- `timestamp`: Movement date and time
- `notes`: Optional movement notes

## 🔧 Configuration

The application uses the following default configurations:

```python
SECRET_KEY = 'dev-secret-key-change-in-production'
SQLALCHEMY_DATABASE_URI = 'sqlite:///inventory.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

For production deployment, make sure to:
- Change the SECRET_KEY to a secure random value
- Use a production database (PostgreSQL, MySQL, etc.)
- Set environment variables for sensitive configurations

## 📊 API Endpoints

- `GET /` - Dashboard
- `GET /products` - Products list
- `POST /products/add` - Add new product
- `POST /products/edit/<product_id>` - Edit product
- `POST /products/delete/<product_id>` - Delete product
- `GET /locations` - Locations list
- `POST /locations/add` - Add new location
- `POST /locations/edit/<location_id>` - Edit location
- `POST /locations/delete/<location_id>` - Delete location
- `GET /movements` - Movements list
- `POST /movements/add` - Add new movement
- `POST /movements/edit/<movement_id>` - Edit movement
- `POST /movements/delete/<movement_id>` - Delete movement
- `GET /reports` - Reports page
- `GET /api/inventory-data` - JSON API for inventory data

## 🚀 Production Deployment

For production deployment:

1. **Use a production WSGI server**
   ```bash
   gunicorn app:app
   ```

2. **Environment Variables**
   Create a `.env` file:
   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=your-database-url-here
   FLASK_ENV=production
   ```

3. **Database Migration**
   For production, consider using Flask-Migrate for database versioning

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

If you encounter any issues or have questions, please create an issue on the GitHub repository.

## 🔄 Version History

- **v1.0.0** - Initial release with core inventory management features
  - Product management
  - Location management
  - Movement tracking
  - Real-time reporting
  - Responsive web interface

---

**Built with ❤️ using Flask and Python**