import yaml
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


class PartnerYAMLImporter:
    def run(self):
        with open('shop1.yaml', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=1)  # упрощённо

        for category in data['categories']:
            cat_obj, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
            cat_obj.shops.add(shop.id)
            cat_obj.save()

        ProductInfo.objects.filter(shop_id=shop.id).delete()

        for item in data['goods']:
            product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

            product_info = ProductInfo.objects.create(
                product_id=product.id,
                external_id=item['id'],
                model=item['model'],
                price=item['price'],
                price_rrc=item['price_rrc'],
                quantity=item['quantity'],
                shop_id=shop.id
            )

            for name, value in item['parameters'].items():
                param_obj, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(
                    product_info_id=product_info.id,
                    parameter_id=param_obj.id,
                    value=value
                )
