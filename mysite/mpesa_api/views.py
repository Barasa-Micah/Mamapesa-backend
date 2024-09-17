from datetime import date
import random
import string
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
import requests
from requests.auth import HTTPBasicAuth
import json
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.views.decorators.csrf import csrf_exempt
from .models import MpesaPayment, Group, GroupMember


def generate_unique_code(length=6):
    """Generates a random alphanumeric string of fixed length."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

@csrf_exempt
def create_group(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            start_date_str = data.get('start_date')
            
            # Convert start_date from string to date object
            if start_date_str:
                start_date = date.fromisoformat(start_date_str)
            else:
                start_date = None
            
            # Generate unique code
            unique_code = generate_unique_code()
            
            group = Group.objects.create(
                unique_code=unique_code,
                group_name=data['group_name'],
                target_amount=data.get('target_amount'),
                description=data.get('description'),
                is_chama=data.get('is_chama', False),
                validity_months=data.get('validity_months'),
                start_date=start_date,
                installments=data.get('installments')
            )
            
            return JsonResponse({
                'message': 'Group created successfully',
                'group': {
                    'unique_code': group.unique_code,
                    'group_name': group.group_name,
                    'target_amount': group.target_amount,
                    'description': group.description,
                    'is_chama': group.is_chama,
                    'validity_months': group.validity_months,
                    'start_date': group.start_date.isoformat() if group.start_date else None,
                    'due_date': group.due_date.isoformat() if group.due_date else None,
                    'installments': group.installments
                }
            }, status=201)
        except KeyError as e:
            return JsonResponse({'error': f'Missing field: {str(e)}'}, status=400)
        except ValueError as e:
            return JsonResponse({'error': f'Invalid date format: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def update_group(request, unique_code):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body.decode('utf-8'))
            group = get_object_or_404(Group, unique_code=unique_code)
            
            # Update fields except unique_code
            for key, value in data.items():
                if hasattr(group, key) and key != 'unique_code':
                    setattr(group, key, value)
            
            group.save()

            return JsonResponse({
                'message': 'Group updated successfully',
                'group': {
                    'unique_code': group.unique_code,
                    'group_name': group.group_name,
                    'target_amount': group.target_amount,
                    'description': group.description,
                    'is_chama': group.is_chama,
                    'validity_months': group.validity_months,
                    'start_date': group.start_date.isoformat() if group.start_date else None,
                    'due_date': group.due_date.isoformat() if group.due_date else None,
                    'installments': group.installments
                }
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)



@csrf_exempt
def delete_group(request, unique_code):
    if request.method == 'DELETE':
        try:
            group = get_object_or_404(Group, unique_code=unique_code)
            group.delete()
            return JsonResponse({'message': 'Group deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def get_all_groups(request):
    if request.method == 'GET':
        groups = Group.objects.all()
        group_list = [{
            'unique_code': group.unique_code,
            'group_name': group.group_name,
            'target_amount': group.target_amount,
            'total_amount_saved': group.total_amount_saved,
            'description': group.description,
            'is_chama': group.is_chama,
            'validity_months': group.validity_months,
            'start_date': group.start_date,
            'due_date': group.due_date,
            'installments': group.installments
        } for group in groups]
        return JsonResponse({'groups': group_list}, status=200)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def get_group_details(request, unique_code):
    if request.method == 'GET':
        try:
            group = get_object_or_404(Group, unique_code=unique_code)
            return JsonResponse({
                'group_name': group.group_name,
                'target_amount': group.target_amount,
                'total_amount_saved': group.total_amount_saved,
                'description': group.description,
                'is_chama': group.is_chama,
                'validity_months': group.validity_months,
                'start_date': group.start_date,
                'due_date': group.due_date,
                'installments': group.installments,
                'remaining_days': group.remaining_days
            }, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def join_group(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            unique_code = data.get('unique_code')
            name = data.get('name')

            if not unique_code or not name:
                return JsonResponse({'error': 'Unique code and name are required'}, status=400)
            
            group = get_object_or_404(Group, unique_code=unique_code)
            
            member, created = GroupMember.objects.get_or_create(group=group, name=name)

            if created:
                return JsonResponse({'message': 'Successfully joined the group', 'member': name}, status=201)
            else:
                return JsonResponse({'message': 'Already a member'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def get_group_members(request, unique_code):
    if request.method == 'GET':
        try:
            group = get_object_or_404(Group, unique_code=unique_code)
            members = GroupMember.objects.filter(group=group)
            member_list = [{'name': member.name, 'total_contributed': member.total_contributed, 'joined_at': member.joined_at.isoformat()} for member in members]
            return JsonResponse({'members': member_list}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def generate_invite_code(request, group_id):
    if request.method == 'GET':
        if not request.user.is_staff:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        try:
            group = get_object_or_404(Group, id=group_id)
            unique_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            group.unique_code = unique_code
            group.save()
            return JsonResponse({'unique_code': unique_code}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def edit_group(request, unique_code):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body.decode('utf-8'))
            group = get_object_or_404(Group, unique_code=unique_code)
            
            if 'group_name' in data:
                group.group_name = data['group_name']
            if 'target_amount' in data:
                group.target_amount = data['target_amount']
            if 'description' in data:
                group.description = data['description']
            if 'validity_months' in data:
                group.validity_months = data['validity_months']
            if 'installments' in data:
                group.installments = data['installments']
            
            group.save()

            return JsonResponse({'message': 'Group details updated'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def fetch_members(request, unique_code):
    if request.method == 'GET':
        try:
            group = get_object_or_404(Group, unique_code=unique_code)
            members = GroupMember.objects.filter(group=group)
            member_data = [{'name': member.name, 'total_contributed': member.total_contributed} for member in members]
            return JsonResponse({'members': member_data}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def admin_group_transactions(request, unique_code):
    if request.method == 'GET':
        if not request.user.is_staff:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        try:
            group = get_object_or_404(Group, unique_code=unique_code)
            # Placeholder for transactions
            transactions = []  # Replace with actual data retrieval
            return JsonResponse({'transactions': transactions}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Create your views here.
@csrf_exempt
def getAccessToken(request):
    consumer_key = 'cHnkwYIgBbrxlgBoneczmIJFXVm0oHky'
    consumer_secret = '2nHEyWSD4VjpNh2g'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']

    return HttpResponse(validated_mpesa_access_token)

@csrf_exempt
def lipa_na_mpesa_online(stat):
    json_data = json.loads(stat.body.decode('utf-8'))
    phone_number = json_data.get('phone_number', '')
    amount = json_data.get('amount', '')
    print("Phone number:", phone_number)
    print("amount:", amount)
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    request = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": phone_number,  # replace with your phone number to get stk push
        "CallBackURL": "https://mydomain.com/pth",
        "AccountReference": "MamaPesa",
        "TransactionDesc": "Testing",
    }

    response = requests.post(api_url, json=request, headers=headers)
    print(response)
    return HttpResponse('success')
    

@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               "ConfirmationURL": "https://79372821.ngrok.io/api/v1/c2b/confirmation",
               "ValidationURL": "https://79372821.ngrok.io/api/v1/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)

    return HttpResponse(response.text)


@csrf_exempt
def call_back(request):
    # Add your callback logic here if needed
    # For now, just return an empty HTTP response
    return HttpResponse( "https://mydomain.com/pth")


@csrf_exempt
def validation(request):

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))

def home(request):
    return HttpResponse("Welcome to MamaPesa!")


@csrf_exempt
def confirmation(request):
    try:
        mpesa_body = request.body.decode('utf-8')
        mpesa_payment = json.loads(mpesa_body)

        payment = MpesaPayment(
            first_name=mpesa_payment.get('FirstName', ''),
            last_name=mpesa_payment.get('LastName', ''),
            middle_name=mpesa_payment.get('MiddleName', ''),
            description=mpesa_payment.get('TransID', ''),
            phone_number=mpesa_payment.get('MSISDN', ''),
            amount=mpesa_payment.get('TransAmount', ''),
            reference=mpesa_payment.get('BillRefNumber', ''),
            organization_balance=mpesa_payment.get('OrgAccountBalance', ''),
            type=mpesa_payment.get('TransactionType', ''),
        )

        payment.save()

        context = {
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        }

        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
