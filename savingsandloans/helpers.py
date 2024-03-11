from newmamapesa.models import SavingsItem
from datetime import timedelta

def update_due_dates_of_suspended_savings_items():
    suspended_items=SavingsItem.objects.filter(is_suspended=True)
    
    for item in suspended_items:
        
        item.due_date+=timedelta(days=1)
        item.save()
    