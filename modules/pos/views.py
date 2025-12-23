import json
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from .services import PoSService


class PoSPageView(PermissionRequiredMixin, View):
    """
    Main PoS interface view
    """
    permission_required = 'pos.add_pos_transaction'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__in=['cashier', 'manager', 'user']).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Render the main PoS interface"""
        return render(request, 'pos.html')


class PoSAPIView(View):
    """
    API view for PoS operations
    """
    def post(self, request):
        """
        Handle POST requests
        """
        try:
            json_request = json.loads(request.body.decode('utf-8'))
            return PoSService.process_post(request, json_request)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)