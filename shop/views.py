from django.shortcuts import render,redirect
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
from django.contrib import messages
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

# Create your views here.
from django.http import HttpResponse


def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)

def search(request):

    queryset = Product.objects.all()

    if request.GET.get('search'):
        search = request.GET.get('search')
        search_prod = queryset.filter(
            Q(product_name__icontains = search)|
            Q(category__icontains = search)|
            Q(price__icontains= search)|
            Q(desc__icontains=search)|
            Q(subcategory__icontains=search)
        )   
        params = {'allProds':search_prod}
    
    return render(request,'shop/search.html',params)

def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        messages.success(request, "Your queries are succesfully submited")
    return render(request, 'shop/contact.html')

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success","updates":updates,"itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'shop/tracker.html')



def productView(request, myid):

    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'product':product[0]})


def checkout(request):
    if request.method=="POST":
        messages.add_message(request, messages.INFO, "Order confirm pay the bill")
        items_json = request.POST.get('itemsJson', '')
        amount = int(request.POST.get('amount',''))*100 
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        client = razorpay.Client(auth=('rzp_test_XGbCMWGXZOJT5A','9CqEblL6yzrsOWsjdJi4rT0r'))
        response_payment = client.order.create(dict(amount=amount,currency='INR'))
        order_status = response_payment['status']
        order_id = response_payment['id']
        if order_status =='created': # if order is placed
            order = Orders(items_json=items_json,amount=amount,order_id=order_id, name=name, email=email, address=address, city=city,
                        state=state, zip_code=zip_code, phone=phone)
            order.save()
            response_payment['name'] = name
            update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
            update.save()            
            id = order.order_id
            thank = True
            return render(request, 'shop/checkout.html', {'id': id,'payment':response_payment,'thank':thank})
    return render(request, 'shop/checkout.html')

@csrf_exempt
def payment_status(request):
    response = request.POST
    params_dict = {
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_signature': response['razorpay_signature']
    }

    # client instance
    client = razorpay.Client(auth=('rzp_test_XGbCMWGXZOJT5A', '9CqEblL6yzrsOWsjdJi4rT0r'))

    try:
        status = client.utility.verify_payment_signature(params_dict)

        order = Orders.objects.get(order_id=response['razorpay_order_id'])
        order.razorpay_payment_id = response['razorpay_payment_id']
        order.paid = True
        order.save()
        messages.add_message(request, messages.INFO, f'''thank you for shoping with us.  use -"{order.order_id}" to track your order details''')
        return render(request, 'shop/payment_status.html', {'status': True})
    except:
        return render(request, 'shop/payment_status.html', {'status': False})