from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Product, Location, ProductMovement
from datetime import datetime

main = Blueprint('main', __name__)

# Home page
@main.route('/')
def index():
    # Get quick stats for dashboard
    products_count = Product.query.count()
    locations_count = Location.query.count()
    movements_count = ProductMovement.query.count()
    
    # Count inventory items (products with stock in any location)
    inventory_items = 0
    products = Product.query.all()
    locations = Location.query.all()
    
    for product in products:
        for location in locations:
            if product.get_balance_at_location(location.location_id) != 0:
                inventory_items += 1
                break  # Count each product only once
    
    return render_template('index.html', 
                         products_count=products_count,
                         locations_count=locations_count,
                         movements_count=movements_count,
                         inventory_items=inventory_items)

# Product routes
@main.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@main.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_id = request.form['product_id']
        name = request.form['name']
        description = request.form['description']
        initial_qty = int(request.form.get('initial_qty', 0))
        
        # Check if product_id already exists
        if Product.query.filter_by(product_id=product_id).first():
            flash('Product ID already exists!', 'error')
            return render_template('add_product.html')
        
        # Validate initial quantity
        if initial_qty < 0:
            flash('Initial quantity cannot be negative!', 'error')
            return render_template('add_product.html')
        
        product = Product(product_id=product_id, name=name, description=description, total_qty=initial_qty)
        db.session.add(product)
        db.session.commit()
        
        flash(f'Product added successfully with {initial_qty} units in stock!', 'success')
        return redirect(url_for('main.products'))
    
    return render_template('add_product.html')

@main.route('/products/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        old_qty = product.total_qty
        new_name = request.form['name']
        new_description = request.form['description']
        new_total_qty = int(request.form.get('total_qty', 0))
        
        # Validate new quantity
        if new_total_qty < 0:
            flash('Total quantity cannot be negative!', 'error')
            return render_template('edit_product.html', product=product)
        
        # Update product details
        product.name = new_name
        product.description = new_description
        product.total_qty = new_total_qty
        
        db.session.commit()
        
        # Provide feedback about quantity changes
        if new_total_qty != old_qty:
            qty_change = new_total_qty - old_qty
            if qty_change > 0:
                flash(f'Product updated successfully! Added {qty_change} units (now {new_total_qty} total).', 'success')
            else:
                flash(f'Product updated successfully! Removed {abs(qty_change)} units (now {new_total_qty} total).', 'success')
        else:
            flash('Product updated successfully!', 'success')
            
        return redirect(url_for('main.products'))
    
    return render_template('edit_product.html', product=product)

@main.route('/products/delete/<product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    try:
        # Check if product has movements
        movements = ProductMovement.query.filter_by(product_id=product_id).all()
        movements_count = len(movements)
        
        if movements:
            # Reverse stock changes for all movements of this product
            for movement in movements:
                movement.reverse_stock_changes()
            
            # Delete all movements for this product
            ProductMovement.query.filter_by(product_id=product_id).delete()
        
        # Now delete the product
        product_name = product.name
        db.session.delete(product)
        db.session.commit()
        
        if movements_count > 0:
            flash(f'Product "{product_name}" and {movements_count} related movements deleted successfully!', 'success')
        else:
            flash(f'Product "{product_name}" deleted successfully!', 'success')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')
    
    return redirect(url_for('main.products'))

# Location routes
@main.route('/locations')
def locations():
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@main.route('/locations/add', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        location_id = request.form['location_id']
        name = request.form['name']
        address = request.form['address']
        
        # Check if location_id already exists
        if Location.query.filter_by(location_id=location_id).first():
            flash('Location ID already exists!', 'error')
            return render_template('add_location.html')
        
        location = Location(location_id=location_id, name=name, address=address)
        db.session.add(location)
        db.session.commit()
        flash('Location added successfully!', 'success')
        return redirect(url_for('main.locations'))
    
    return render_template('add_location.html')

@main.route('/locations/edit/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    
    if request.method == 'POST':
        location.name = request.form['name']
        location.address = request.form['address']
        db.session.commit()
        flash('Location updated successfully!', 'success')
        return redirect(url_for('main.locations'))
    
    return render_template('edit_location.html', location=location)

@main.route('/locations/delete/<location_id>', methods=['POST'])
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    
    try:
        # Check if location has movements (either as from_location or to_location)
        movements_from = ProductMovement.query.filter_by(from_location=location_id).all()
        movements_to = ProductMovement.query.filter_by(to_location=location_id).all()
        all_movements = movements_from + movements_to
        movements_count = len(all_movements)
        
        if all_movements:
            # Reverse stock changes for all movements involving this location
            for movement in all_movements:
                movement.reverse_stock_changes()
            
            # Delete all movements involving this location
            ProductMovement.query.filter(
                (ProductMovement.from_location == location_id) | 
                (ProductMovement.to_location == location_id)
            ).delete(synchronize_session=False)
        
        # Now delete the location
        location_name = location.name
        db.session.delete(location)
        db.session.commit()
        
        if movements_count > 0:
            flash(f'Location "{location_name}" and {movements_count} related movements deleted successfully!', 'success')
        else:
            flash(f'Location "{location_name}" deleted successfully!', 'success')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting location: {str(e)}', 'error')
    
    return redirect(url_for('main.locations'))

# Movement routes
@main.route('/movements')
def movements():
    page = request.args.get('page', 1, type=int)
    movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('movements.html', movements=movements)

@main.route('/movements/add', methods=['GET', 'POST'])
def add_movement():
    if request.method == 'POST':
        try:
            product_id = request.form['product_id']
            from_location = request.form['from_location'] if request.form['from_location'] else None
            to_location = request.form['to_location'] if request.form['to_location'] else None
            
            # Validate quantity input
            try:
                qty = int(request.form['qty'])
            except (ValueError, TypeError):
                raise ValueError("Quantity must be a valid number")
            
            notes = request.form.get('notes', '')
            
            # Create movement object
            movement = ProductMovement(
                product_id=product_id,
                from_location=from_location,
                to_location=to_location,
                qty=qty,
                notes=notes
            )
            
            # Validate the movement
            movement.validate_movement()
            
            # Apply stock changes
            movement.apply_stock_changes()
            
            # Save to database
            db.session.add(movement)
            db.session.commit()
            
            # Success message with context
            product = Product.query.get(product_id)
            if movement.movement_type == "Stock Allocation":
                flash(f'Stock allocated successfully! {product.name} total stock remains {product.total_qty} units.', 'success')
            elif movement.movement_type == "Stock Out":
                flash(f'Stock removed successfully! {product.name} now has {product.total_qty} units remaining.', 'success')
            else:
                flash(f'Transfer completed successfully! {product.name} total stock: {product.total_qty} units.', 'success')
            
            return redirect(url_for('main.movements'))
            
        except ValueError as e:
            flash(str(e), 'error')
            products = Product.query.all()
            locations = Location.query.all()
            return render_template('add_movement.html', products=products, locations=locations)
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            products = Product.query.all()
            locations = Location.query.all()
            return render_template('add_movement.html', products=products, locations=locations)
    
    products = Product.query.all()
    locations = Location.query.all()
    return render_template('add_movement.html', products=products, locations=locations)

@main.route('/movements/edit/<int:movement_id>', methods=['GET', 'POST'])
def edit_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    original_qty = movement.qty
    original_product_id = movement.product_id
    original_from_location = movement.from_location
    original_to_location = movement.to_location
    
    if request.method == 'POST':
        try:
            new_product_id = request.form['product_id']
            new_from_location = request.form['from_location'] if request.form['from_location'] else None
            new_to_location = request.form['to_location'] if request.form['to_location'] else None
            
            # Validate quantity input
            try:
                new_qty = int(request.form['qty'])
            except (ValueError, TypeError):
                raise ValueError("Quantity must be a valid number")
                
            new_notes = request.form.get('notes', '')
            
            # First, reverse the original movement's stock changes
            movement.reverse_stock_changes()
            
            # Update movement details
            movement.product_id = new_product_id
            movement.from_location = new_from_location
            movement.to_location = new_to_location
            movement.qty = new_qty
            movement.notes = new_notes
            
            # Validate the updated movement
            movement.validate_movement()
            
            # Apply new stock changes
            movement.apply_stock_changes()
            
            # Save changes
            db.session.commit()
            
            # Success message with context
            product = Product.query.get(new_product_id)
            flash(f'Movement updated successfully! {product.name} now has {product.total_qty} units total.', 'success')
            return redirect(url_for('main.movements'))
            
        except ValueError as e:
            # If validation fails, restore original values
            movement.product_id = original_product_id
            movement.from_location = original_from_location
            movement.to_location = original_to_location
            movement.qty = original_qty
            
            # Restore original stock changes
            movement.apply_stock_changes()
            db.session.rollback()
            
            flash(str(e), 'error')
            products = Product.query.all()
            locations = Location.query.all()
            return render_template('edit_movement.html', movement=movement, products=products, locations=locations)
        except Exception as e:
            # Restore original values on any error
            movement.product_id = original_product_id
            movement.from_location = original_from_location
            movement.to_location = original_to_location
            movement.qty = original_qty
            
            # Restore original stock changes
            movement.apply_stock_changes()
            db.session.rollback()
            
            flash(f'An error occurred: {str(e)}', 'error')
            products = Product.query.all()
            locations = Location.query.all()
            return render_template('edit_movement.html', movement=movement, products=products, locations=locations)
    
    products = Product.query.all()
    locations = Location.query.all()
    return render_template('edit_movement.html', movement=movement, products=products, locations=locations)

@main.route('/movements/delete/<int:movement_id>', methods=['POST'])
def delete_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    
    try:
        # Reverse the stock changes before deleting
        movement.reverse_stock_changes()
        
        # Get product info for the flash message
        product = Product.query.get(movement.product_id)
        product_name = product.name if product else "Unknown Product"
        new_total = product.total_qty if product else 0
        
        # Delete the movement
        db.session.delete(movement)
        db.session.commit()
        
        flash(f'Movement deleted successfully! {product_name} now has {new_total} units total.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting movement: {str(e)}', 'error')
    
    return redirect(url_for('main.movements'))

@main.route('/movements/clear_all', methods=['POST'])
def clear_all_movements():
    try:
        # Get all movements
        movements = ProductMovement.query.all()
        movements_count = len(movements)
        
        if movements_count == 0:
            flash('No movements to clear.', 'info')
            return redirect(url_for('main.movements'))
        
        # Reverse stock changes for all movements
        for movement in movements:
            movement.reverse_stock_changes()
        
        # Delete all movements
        ProductMovement.query.delete()
        db.session.commit()
        
        flash(f'All {movements_count} movements cleared successfully! All product stock quantities have been reset.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing movements: {str(e)}', 'error')
    
    return redirect(url_for('main.movements'))

# Reports route
@main.route('/reports')
def reports():
    # Get all products and locations
    products = Product.query.all()
    locations = Location.query.all()
    
    # Create grid data with Product, Warehouse, Qty columns as requested
    grid_data = []
    for product in products:
        for location in locations:
            balance = product.get_balance_at_location(location.location_id)
            # Include all combinations for complete grid view
            grid_data.append({
                'Product': product.name,
                'Warehouse': location.name,
                'Qty': balance,
                'product_id': product.product_id,
                'location_id': location.location_id
            })
    
    # Calculate summary statistics
    total_quantity = sum(item['Qty'] for item in grid_data)
    positive_items = len([item for item in grid_data if item['Qty'] > 0])
    low_stock_items = len([item for item in grid_data if 0 < item['Qty'] <= 10])
    
    return render_template('reports.html', 
                         grid_data=grid_data,
                         total_quantity=total_quantity,
                         positive_items=positive_items,
                         low_stock_items=low_stock_items)

@main.route('/api/inventory-data')
def api_inventory_data():
    """API endpoint for inventory data (can be used for AJAX updates)"""
    products = Product.query.all()
    locations = Location.query.all()
    
    data = []
    for product in products:
        for location in locations:
            balance = product.get_balance_at_location(location.location_id)
            data.append({
                'product_id': product.product_id,
                'product_name': product.name,
                'location_id': location.location_id,
                'location_name': location.name,
                'balance': balance
            })
    
    return jsonify(data)
