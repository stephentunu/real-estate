from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from apps.core.mixins import VisibilityMixin, SoftDeleteMixin, SearchableMixin


class Country(VisibilityMixin, SoftDeleteMixin, SearchableMixin, models.Model):
    """
    Country model for storing country information
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(2)],
        help_text="Full country name"
    )
    code = models.CharField(
        max_length=3,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{2,3}$',
                message='Country code must be 2-3 uppercase letters'
            )
        ],
        help_text="ISO country code (e.g., US, UK, KE)"
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the country name"
    )
    continent = models.CharField(
        max_length=50,
        choices=[
            ('africa', 'Africa'),
            ('asia', 'Asia'),
            ('europe', 'Europe'),
            ('north_america', 'North America'),
            ('south_america', 'South America'),
            ('oceania', 'Oceania'),
            ('antarctica', 'Antarctica'),
        ],
        help_text="Continent where the country is located"
    )
    currency_code = models.CharField(
        max_length=3,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{3}$',
                message='Currency code must be 3 uppercase letters'
            )
        ],
        help_text="ISO currency code (e.g., USD, EUR, KES)"
    )
    currency_symbol = models.CharField(
        max_length=5,
        blank=True,
        help_text="Currency symbol (e.g., $, €, KSh)"
    )
    phone_code = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\+\d{1,4}$',
                message='Phone code must start with + followed by 1-4 digits'
            )
        ],
        help_text="International phone code (e.g., +1, +254)"
    )
    flag_emoji = models.CharField(
        max_length=10,
        blank=True,
        help_text="Flag emoji for the country"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this country is active for property listings"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_countries'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_countries'
    )
    
    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['continent']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate slug"""
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Ensure unique slug
        original_slug = self.slug
        counter = 1
        while Country.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Return the absolute URL for this country"""
        return reverse('cities:country-detail', kwargs={'slug': self.slug})
    
    @property
    def state_count(self):
        """Return the number of states/provinces in this country"""
        return self.states.filter(is_visible=True, is_deleted=False).count()
    
    @property
    def city_count(self):
        """Return the number of cities in this country"""
        return City.objects.filter(
            state__country=self,
            is_visible=True,
            is_deleted=False
        ).count()
    
    @property
    def property_count(self):
        """Return the number of properties in this country"""
        # This would be implemented when Property model is available
        return 0


class State(VisibilityMixin, SoftDeleteMixin, SearchableMixin, models.Model):
    """
    State/Province model for storing state/province information
    """
    
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="Full state/province name"
    )
    code = models.CharField(
        max_length=10,
        blank=True,
        help_text="State/province code (e.g., CA, NY, NAI)"
    )
    slug = models.SlugField(
        max_length=120,
        blank=True,
        help_text="URL-friendly version of the state name"
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name='states',
        help_text="Country this state belongs to"
    )
    type = models.CharField(
        max_length=20,
        choices=[
            ('state', 'State'),
            ('province', 'Province'),
            ('region', 'Region'),
            ('territory', 'Territory'),
            ('district', 'District'),
            ('county', 'County'),
        ],
        default='state',
        help_text="Type of administrative division"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this state is active for property listings"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_states'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_states'
    )
    
    class Meta:
        verbose_name = 'State/Province'
        verbose_name_plural = 'States/Provinces'
        ordering = ['country__name', 'name']
        unique_together = ['country', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['country', 'name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name}, {self.country.name}"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate slug"""
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.country.code}")
        
        # Ensure unique slug
        original_slug = self.slug
        counter = 1
        while State.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Return the absolute URL for this state"""
        return reverse('cities:state-detail', kwargs={'slug': self.slug})
    
    @property
    def city_count(self):
        """Return the number of cities in this state"""
        return self.cities.filter(is_visible=True, is_deleted=False).count()
    
    @property
    def property_count(self):
        """Return the number of properties in this state"""
        # This would be implemented when Property model is available
        return 0


class City(VisibilityMixin, SoftDeleteMixin, SearchableMixin, models.Model):
    """
    City model for storing city information
    """
    
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="Full city name"
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the city name"
    )
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='cities',
        help_text="State/province this city belongs to"
    )
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Longitude coordinate"
    )
    population = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="City population"
    )
    area_km2 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="City area in square kilometers"
    )
    timezone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Timezone (e.g., America/New_York, Africa/Nairobi)"
    )
    postal_codes = models.JSONField(
        default=list,
        blank=True,
        help_text="List of postal/zip codes for this city"
    )
    is_capital = models.BooleanField(
        default=False,
        help_text="Whether this city is a capital (state/country)"
    )
    is_major = models.BooleanField(
        default=False,
        help_text="Whether this is a major city"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this city is active for property listings"
    )
    
    # SEO and Marketing
    description = models.TextField(
        blank=True,
        help_text="Description of the city for SEO and marketing"
    )
    image = models.ImageField(
        upload_to='cities/images/',
        null=True,
        blank=True,
        help_text="City image for display"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_cities'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_cities'
    )
    
    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        ordering = ['state__country__name', 'state__name', 'name']
        unique_together = ['state', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['state', 'name']),
            models.Index(fields=['is_major']),
            models.Index(fields=['is_capital']),
            models.Index(fields=['is_active']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.name}, {self.state.name}, {self.state.country.name}"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate slug"""
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.state.name}-{self.state.country.code}")
        
        # Ensure unique slug
        original_slug = self.slug
        counter = 1
        while City.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Return the absolute URL for this city"""
        return reverse('cities:city-detail', kwargs={'slug': self.slug})
    
    @property
    def country(self):
        """Return the country this city belongs to"""
        return self.state.country
    
    @property
    def full_name(self):
        """Return the full name including state and country"""
        return f"{self.name}, {self.state.name}, {self.state.country.name}"
    
    @property
    def coordinates(self):
        """Return coordinates as a tuple"""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None
    
    @property
    def property_count(self):
        """Return the number of properties in this city"""
        # This would be implemented when Property model is available
        return 0
    
    def get_nearby_cities(self, radius_km=50):
        """
        Get nearby cities within the specified radius
        This is a simplified version - in production, you'd use PostGIS
        """
        if not self.coordinates:
            return City.objects.none()
        
        # Simple bounding box calculation (not accurate for large distances)
        lat_delta = radius_km / 111.0  # Rough conversion: 1 degree ≈ 111 km
        lng_delta = radius_km / (111.0 * abs(float(self.latitude)) * 0.017453)  # Adjust for latitude
        
        return City.objects.filter(
            latitude__range=(
                float(self.latitude) - lat_delta,
                float(self.latitude) + lat_delta
            ),
            longitude__range=(
                float(self.longitude) - lng_delta,
                float(self.longitude) + lng_delta
            ),
            is_visible=True,
            is_deleted=False,
            is_active=True
        ).exclude(pk=self.pk)
