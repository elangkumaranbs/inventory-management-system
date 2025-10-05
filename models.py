from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    
    product_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    total_qty = db.Column(db.Integer, nullable=False, default=0)
    
    # Relationship with ProductMovement
    movements = db.relationship('ProductMovement', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.product_id}: {self.name} (Stock: {self.total_qty})>'
    
    def get_balance_at_location(self, location_id):
        """Calculate balance of this product at a specific location"""
        incoming = db.session.query(db.func.sum(ProductMovement.qty)).filter(
            ProductMovement.product_id == self.product_id,
            ProductMovement.to_location == location_id
        ).scalar() or 0
        
        outgoing = db.session.query(db.func.sum(ProductMovement.qty)).filter(
            ProductMovement.product_id == self.product_id,
            ProductMovement.from_location == location_id
        ).scalar() or 0
        
        return incoming - outgoing
    
    def get_total_allocated(self):
        """Get total quantity allocated across all locations"""
        # More efficient: calculate directly from movements
        incoming = db.session.query(db.func.sum(ProductMovement.qty)).filter(
            ProductMovement.product_id == self.product_id,
            ProductMovement.to_location.isnot(None)
        ).scalar() or 0
        
        outgoing = db.session.query(db.func.sum(ProductMovement.qty)).filter(
            ProductMovement.product_id == self.product_id,
            ProductMovement.from_location.isnot(None)
        ).scalar() or 0
        
        return incoming - outgoing
    
    def get_available_stock(self):
        """Get available stock that can be moved out"""
        return self.total_qty
    
    def can_move_quantity(self, quantity, from_location=None):
        """Check if we can move the specified quantity"""
        if from_location:
            # Moving from a specific location - check location balance
            location_balance = self.get_balance_at_location(from_location)
            return location_balance >= quantity
        else:
            # Allocating from unallocated stock - check available unallocated stock
            total_allocated = self.get_total_allocated()
            unallocated = self.total_qty - total_allocated
            return unallocated >= quantity
    
    def update_total_qty(self, quantity_change):
        """Update total quantity (positive for stock in, negative for stock out)"""
        self.total_qty += quantity_change
        if self.total_qty < 0:
            self.total_qty = 0

class Location(db.Model):
    __tablename__ = 'locations'
    
    location_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    
    # Relationships with ProductMovement
    movements_from = db.relationship('ProductMovement', foreign_keys='ProductMovement.from_location', backref='from_loc', lazy=True)
    movements_to = db.relationship('ProductMovement', foreign_keys='ProductMovement.to_location', backref='to_loc', lazy=True)
    
    def __repr__(self):
        return f'<Location {self.location_id}: {self.name}>'

class ProductMovement(db.Model):
    __tablename__ = 'product_movements'
    
    movement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    from_location = db.Column(db.String(50), db.ForeignKey('locations.location_id'), nullable=True)
    to_location = db.Column(db.String(50), db.ForeignKey('locations.location_id'), nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey('products.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Movement {self.movement_id}: {self.product_id} qty:{self.qty}>'
    
    @property
    def movement_type(self):
        """Determine the type of movement"""
        if self.from_location is None:
            return "Stock Allocation"  # Allocating unallocated stock to a location
        elif self.to_location is None:
            return "Stock Out"  # Removing stock from the system
        else:
            return "Transfer"  # Moving between locations
    
    def validate_movement(self):
        """Validate if this movement is possible"""
        # Validate that at least one location is provided
        if not self.from_location and not self.to_location:
            raise ValueError("At least one location (from_location or to_location) must be provided")
        
        # Validate quantity is positive
        if self.qty <= 0:
            raise ValueError("Quantity must be positive")
        
        # Get the product
        product = Product.query.get(self.product_id)
        if not product:
            raise ValueError("Product not found")
        
        # Validate locations exist
        if self.from_location:
            from_loc = Location.query.get(self.from_location)
            if not from_loc:
                raise ValueError(f"From location '{self.from_location}' does not exist")
        
        if self.to_location:
            to_loc = Location.query.get(self.to_location)
            if not to_loc:
                raise ValueError(f"To location '{self.to_location}' does not exist")
        
        # Check stock availability
        if self.from_location:
            # Moving from a location - check location has enough stock
            location_balance = product.get_balance_at_location(self.from_location)
            if location_balance < self.qty:
                from_loc = Location.query.get(self.from_location)
                raise ValueError(f"Not enough stock available at {from_loc.name if from_loc else 'location'}. Available: {location_balance}, Requested: {self.qty}")
        else:
            # Allocating from unallocated stock - check available unallocated stock
            total_allocated = product.get_total_allocated()
            unallocated = product.total_qty - total_allocated
            if unallocated < self.qty:
                raise ValueError(f"Not enough unallocated stock available. Available: {unallocated}, Requested: {self.qty}")
        
        # For stock out operations, check location has enough stock
        if not self.to_location:  # Stock out
            if self.from_location:
                location_balance = product.get_balance_at_location(self.from_location)
                if location_balance < self.qty:
                    from_loc = Location.query.get(self.from_location)
                    raise ValueError(f"Not enough stock at {from_loc.name if from_loc else 'location'} for stock out. Available: {location_balance}, Requested: {self.qty}")
            else:
                raise ValueError("Stock out requires a from_location")
    
    def apply_stock_changes(self):
        """Apply stock changes to product total quantity"""
        product = Product.query.get(self.product_id)
        if not product:
            return
        
        # Only Stock Out (from location to None) decreases total quantity
        # Stock In (from None to location) increases total quantity
        # Transfers between locations don't change total quantity
        if self.from_location and not self.to_location:
            # Stock Out: Decrease total quantity
            product.update_total_qty(-self.qty)
        elif not self.from_location and self.to_location:
            # Stock In: Increase total quantity
            product.update_total_qty(self.qty)
        
        # Transfers between locations don't change total quantity
        # They just track location allocation of existing stock
    
    def reverse_stock_changes(self):
        """Reverse the stock changes made by this movement"""
        product = Product.query.get(self.product_id)
        if not product:
            return
        
        # Reverse Stock Out operations (increase total quantity back)
        if self.from_location and not self.to_location:
            # Reverse Stock Out: Increase total quantity
            product.update_total_qty(self.qty)
        # Reverse Stock In operations (decrease total quantity back)
        elif not self.from_location and self.to_location:
            # Reverse Stock In: Decrease total quantity
            product.update_total_qty(-self.qty)
        
        # Transfers between locations don't affect total quantity, so no reversal needed
    
    def __init__(self, **kwargs):
        super(ProductMovement, self).__init__(**kwargs)
        # Validation will be called explicitly in routes
