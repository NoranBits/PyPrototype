
# views.py in a Django app
from django.http import JsonResponse
from .models import Bill, Voting  # Assuming you have these models

def bills_overview(request):
    bills = list(Bill.objects.values('bill_number', 'title', 'parliament_number', 'session_number', 'bill_type', 'status', 'introduced_date', 'royal_assent_date', 'full_text_link'))
    return JsonResponse(bills, safe=False)

def voting_details(request):
    votes = list(Voting.objects.values('bill_id', 'total_yeas', 'total_nays', 'total_abstain', 'vote_date'))
    return JsonResponse(votes, safe=False)