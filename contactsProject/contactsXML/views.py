import os
import uuid
import xml.etree.ElementTree as ET
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from .forms import ContactForm, UploadFileForm

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

            # Создаём XML: <contacts><contact>...</contact></contacts>
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
            uploaded_file = request.FILES['file']
            filename = f"{uuid.uuid4()}.xml"
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # Сохраняем файл
            with open(filepath, 'wb+') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # === СТРОГАЯ ПРОВЕРКА СТРУКТУРЫ ===
            is_valid, error_msg, _ = validate_xml_structure(filepath)

            if not is_valid:
                os.remove(filepath)
                messages.error(request, f"Файл не соответствует формату: {error_msg}. Файл удалён.")
            else:
                messages.success(request, f"Файл {filename} успешно загружен и проверен.")

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

        # Ищем все <contact> в любом месте
        contact_elements = root.findall('.//contact')
        if not contact_elements:
            return False, "В файле не найден тег <contact>", []

        contacts = []
        for contact in contact_elements:
            # Проверяем наличие всех обязательных полей
            first_name = contact.findtext('first_name')
            last_name = contact.findtext('last_name')
            email = contact.findtext('email')
            phone = contact.findtext('phone')

            if None in (first_name, last_name, email, phone):
                missing = [name for name, val in [
                    ('first_name', first_name),
                    ('last_name', last_name),
                    ('email', email),
                    ('phone', phone)
                ] if val is None]
                return False, f"В теге <contact> отсутствуют поля: {', '.join(missing)}", []

            # Дополнительно: email должен содержать @
            if '@' not in email:
                return False, f"Некорректный email: {email}", []

            contacts.append({
                'first_name': first_name.strip(),
                'last_name': last_name.strip(),
                'email': email.strip(),
                'phone': phone.strip(),
            })

        return True, "OK", contacts

    except ET.ParseError as e:
        return False, f"XML невалиден: {e}", []
    except Exception as e:
        return False, f"Ошибка обработки: {e}", []