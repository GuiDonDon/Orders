# orders/importer.py

import os
import requests
import yaml
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


class PartnerYAMLImporter:
    def __init__(self, partner, source):
        self.partner = partner
        self.source = source
        self.data = None

    def load(self):
        if os.path.isfile(self.source):
            self._load_from_file()
        elif self._is_valid_url(self.source):
            self._load_from_url()
        else:
            raise FileNotFoundError(f"Source '{self.source}' is neither a file nor a valid URL.")

    def _is_valid_url(self, url):
        try:
            URLValidator()(url)
            return True
        except ValidationError:
            return False

    def _load_from_file(self):
        with open(self.source, 'r', encoding='utf-8') as file:
            self.data = yaml.safe_load(file)

    def _load_from_url(self):
        try:
            response = requests.get(self.source)
            response.raise_for_status()
            self.data = yaml.safe_load(response.content)
        except Exception as e:
            raise ValueError(f"Failed to load YAML from URL: {str(e)}")

    def import_data(self):
        if not self.data:
            raise ValueError("No data loaded. Call `load()` first.")

        try:
            shop, _ = Shop.objects.get_or_create(name=self.data['shop'], user_id=self.partner)
        except IntegrityError as e:
            raise ValueError(f"Error creating shop: {str(e)}")

        # Категории
        for category in self.data.get('categories', []):
            category_obj, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
            category_obj.shops.add(shop.id)

        # Очистка старых товаров
        ProductInfo.objects.filter(shop_id=shop.id).delete()

        # Товары
        for item in self.data.get('goods', []):
            product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
            product_info = ProductInfo.objects.create(
                product_id=product.id,
                external_id=item['id'],
                model=item['model'],
                price=item['price'],
                price_rrc=item['price_rrc'],
                quantity=item['quantity'],
                shop_id=shop.id,
            )

            for name, value in item.get('parameters', {}).items():
                param_obj, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(
                    product_info_id=product_info.id,
                    parameter_id=param_obj.id,
                    value=value,
                )

        return {'Status': True}

