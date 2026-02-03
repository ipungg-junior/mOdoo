import json
from django.db import transaction as transaction_atomic
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .models import Tax, TaxType
from engine.utils import format_rupiah, supabase_storage
from datetime import datetime


class CoreService:
    
    @staticmethod
    def process_post(request, json_request):
        
        action = json_request.get('action')

        if action == 'tax_list':
            return TaxService._list_taxes()
        else:
            return JsonResponse({'success': False, 'message': f'Unknown POST action: {action}'}, status=400)


class TaxService:
    
    @staticmethod
    def _list_taxes():
        try:
            taxes = Tax.objects.all().select_related('tax_type')
            tax_list = []
            for tax in taxes:
                tax_list.append({
                    'id': tax.id,
                    'name': tax.name,
                    'rate': tax.rate,
                    'type': tax.tax_type.name,
                })
            return JsonResponse({'success': True, 'data': tax_list}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)