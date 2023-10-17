from celery import shared_task
import time
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from django.http import HttpResponse

# from celery import task
from .models import Order
# from .utils import generate_invoice_pdf  # Import the function to generate the PDF
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponseBadRequest
import os
from weasyprint import HTML
from django.conf import settings
# @shared_task
# def handel_task():
#     print("handel task....")
#     time.sleep(10)
from .models import *

# from celery import task


@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.get(pk=order_id)
        pdf_response = generate_invoice_pdf(order_id)

        subject = f'Order Confirmation - Order #{order.id}'
        from_email = 'your-email@example.com'  # Replace with your email
        recipient_list = [order.email]

        context = {
            'customer_name': order.name,
            'order_number': order.id,
            'shipping_address': order.address,
            'total_amount': order.total_amount,
        }

        email_content = render_to_string('shop/order_confirmation_email.html', context)

        email_message = EmailMessage(
            subject,
            email_content,
            from_email,
            recipient_list,
        )

        file_name = f'invoice_{order.id}.pdf'
        email_message.attach(file_name, pdf_response.getvalue(), 'application/pdf')
        email_message.content_subtype = 'html'

        email_message.send()
    except Order.DoesNotExist:
        return "Order not found"

@shared_task
def generate_invoice_pdf(order_id):
    try:
        order = Order.objects.get(pk=order_id)

        html_content = render_to_string('shop/invoice_template.html', {'order': order})
        presentational_hints = True
        pdf_bytes = HTML(string=html_content, base_url=settings.STATIC_URL).write_pdf(presentational_hints=presentational_hints)

        invoice_folder = os.path.join(settings.MEDIA_ROOT, 'invoices')
        os.makedirs(invoice_folder, exist_ok=True)

        file_name = f'invoice_{order_id}.pdf'
        file_path = os.path.join(invoice_folder, file_name)

        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(pdf_bytes)

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={file_name}'

        return response
    except Order.DoesNotExist:
        return HttpResponseBadRequest("Order not found")



# @shared_task

# def generate_invoice_pdf(order_id):
#     try:
#         order = Order.objects.get(pk=order_id)

#         html_content = render_to_string('shop/invoice_template.html', {'order': order})
#         presentational_hints = True
#         pdf_bytes = HTML(string=html_content, base_url=settings.STATIC_URL).write_pdf(presentational_hints=presentational_hints)

#         invoice_folder = os.path.join(settings.MEDIA_ROOT, 'invoices')
#         os.makedirs(invoice_folder, exist_ok=True)

#         file_name = f'invoice_{order_id}.pdf'
#         file_path = os.path.join(invoice_folder, file_name)

#         with open(file_path, 'wb') as pdf_file:
#             pdf_file.write(pdf_bytes)

#         return file_path
#     except Order.DoesNotExist:
#         return HttpResponseBadRequest("Order not found")