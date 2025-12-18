import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import *
from django.contrib.auth.models import User
from engine.utils import format_rupiah


# Class Service for Account Receivable
class AccountReceivable:

    @staticmethod
    def process_post(request, json_request):
        action = json_request.get('action')
        if action == 'list':
            return AccountReceivable.list_receivables(request)
        elif action == 'create':
            return AccountReceivable.create_receivable(request, json_request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown action: {action}'}, status=400)

    @staticmethod
    def create_receivable(request, data):
        amount = data.get('amount')
        due_date = data.get('due_date')
        status_id = data.get('status_id')
        term_id = data.get('term_id')

        if not all([amount, due_date, status_id, term_id]):
            return JsonResponse({'success': False, 'message': 'All fields are required'}, status=400)

        try:
            from .models import AccountingPaymentStatus, AccountingPaymentTerm
            status = AccountingPaymentStatus.objects.get(id=status_id)
            term = AccountingPaymentTerm.objects.get(id=term_id)

            payment = AccountingReceivablePayment(
                amount=amount,
                due_date=due_date,
                status=status,
                term=term,
                created_by=request.user
            )
            payment.full_clean()
            payment.save()

            return JsonResponse({
                'success': True,
                'message': 'Receivable payment created successfully',
                'data': {
                    'id': payment.id,
                    'amount': str(payment.amount),
                    'due_date': payment.due_date.isoformat(),
                    'status': payment.status.display_name,
                    'term': payment.term.display_name
                }
            })

        except AccountingPaymentStatus.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)
        except AccountingPaymentTerm.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid term'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    @staticmethod
    def list_receivables(request):
        from .models import AccountingReceivablePayment
        receivables = AccountingReceivablePayment.objects.filter(status__name='unpaid')
        data = []
        for r in receivables:
            data.append({
                'id': r.id,
                'receivable_name': r.get_display_name(),
                'amount': ((r.amount)),
                'due_date': r.due_date.isoformat() if r.due_date else None,
                'status': r.status.display_name if r.status else 'N/A',
                'status_value': r.status.name if r.status else 'N/A',
                'term': r.term.display_name if r.term else 'N/A'
            })
            
        # Calculate totals
        total_pending = sum(float(r['amount']) for r in data if 'unpaid' in r['status'].lower())
        return JsonResponse({
            'success': True,
            'data': {
                'receivables': data,
                'total_pending': format_rupiah(total_pending),
                'count': len(data)
            }
        })


class MasterDataService:

    @staticmethod
    def process_post(request, json_request):
        action = json_request.get('action')
        if action == 'get_master_payment_status':
            return MasterDataService.get_payment_statuses(request)
        elif action == 'get_master_payment_term':
            return MasterDataService.get_payment_terms(request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown action: {action}'}, status=400)

    @staticmethod
    def get_payment_statuses(request):
        from .models import AccountingPaymentStatus
        statuses = AccountingPaymentStatus.objects.all()
        data = [{'id': s.id, 'name': s.name, 'display_name': s.display_name} for s in statuses]
        return JsonResponse({'success': True, 'data': data})

    @staticmethod
    def get_payment_terms(request):
        from .models import AccountingPaymentTerm
        terms = AccountingPaymentTerm.objects.all()
        data = [{'id': t.id, 'name': t.name, 'display_name': t.display_name} for t in terms]
        return JsonResponse({'success': True, 'data': data})