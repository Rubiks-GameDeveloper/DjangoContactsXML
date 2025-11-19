from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse
from django.db import models  # For Q in search
from django.conf import settings
from django.utils.encoding import escape_uri_path
import os
import uuid
import json
import xml.etree.ElementTree as ET
import tempfile
import shutil
from .forms import ContactForm, UploadFileForm, EditContactForm, ContactValidationForm
from .models import Contact


XML_FILE = os.path.join(settings.MEDIA_ROOT, 'contacts.xml')
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

def home(request):
    return render(request, 'contactsXML/home.html')

def validate_xml_structure(filepath):
    try:
        if not os.path.exists(filepath):
            return False, "Файл не найден или не создан", []

        tree = ET.parse(filepath)
        root = tree.getroot()

        # Ищем все <contact> в любом месте
        contact_elements = root.findall('.//contact')
        if not contact_elements:
            return False, "Не найден ни один тег <contact> в файле", []

        contacts = []
        for idx, contact in enumerate(contact_elements, 1):
            # Получаем все дочерние теги
            child_tags = {child.tag for child in contact}

            # Должно быть ровно {'first_name', 'last_name', 'email', 'phone'}
            required_fields = {'first_name', 'last_name', 'email', 'phone'}
            if child_tags != required_fields:
                missing = required_fields - child_tags
                extra = child_tags - required_fields
                error_parts = []
                if missing:
                    error_parts.append(f"отсутствуют: {', '.join(missing)}")
                if extra:
                    error_parts.append(f"лишние: {', '.join(extra)}")
                return False, f"Контакт #{idx}: неверная структура — {'; '.join(error_parts)}", []

            # Извлекаем и нормализуем данные
            data = {
                'first_name': contact.findtext('first_name', '').strip(),
                'last_name': contact.findtext('last_name', '').strip(),
                'email': contact.findtext('email', '').strip(),
                'phone': contact.findtext('phone', '').strip(),
            }

            # Проверяем на пустые поля после strip
            if not all(data.values()):
                missing = [k for k, v in data.items() if not v]
                return False, f"Контакт #{idx}: пустые поля после очистки: {', '.join(missing)}", []

            # Валидация через новую форму (без 'storage')
            form = ContactValidationForm(data)
            if not form.is_valid():
                errors = []
                for field, msgs in form.errors.items():
                    errors.append(f"{field}: {', '.join(msgs)}")
                return False, f"Контакт #{idx}: ошибки валидации — {'; '.join(errors)}", []

            # Используем cleaned_data (с нормализацией из clean_ методов)
            contacts.append(form.cleaned_data)

        return True, "OK", contacts

    except ET.ParseError as e:
        return False, f"Невалидный XML: {str(e)}", []
    except Exception as e:
        return False, f"Неожиданная ошибка обработки: {str(e)}", []

def ensure_xml_exists():
    if not os.path.exists(XML_FILE):
        root = ET.Element('contacts')
        tree = ET.ElementTree(root)
        tree.write(XML_FILE, encoding='utf-8', xml_declaration=True)

def add_to_xml(contacts_data):
    ensure_xml_exists()
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    for data in contacts_data:
        contact = ET.SubElement(root, 'contact')
        for key, value in data.items():
            ET.SubElement(contact, key).text = value
    tree.write(XML_FILE, encoding='utf-8', xml_declaration=True)

def add_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            storage = data.pop('storage')
            if storage == 'db':
                if Contact.objects.filter(**data).exists():
                    messages.error(request, "Дубликат! Контакт уже существует в БД.")
                else:
                    Contact.objects.create(**data)
                    messages.success(request, "Контакт добавлен в БД.")
            else:
                add_to_xml([data])
                messages.success(request, "Контакт добавлен в XML.")
            return redirect('contactsXML:list_contacts')
    else:
        form = ContactForm()
    return render(request, 'contactsXML/add_contact.html', {'form': form})

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp:
                for chunk in uploaded_file.chunks():
                    tmp.write(chunk)
                temp_path = tmp.name
            try:
                is_valid, error_msg, contacts = validate_xml_structure(temp_path)
                if not is_valid:
                    raise ValueError(error_msg)
                add_to_xml(contacts)
                messages.success(request, "Контакты из файла добавлены в XML.")
            except Exception as e:
                messages.error(request, str(e))
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            return redirect('contactsXML:list_contacts')
    else:
        form = UploadFileForm()
    return render(request, 'contactsXML/upload_file.html', {'form': form})

def list_contacts(request):
    source = request.GET.get('source', 'db')
    contents = []
    error_msg = None

    if source == 'db':
        contacts = Contact.objects.all()
        for c in contacts:
            contents.append({
                'id': c.id,
                'first_name': c.first_name,
                'last_name': c.last_name,
                'email': c.email,
                'phone': c.phone,
            })
    else:
        ensure_xml_exists()
        is_valid, error_msg, contacts = validate_xml_structure(XML_FILE)
        if is_valid:
            contents = contacts
        # Если ошибка, contents остаётся пустым, но error_msg передаётся

    return render(request, 'contactsXML/list_contacts.html', {
        'contents': contents,
        'source': source,
        #'error_msg': error_msg if source == 'file' else None
    })

def edit_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        form = EditContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, "Контакт обновлён.")
            return redirect('contactsXML:list_contacts')
    else:
        form = EditContactForm(instance=contact)
    return render(request, 'contactsXML/edit_contact.html', {'form': form})

def delete_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        contact.delete()
        messages.success(request, "Контакт удалён.")
        return redirect('contactsXML:list_contacts')
    return render(request, 'contactsXML/delete_contact.html', {'contact': contact})

def search_contacts(request):
    query = request.GET.get('query', '')
    contacts = Contact.objects.filter(
        models.Q(first_name__icontains=query) |
        models.Q(last_name__icontains=query) |
        models.Q(email__icontains=query)
    )
    data = list(contacts.values())
    return JsonResponse(data, safe=False)

def download_file(request):
    if os.path.exists(XML_FILE):
        with open(XML_FILE, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/xml')
            response['Content-Disposition'] = 'attachment; filename="contacts.xml"'
            return response
    raise Http404