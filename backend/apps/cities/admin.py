from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.contrib.admin import SimpleListFilter

from .models import Country, State, City


class StateInline(admin.TabularInline):
    """Inline admin for states within country admin"""
    model = State
    extra = 0
    fields = ('name', 'code', 'type', 'is_active')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    show_change_link = True


class CityInline(admin.TabularInline):
    """Inline admin for cities within state admin"""
    model = City
    extra = 0
    fields = ('name', 'is_capital', 'is_major', 'population', 'is_active')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    show_change_link = True


class ContinentFilter(SimpleListFilter):
    """Custom filter for continent"""
    title = 'continent'
    parameter_name = 'continent'

    def lookups(self, request, model_admin):
        continents = Country.objects.values_list('continent', flat=True).distinct()
        return [(continent, continent.title()) for continent in continents if continent]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(continent=self.value())
        return queryset


class StateTypeFilter(SimpleListFilter):
    """Custom filter for state type"""
    title = 'state type'
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        types = State.objects.values_list('type', flat=True).distinct()
        return [(type_val, type_val.title()) for type_val in types if type_val]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(type=self.value())
        return queryset


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Admin configuration for Country model"""
    
    list_display = [
        'name', 'code', 'continent', 'currency_code', 'phone_code',
        'state_count', 'city_count', 'is_active', 'created_at'
    ]
    list_filter = [
        'is_active', 'visibility_level', 'is_deleted',
        ContinentFilter, 'currency_code', 'created_at'
    ]
    search_fields = ['name', 'code', 'continent', 'currency_code']
    readonly_fields = [
        'slug', 'state_count', 'city_count', 'created_at', 'updated_at'
    ]
    ordering = ['name']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'slug')
        }),
        ('Geographic Information', {
            'fields': ('continent', 'flag_emoji')
        }),
        ('Currency & Contact', {
            'fields': ('currency_code', 'currency_symbol', 'phone_code')
        }),
        ('Status', {
            'fields': ('is_active', 'visibility_level')
        }),
        ('Statistics', {
            'fields': ('state_count', 'city_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [StateInline]
    
    def get_queryset(self, request):
        """Optimize queryset with annotations"""
        return super().get_queryset(request).annotate(
            state_count=Count('states', distinct=True),
            city_count=Count('states__cities', distinct=True)
        )
    
    def state_count(self, obj):
        """Display state count with link"""
        count = getattr(obj, 'state_count', 0)
        if count > 0:
            url = reverse('admin:cities_state_changelist') + f'?country__id__exact={obj.id}'
            return format_html('<a href="{}">{} states</a>', url, count)
        return '0 states'
    state_count.short_description = 'States'
    state_count.admin_order_field = 'state_count'
    
    def city_count(self, obj):
        """Display city count with link"""
        count = getattr(obj, 'city_count', 0)
        if count > 0:
            url = reverse('admin:cities_city_changelist') + f'?state__country__id__exact={obj.id}'
            return format_html('<a href="{}">{} cities</a>', url, count)
        return '0 cities'
    city_count.short_description = 'Cities'
    city_count.admin_order_field = 'city_count'
    
    actions = ['make_active', 'make_inactive', 'make_public', 'make_private']
    
    def make_active(self, request, queryset):
        """Mark selected countries as active"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} countries marked as active.')
    make_active.short_description = 'Mark selected countries as active'
    
    def make_inactive(self, request, queryset):
        """Mark selected countries as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} countries marked as inactive.')
    make_inactive.short_description = 'Mark selected countries as inactive'
    
    def make_public(self, request, queryset):
        """Mark selected countries as public"""
        queryset.update(visibility_level='public')
        self.message_user(request, f'{queryset.count()} countries marked as public.')
    make_public.short_description = 'Mark selected countries as public'

    def make_private(self, request, queryset):
        """Mark selected countries as private"""
        queryset.update(visibility_level='private')
        self.message_user(request, f'{queryset.count()} countries marked as private.')
    make_private.short_description = 'Mark selected countries as private'


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    """Admin configuration for State model"""
    
    list_display = [
        'name', 'code', 'country', 'type',
        'city_count', 'is_active', 'created_at'
    ]
    list_filter = [
        'is_active', 'visibility_level', 'is_deleted',
        StateTypeFilter, 'country', 'created_at'
    ]
    search_fields = ['name', 'code', 'country__name']
    readonly_fields = [
        'slug', 'city_count', 'created_at', 'updated_at'
    ]
    ordering = ['country__name', 'name']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'slug', 'country')
        }),
        ('Geographic Information', {
            'fields': ('type',)
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'visibility_level')
        }),
        ('Statistics', {
            'fields': ('city_count',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [CityInline]
    
    def get_queryset(self, request):
        """Optimize queryset with annotations"""
        return super().get_queryset(request).annotate(
            city_count=Count('cities', distinct=True)
        ).select_related('country')
    
    def city_count(self, obj):
        """Display city count with link"""
        count = getattr(obj, 'city_count', 0)
        if count > 0:
            url = reverse('admin:cities_city_changelist') + f'?state__id__exact={obj.id}'
            return format_html('<a href="{}">{} cities</a>', url, count)
        return '0 cities'
    city_count.short_description = 'Cities'
    city_count.admin_order_field = 'city_count'
    
    actions = ['make_active', 'make_inactive', 'make_public', 'make_private']
    
    def make_active(self, request, queryset):
        """Mark selected states as active"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} states marked as active.')
    make_active.short_description = 'Mark selected states as active'
    
    def make_inactive(self, request, queryset):
        """Mark selected states as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} states marked as inactive.')
    make_inactive.short_description = 'Mark selected states as inactive'
    
    def make_public(self, request, queryset):
        """Mark selected states as public"""
        queryset.update(visibility_level='public')
        self.message_user(request, f'{queryset.count()} states marked as public.')
    make_public.short_description = 'Mark selected states as public'

    def make_private(self, request, queryset):
        """Mark selected states as private"""
        queryset.update(visibility_level='private')
        self.message_user(request, f'{queryset.count()} states marked as private.')
    make_private.short_description = 'Mark selected states as private'


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Admin configuration for City model"""
    
    list_display = [
        'name', 'state', 'country_name', 'population', 'area_km2',
        'is_capital', 'is_major', 'is_active', 'created_at'
    ]
    list_filter = [
        'is_active', 'visibility_level', 'is_deleted', 'is_capital', 'is_major',
        'state__country', 'state', 'created_at'
    ]
    search_fields = [
        'name', 'description', 'state__name', 'state__country__name'
    ]
    readonly_fields = [
        'slug', 'country_name', 'created_at', 'updated_at'
    ]
    ordering = ['state__country__name', 'state__name', 'name']
    list_per_page = 100
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'state', 'description')
        }),
        ('Geographic Information', {
            'fields': (
                'latitude', 'longitude', 'area_km2', 'population', 'timezone'
            )
        }),
        ('Classification', {
            'fields': ('is_capital', 'is_major')
        }),
        ('Status', {
            'fields': ('is_active', 'visibility_level')
        }),
        ('Metadata', {
            'fields': (
                'country_name', 'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'state', 'state__country'
        )
    
    def country_name(self, obj):
        """Display country name with link"""
        if obj.state and obj.state.country:
            url = reverse('admin:cities_country_change', args=[obj.state.country.id])
            return format_html('<a href="{}">{}</a>', url, obj.state.country.name)
        return '-'
    country_name.short_description = 'Country'
    country_name.admin_order_field = 'state__country__name'
    
    actions = [
        'make_active', 'make_inactive', 'make_public', 'make_private',
        'mark_as_major', 'unmark_as_major', 'mark_as_capital', 'unmark_as_capital'
    ]
    
    def make_active(self, request, queryset):
        """Mark selected cities as active"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} cities marked as active.')
    make_active.short_description = 'Mark selected cities as active'
    
    def make_inactive(self, request, queryset):
        """Mark selected cities as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} cities marked as inactive.')
    make_inactive.short_description = 'Mark selected cities as inactive'
    
    def make_public(self, request, queryset):
        """Mark selected cities as public"""
        queryset.update(visibility_level='public')
        self.message_user(request, f'{queryset.count()} cities marked as public.')
    make_public.short_description = 'Mark selected cities as public'

    def make_private(self, request, queryset):
        """Mark selected cities as private"""
        queryset.update(visibility_level='private')
        self.message_user(request, f'{queryset.count()} cities marked as private.')
    make_private.short_description = 'Mark selected cities as private'
    
    def mark_as_major(self, request, queryset):
        """Mark selected cities as major"""
        updated = queryset.update(is_major=True)
        self.message_user(request, f'{updated} cities marked as major.')
    mark_as_major.short_description = 'Mark selected cities as major'
    
    def unmark_as_major(self, request, queryset):
        """Unmark selected cities as major"""
        updated = queryset.update(is_major=False)
        self.message_user(request, f'{updated} cities unmarked as major.')
    unmark_as_major.short_description = 'Unmark selected cities as major'
    
    def mark_as_capital(self, request, queryset):
        """Mark selected cities as capital"""
        updated = queryset.update(is_capital=True)
        self.message_user(request, f'{updated} cities marked as capital.')
    mark_as_capital.short_description = 'Mark selected cities as capital'
    
    def unmark_as_capital(self, request, queryset):
        """Unmark selected cities as capital"""
        updated = queryset.update(is_capital=False)
        self.message_user(request, f'{updated} cities unmarked as capital.')
    unmark_as_capital.short_description = 'Unmark selected cities as capital'


# Custom admin site configuration
admin.site.site_header = 'Jaston - Cities Administration'
admin.site.site_title = 'Cities Admin'
admin.site.index_title = 'Cities Management'
