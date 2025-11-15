"""Helpers for linking airports to normalized Country and City models."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

from django.db import transaction
from django.utils.text import slugify

from apps.base.models import City, Country

COUNTRIES_CSV_PATH = Path("downloads/countries.csv")


@dataclass
class LocationLink:
    """Result of linking an airport to normalized models."""

    country: Country | None
    city: City | None
    created_country: bool = False
    created_city: bool = False


class AirportLocationIntegrator:
    """
    Creates/links normalized Country and City rows for airports.

    The integrator keeps a small in-memory cache so repeated lookups
    during the same import run avoid redundant database queries.
    """

    def __init__(self, *, country_lookup: Dict[str, str] | None = None):
        self.country_lookup = country_lookup or self._load_country_lookup()
        self._country_cache: dict[str, Country] = {}
        self._city_cache: dict[Tuple[str, str], City] = {}

    def _load_country_lookup(self) -> Dict[str, str]:
        """Load optional ISO country names from downloads/countries.csv."""
        lookup: Dict[str, str] = {}
        if not COUNTRIES_CSV_PATH.exists():
            return lookup

        with COUNTRIES_CSV_PATH.open(encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                code = (row.get("code") or row.get("iso_code") or "").strip().upper()
                name = (row.get("name") or row.get("country") or "").strip() or code
                if code:
                    lookup[code] = name
        return lookup

    def _normalize_country_code(self, iso_code: str | None) -> str:
        return (iso_code or "").strip().upper()

    def _normalize_city_name(self, name: str | None) -> str:
        return (name or "").strip()

    @transaction.atomic
    def get_or_create_country(self, iso_code: str | None) -> tuple[Country | None, bool]:
        """Return normalized Country for the ISO code (creating if needed)."""
        normalized = self._normalize_country_code(iso_code)
        if not normalized:
            return None, False
        if normalized in self._country_cache:
            return self._country_cache[normalized], False

        defaults = {
            "name": self.country_lookup.get(normalized, normalized),
            "search_name": self.country_lookup.get(normalized, normalized).lower(),
        }
        country, created = Country.objects.get_or_create(
            iso_code=normalized,
            defaults=defaults,
        )
        self._country_cache[normalized] = country
        return country, created

    @transaction.atomic
    def get_or_create_city(
        self,
        *,
        country: Country | None,
        name: str | None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> tuple[City | None, bool]:
        """Return normalized City for the provided municipality."""
        if not country:
            return None, False
        normalized_name = self._normalize_city_name(name)
        if not normalized_name:
            return None, False

        cache_key = (country.iso_code, normalized_name.lower())
        if cache_key in self._city_cache:
            return self._city_cache[cache_key], False

        slug_value = slugify(f"{country.iso_code}-{normalized_name}")[:255] or slugify(normalized_name)[:255]
        city, created = City.objects.get_or_create(
            country=country,
            search_name=normalized_name.lower(),
            defaults={
                "name": normalized_name,
                "ascii_name": normalized_name,
                "slug": slug_value,
                "latitude": latitude,
                "longitude": longitude,
            },
        )
        if created:
            # slug/search_name defaults handled via model save, but ensure lat/lon update.
            if latitude is not None:
                city.latitude = latitude
            if longitude is not None:
                city.longitude = longitude
            city.save()

        self._city_cache[cache_key] = city
        return city, created

    def link_location(
        self,
        *,
        iso_country: str | None,
        municipality: str | None,
        latitude: float | None = None,
        longitude: float | None = None,
        link_country: bool = True,
        link_city: bool = True,
    ) -> LocationLink:
        """Return LocationLink describing normalized Country/City matches."""
        country: Country | None = None
        created_country = False
        city: City | None = None
        created_city = False

        if link_country:
            country, created_country = self.get_or_create_country(iso_country)

        if link_city:
            city, created_city = self.get_or_create_city(
                country=country,
                name=municipality,
                latitude=latitude,
                longitude=longitude,
            )

        return LocationLink(
            country=country,
            city=city,
            created_country=created_country,
            created_city=created_city,
        )
