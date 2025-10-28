import os
import uuid
import tempfile
import shutil
from django.core.files.uploadedfile import UploadedFile
import xml.etree.ElementTree as ET
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm, UploadFileForm
from django.http import HttpResponse, Http404
from django.conf import settings
from django.utils.encoding import escape_uri_path

UPLOAD_FOLDER = os.path.join(settings.MEDIA_ROOT, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def home(request):
    return render(request, 'contactsXML/home.html')

def add_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            filename = f"{uuid.uuid4()}.xml"
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            root = ET.Element('contacts')
            contact = ET.SubElement(root, 'contact')
            ET.SubElement(contact, 'first_name').text = data['first_name']
            ET.SubElement(contact, 'last_name').text = data['last_name']
            ET.SubElement(contact, 'email').text = data['email']
            ET.SubElement(contact, 'phone').text = data['phone']

            tree = ET.ElementTree(root)
            tree.write(filepath, encoding='utf-8', xml_declaration=True)

            messages.success(request, f'Контакт сохранён: {filename}')
            return redirect('contactsXML:list_files')
    else:
        form = ContactForm()
    return render(request, 'contactsXML/add_contact.html', {'form': form})


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file: UploadedFile = request.FILES['file']

            # 1. Сохраняем во временный файл
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                for chunk in uploaded_file.chunks():
                    tmp_file.write(chunk)
                temp_path = tmp_file.name

            try:
                # 2. Проверяем структуру XML
                is_valid, error_msg, _ = validate_xml_structure(temp_path)

                if not is_valid:
                    messages.error(request, f"Файл не соответствует формату: {error_msg}")
                    return redirect('contactsXML:list_files')

                # 3. УСПЕХ → перемещаем в uploads
                filename = f"{uuid.uuid4()}.xml"
                final_path = os.path.join(UPLOAD_FOLDER, filename)
                shutil.move(temp_path, final_path)

                messages.success(request, f"Файл {filename} успешно загружен.")

            except Exception as e:
                # Любая ошибка — удаляем временный файл
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                messages.error(request, f"Ошибка обработки файла: {e}")

            finally:
                # Гарантированно удаляем временный файл, если он остался
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass

            return redirect('contactsXML:list_files')

    else:
        form = UploadFileForm()
    return render(request, 'contactsXML/upload_file.html', {'form': form})

def list_files(request):
    xml_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.xml')]

    if not xml_files:
        messages.info(request, "На сервере нет XML-файлов.")
        return render(request, 'contactsXML/list_files.html', {'contents': []})

    contents = []
    for filename in sorted(xml_files):
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        is_valid, error_msg, contacts = validate_xml_structure(filepath)

        if not is_valid:
            contents.append({
                'filename': filename,
                'error': f"Ошибка структуры: {error_msg}",
                'contacts': []
            })
        else:
            contents.append({
                'filename': filename,
                'contacts': contacts,
                'error': None
            })

    return render(request, 'contactsXML/list_files.html', {'contents': contents})

def validate_xml_structure(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        contact_elements = root.findall('.//contact')

        if not contact_elements:
            return False, "Не найден тег <contact>", []

        contacts = []
        for idx, contact in enumerate(contact_elements, 1):
            child_tags = [child.tag for child in contact]

            required_fields = {'first_name', 'last_name', 'email', 'phone'}
            if set(child_tags) != required_fields:
                found = set(child_tags)
                missing = required_fields - found
                extra = found - required_fields
                error_parts = []
                if missing:
                    error_parts.append(f"отсутствуют: {', '.join(missing)}")
                if extra:
                    error_parts.append(f"лишние: {', '.join(extra)}")
                return False, f"Контакт #{idx}: неверная структура — {', '.join(error_parts)}", []

            data = {
                'first_name': contact.findtext('first_name', '').strip(),
                'last_name': contact.findtext('last_name', '').strip(),
                'email': contact.findtext('email', '').strip(),
                'phone': contact.findtext('phone', '').strip(),
            }

            form = ContactForm(data)
            if not form.is_valid():
                errors = []
                for field, msgs in form.errors.items():
                    errors.append(f"{field}: {', '.join(msgs)}")
                return False, f"Контакт #{idx}: {'; '.join(errors)}", []

            contacts.append(form.cleaned_data)

        return True, "OK", contacts

    except ET.ParseError as e:
        return False, f"XML невалиден: {e}", []
    except Exception as e:
        return False, f"Ошибка: {e}", []

def download_file(request, filename):
    filepath = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

    if not os.path.exists(filepath) or not filename.endswith('.xml'):
        raise Http404("Файл не найден или не является XML.")

    with open(filepath, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/xml')

        # Устанавливаем заголовок для скачивания
        safe_filename = escape_uri_path(filename)
        response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'

        return response