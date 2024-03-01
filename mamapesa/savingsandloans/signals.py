from django.dispatch import receiver
from newmamapesa.models import SavingsItem
from django.db.models.signals import post_save
from decimal import Decimal

@receiver(post_save, sender=SavingsItem)
def update_saving_account_total_amount(sender, instance, created, **kwargs):
    # if created:
    all_savings_items=instance.savings.savings_items.all()
    total_price=Decimal("0.00")
    for each in all_savings_items:
        total_price+=each.amount_saved
        
    instance.savings.amount_saved=total_price
    # print(f"done {total_price}")
    instance.savings.save()
        