from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    PropertyType, PropertyStatus, Property, PropertyImage,
    PropertyFeature, PropertyFeatureAssignment, SavedProperty,
    Amenity, PropertyAmenity
)


class PropertyImageInline(admin.TabularInline):
    """
    Inline admin for PropertyImage
    """
    model = PropertyImage
    extra = 1
    fields = ('image', 'caption', 'is_primary', 'order')
    readonly_fields = ('created_at',)


class PropertyFeatureAssignmentInline(admin.TabularInline):
    """
    Inline admin for PropertyFeatureAssignment
    """
    model = PropertyFeatureAssignment
    extra = 1
    fields = ('feature', 'value')
    readonly_fields = ('created_at',)


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    """
    Admin for PropertyType
    """
    list_display = ('name', 'is_active', 'property_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def property_count(self, obj):
        return obj.properties.count()
    property_count.short_description = 'Properties'


@admin.register(PropertyStatus)
class PropertyStatusAdmin(admin.ModelAdmin):
    """
    Admin for PropertyStatus
    """
    list_display = ('name', 'is_active', 'property_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def property_count(self, obj):
        return obj.properties.count()
    property_count.short_description = 'Properties'


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """
    Comprehensive Property admin
    """
    inlines = [PropertyImageInline, PropertyFeatureAssignmentInline]
    
    list_display = (
        'title', 'property_type', 'listing_type', 'status',
        'get_price_display', 'city', 'state', 'owner',
        'is_published', 'is_featured', 'views_count', 'created_at'
    )
    
    list_filter = (
        'property_type', 'status', 'listing_type',
        'is_published', 'is_featured', 'city', 'state',
        'bedrooms', 'bathrooms', 'created_at'
    )
    
    search_fields = (
        'title', 'description', 'address_line_1',
        'city', 'state', 'owner__email', 'owner__first_name', 'owner__last_name'
    )
    
    readonly_fields = (
        'views_count', 'created_at', 'updated_at', 'published_at'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'description', 'property_type', 'status', 'listing_type'
            )
        }),
        ('Ownership', {
            'fields': ('owner', 'agent')
        }),
        ('Location', {
            'fields': (
                ('address_line_1', 'address_line_2'),
                ('city', 'state', 'postal_code'),
                'country',
                ('latitude', 'longitude')
            )
        }),
        ('Property Details', {
            'fields': (
                ('bedrooms', 'bathrooms'),
                ('square_feet', 'lot_size'),
                'year_built'
            )
        }),
        ('Pricing', {
            'fields': (
                ('sale_price', 'rent_price'),
                'currency'
            )
        }),
        ('Features', {
            'fields': (
                ('parking_spaces', 'has_garage'),
                ('has_pool', 'has_garden'),
                'is_furnished'
            )
        }),
        ('Publishing', {
            'fields': (
                ('is_published', 'is_featured'),
                'views_count'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'publish_properties', 'unpublish_properties',
        'feature_properties', 'unfeature_properties',
        'mark_as_sold', 'mark_as_available'
    ]
    
    def publish_properties(self, request, queryset):
        """
        Publish selected properties
        """
        from django.utils import timezone
        updated = 0
        for property in queryset:
            if not property.is_published:
                property.is_published = True
                if not property.published_at:
                    property.published_at = timezone.now()
                property.save()
                updated += 1
        self.message_user(request, f'{updated} properties published.')
    publish_properties.short_description = "Publish selected properties"
    
    def unpublish_properties(self, request, queryset):
        """
        Unpublish selected properties
        """
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} properties unpublished.')
    unpublish_properties.short_description = "Unpublish selected properties"
    
    def feature_properties(self, request, queryset):
        """
        Feature selected properties
        """
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} properties featured.')
    feature_properties.short_description = "Feature selected properties"
    
    def unfeature_properties(self, request, queryset):
        """
        Unfeature selected properties
        """
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} properties unfeatured.')
    unfeature_properties.short_description = "Unfeature selected properties"
    
    def mark_as_sold(self, request, queryset):
        """
        Mark selected properties as sold
        """
        try:
            sold_status = PropertyStatus.objects.get(name='Sold')
            updated = queryset.update(status=sold_status)
            self.message_user(request, f'{updated} properties marked as sold.')
        except PropertyStatus.DoesNotExist:
            self.message_user(request, 'Sold status not found. Please create it first.', level='error')
    mark_as_sold.short_description = "Mark selected properties as sold"
    
    def mark_as_available(self, request, queryset):
        """
        Mark selected properties as available
        """
        try:
            available_status = PropertyStatus.objects.get(name='Available')
            updated = queryset.update(status=available_status)
            self.message_user(request, f'{updated} properties marked as available.')
        except PropertyStatus.DoesNotExist:
            self.message_user(request, 'Available status not found. Please create it first.', level='error')
    mark_as_available.short_description = "Mark selected properties as available"


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """
    Admin for PropertyImage
    """
    list_display = ('property', 'caption', 'is_primary', 'order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('property__title', 'caption')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property')


@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    """
    Admin for PropertyFeature
    """
    list_display = ('name', 'icon', 'is_active', 'property_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def property_count(self, obj):
        return obj.property_assignments.count()
    property_count.short_description = 'Properties'


@admin.register(PropertyFeatureAssignment)
class PropertyFeatureAssignmentAdmin(admin.ModelAdmin):
    """
    Admin for PropertyFeatureAssignment
    """
    list_display = ('property', 'feature', 'value', 'created_at')
    list_filter = ('feature', 'created_at')
    search_fields = ('property__title', 'feature__name', 'value')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property', 'feature')


@admin.register(SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    """
    Admin for SavedProperty
    """
    list_display = ('user', 'property', 'created_at')
    list_filter = ('created_at',)
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'property__title', 'property__city'
    )
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'property')


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    """
    Admin for Amenity
    """
    list_display = ('name', 'category', 'icon', 'is_active', 'property_count', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'category')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Display', {
            'fields': ('icon', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def property_count(self, obj):
        return obj.property_amenities.count()
    property_count.short_description = 'Properties'


@admin.register(PropertyAmenity)
class PropertyAmenityAdmin(admin.ModelAdmin):
    """
    Admin for PropertyAmenity
    """
    list_display = ('property', 'amenity', 'amenity_category', 'created_at')
    list_filter = ('amenity__category', 'created_at')
    search_fields = ('property__title', 'amenity__name', 'amenity__category')
    readonly_fields = ('created_at',)
    
    def amenity_category(self, obj):
        return obj.amenity.category
    amenity_category.short_description = 'Category'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property', 'amenity')
