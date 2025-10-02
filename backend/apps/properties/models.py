from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.core.mixins import VisibilityMixin, SoftDeleteMixin, SearchableMixin


class PropertyType(models.Model):
    """
    Property types (House, Apartment, Commercial, etc.)
    Normalized table following 3NF principles
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Property type name (e.g., House, Apartment, Commercial)"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the property type"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this property type is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'property_types'
        verbose_name = 'Property Type'
        verbose_name_plural = 'Property Types'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PropertyStatus(models.Model):
    """
    Property status (Available, Sold, Rented, etc.)
    Normalized table following 3NF principles
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Status name (e.g., Available, Sold, Rented)"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the status"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this status is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'property_statuses'
        verbose_name = 'Property Status'
        verbose_name_plural = 'Property Statuses'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Property(VisibilityMixin, SoftDeleteMixin, SearchableMixin, models.Model):
    """
    Main Property model with enhanced mixins
    Following 3NF principles for database design
    Includes visibility control, soft deletion, and search capabilities
    """
    
    class ListingType(models.TextChoices):
        SALE = 'sale', 'For Sale'
        RENT = 'rent', 'For Rent'
        BOTH = 'both', 'Sale or Rent'
    
    # Basic property information
    title = models.CharField(
        max_length=200,
        help_text="Property title/name"
    )
    description = models.TextField(
        help_text="Detailed property description"
    )
    
    # Property classification
    property_type = models.ForeignKey(
        PropertyType,
        on_delete=models.PROTECT,
        related_name='properties',
        help_text="Type of property"
    )
    status = models.ForeignKey(
        PropertyStatus,
        on_delete=models.PROTECT,
        related_name='properties',
        help_text="Current status of the property"
    )
    listing_type = models.CharField(
        max_length=10,
        choices=ListingType.choices,
        default=ListingType.SALE,
        help_text="Whether property is for sale, rent, or both"
    )
    
    # Owner/Agent information
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_properties',
        help_text="Property owner"
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_properties',
        help_text="Assigned agent (optional)"
    )
    
    # Location information
    address_line_1 = models.CharField(
        max_length=255,
        help_text="Primary address line"
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Secondary address line"
    )
    city = models.CharField(
        max_length=100,
        help_text="City name"
    )
    state = models.CharField(
        max_length=100,
        help_text="State or province"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="Postal or ZIP code"
    )
    country = models.CharField(
        max_length=100,
        default='Kenya',
        help_text="Country name"
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Longitude coordinate"
    )
    
    # Property details
    bedrooms = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Number of bedrooms"
    )
    bathrooms = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.5')), MaxValueValidator(Decimal('50.0'))],
        help_text="Number of bathrooms (can be decimal for half baths)"
    )
    square_feet = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Property size in square feet"
    )
    lot_size = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Lot size in acres"
    )
    year_built = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800), MaxValueValidator(2030)],
        help_text="Year the property was built"
    )
    
    # Pricing information
    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Sale price (if for sale)"
    )
    rent_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monthly rent price (if for rent)"
    )
    currency = models.CharField(
        max_length=3,
        default='KES',
        help_text="Currency code (e.g., KES, USD)"
    )
    
    # Property features
    parking_spaces = models.PositiveIntegerField(
        default=0,
        help_text="Number of parking spaces"
    )
    has_garage = models.BooleanField(
        default=False,
        help_text="Whether property has a garage"
    )
    has_pool = models.BooleanField(
        default=False,
        help_text="Whether property has a pool"
    )
    has_garden = models.BooleanField(
        default=False,
        help_text="Whether property has a garden"
    )
    is_furnished = models.BooleanField(
        default=False,
        help_text="Whether property is furnished"
    )
    
    # Listing information
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this is a featured listing"
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Whether the listing is published"
    )
    views_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this property has been viewed"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the property was first published"
    )
    
    class Meta:
        db_table = 'properties'
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'state']),
            models.Index(fields=['property_type', 'listing_type']),
            models.Index(fields=['sale_price']),
            models.Index(fields=['rent_price']),
            models.Index(fields=['bedrooms', 'bathrooms']),
            models.Index(fields=['is_published', 'is_featured']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.city}, {self.state}"
    
    def get_full_address(self):
        """Return formatted full address"""
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, address_parts))
    
    def get_price_display(self):
        """Return formatted price based on listing type"""
        if self.listing_type == self.ListingType.SALE and self.sale_price:
            return f"{self.currency} {self.sale_price:,.2f}"
        elif self.listing_type == self.ListingType.RENT and self.rent_price:
            return f"{self.currency} {self.rent_price:,.2f}/month"
        elif self.listing_type == self.ListingType.BOTH:
            prices = []
            if self.sale_price:
                prices.append(f"Sale: {self.currency} {self.sale_price:,.2f}")
            if self.rent_price:
                prices.append(f"Rent: {self.currency} {self.rent_price:,.2f}/month")
            return ' | '.join(prices)
        return "Price not set"
    
    # SearchableMixin implementation
    @classmethod
    def get_searchable_fields(cls):
        """
        Define which fields are searchable for properties
        """
        return [
            'title',
            'description', 
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'property_type__name',
            'feature_assignments__feature__name',
            'feature_assignments__value'
        ]
    
    @classmethod
    def get_search_boost(cls):
        """
        Define search boost factors for property fields
        """
        return {
            'title': 2.0,
            'address_line_1': 1.8,
            'city': 1.5,
            'property_type__name': 1.3,
            'description': 1.0,
            'feature_assignments__feature__name': 0.8
        }
    
    @classmethod
    def get_search_filters(cls):
        """
        Define custom search filters for properties
        """
        return {
            'bedrooms_min': lambda q, value: q.filter(bedrooms__gte=value),
            'bedrooms_max': lambda q, value: q.filter(bedrooms__lte=value),
            'bathrooms_min': lambda q, value: q.filter(bathrooms__gte=value),
            'price_min': lambda q, value: q.filter(
                models.Q(sale_price__gte=value) | models.Q(rent_price__gte=value)
            ),
            'price_max': lambda q, value: q.filter(
                models.Q(sale_price__lte=value) | models.Q(rent_price__lte=value)
            ),
            'property_type': lambda q, value: q.filter(property_type__name__icontains=value),
            'has_pool': lambda q, value: q.filter(has_pool=value),
            'has_garage': lambda q, value: q.filter(has_garage=value),
            'is_furnished': lambda q, value: q.filter(is_furnished=value),
            'listing_type': lambda q, value: q.filter(listing_type=value)
        }
    
    @classmethod
    def get_search_result_fields(cls, context=None):
        """
        Define fields to return in search results based on user context
        """
        base_fields = [
            'id', 'title', 'address_line_1', 'city', 'state',
            'bedrooms', 'bathrooms', 'square_feet', 'listing_type'
        ]
        
        if context and hasattr(context, 'role'):
            if context.role in ['seller', 'admin']:  # Landlords
                base_fields.extend(['sale_price', 'rent_price', 'views_count', 'created_at'])
            elif context.role == 'agent':
                base_fields.extend(['sale_price', 'rent_price', 'owner', 'status'])
            elif context.role == 'buyer':  # Tenants
                base_fields.extend(['rent_price' if 'rent' in str(context) else 'sale_price'])
        else:
            # Public/anonymous users
            base_fields.extend(['sale_price', 'rent_price'])
        
        return base_fields


class PropertyImage(models.Model):
    """
    Property images
    Separated from Property model following 3NF principles
    """
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='properties/',
        help_text="Property image"
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Image caption or description"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the primary/featured image"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order of the image"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'property_images'
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['property', 'is_primary']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"Image for {self.property.title}"


class PropertyFeature(models.Model):
    """
    Additional property features
    Normalized table following 3NF principles
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Feature name (e.g., Fireplace, Balcony, Security System)"
    )
    description = models.TextField(
        blank=True,
        help_text="Feature description"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon class or name for UI display"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this feature is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'property_features'
        verbose_name = 'Property Feature'
        verbose_name_plural = 'Property Features'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PropertyFeatureAssignment(models.Model):
    """
    Many-to-many relationship between Properties and Features
    Following 3NF principles with explicit through model
    """
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='feature_assignments'
    )
    feature = models.ForeignKey(
        PropertyFeature,
        on_delete=models.CASCADE,
        related_name='property_assignments'
    )
    value = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional value for the feature (e.g., '2' for 'Fireplaces')"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'property_feature_assignments'
        verbose_name = 'Property Feature Assignment'
        verbose_name_plural = 'Property Feature Assignments'
        unique_together = ['property', 'feature']
        indexes = [
            models.Index(fields=['property']),
            models.Index(fields=['feature']),
        ]
    
    def __str__(self):
        return f"{self.property.title} - {self.feature.name}"


class Amenity(VisibilityMixin, SoftDeleteMixin, SearchableMixin, models.Model):
    """
    Property amenities model for managing available amenities
    Following 3NF principles for database design
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the amenity"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the amenity"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon class or name for UI display"
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Category of amenity (e.g., 'Recreation', 'Security', 'Utilities')"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this amenity is active and available for selection"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Search configuration
    searchable_fields = ['name', 'description', 'category']
    
    class Meta:
        db_table = 'property_amenities'
        verbose_name = 'Amenity'
        verbose_name_plural = 'Amenities'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self) -> str:
        return self.name


class PropertyAmenity(models.Model):
    """
    Many-to-many relationship between Property and Amenity
    Following 3NF principles
    """
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='property_amenities'
    )
    amenity = models.ForeignKey(
        Amenity,
        on_delete=models.CASCADE,
        related_name='property_amenities'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'property_amenity_relations'
        verbose_name = 'Property Amenity'
        verbose_name_plural = 'Property Amenities'
        unique_together = ['property', 'amenity']
        ordering = ['amenity__name']
        indexes = [
            models.Index(fields=['property']),
            models.Index(fields=['amenity']),
        ]
    
    def __str__(self):
        return f"{self.property.title} - {self.amenity.name}"


class SavedProperty(models.Model):
    """
    User saved/favorite properties
    Following 3NF principles
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_properties'
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='saved_by_users'
    )
    notes = models.TextField(
        blank=True,
        help_text="User's private notes about this property"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_properties'
        verbose_name = 'Saved Property'
        verbose_name_plural = 'Saved Properties'
        unique_together = ['user', 'property']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} saved {self.property.title}"
