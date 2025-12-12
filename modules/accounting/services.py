import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import *
from django.contrib.auth.models import User
from engine.utils import format_rupiah


# Class Sevice for Account Receivable
class AccountReceivable:
    
    def create_receivable(request, data):
        pass