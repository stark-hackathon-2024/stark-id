import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path
from django.core.wsgi import get_wsgi_application
from django import forms
from django.http import HttpResponse
from ecdsa import SigningKey, SECP256k1
import hashlib
from merkle import PedersenMerkleTree as MerkleTree
from fast_pedersen_hash import pedersen_hash
from utils import to_bytes


# Define settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
settings.configure(
    DEBUG=True,
    SECRET_KEY='your_secret_key',
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
    MIDDLEWARE=[
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
    ],
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                ],
            },
        },
    ],
)

def generate_merkle_tree_and_signature(**fields):
    # Create a Merkle tree
    tree = MerkleTree([value for key, value in fields.items()])

    # Get the root of the Merkle tree
    root_hash = tree.get_root()

    # Generate a signing key (use your persistent private key in production)
    # sk = SigningKey.generate(curve=SECP256k1)
    # vk = sk.get_verifying_key()
    with open('keys', 'r') as f:
        key_data = json.load(f)
        sk = SigningKey.from_string(bytes.fromhex(key_data['private']), curve=SECP256k1)
        
        vk = key_data['public']
    

    # Sign the root hash
    signature = sk.sign_deterministic(to_bytes(root_hash))

     # Get a visualization of the tree
    tree_representation = tree.visualize_tree()

    return {
        'merkle_tree': tree,
        'root_hash': root_hash,
        'signature': signature,
        'verifying_key': vk,
        'tree_representation': tree_representation
    }


# Define a form class
class InputForm(forms.Form):
    first_name = forms.CharField(label='Fisrt Name:', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Last Name:', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    id_number = forms.CharField(label='ID Number:', max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(label='Date of Birth:', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    nationality = forms.CharField(label='Nationality:', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    starknet_address = forms.CharField(label='Starknet Address:', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    favorite_color = forms.CharField(label='Favorite Color:', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    favorite_animal = forms.CharField(label='Favorite Animal:', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

# Define views
def index(request):
    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            id_number = form.cleaned_data['id_number']
            date_of_birth = form.cleaned_data['date_of_birth']
            nationality = form.cleaned_data['nationality']
            starknet_address = form.cleaned_data['starknet_address']
            favorite_color = form.cleaned_data['favorite_color']
            favorite_animal = form.cleaned_data['favorite_animal']
            # Replace this with arbitrary code

            fields = {
                "starknet_address": int(starknet_address),
                "id_number_hash": pedersen_hash(int(id_number), 0),
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": str(date_of_birth),
                "nationality": nationality,
                "favorite_color": favorite_color,
                "favorite_animal": favorite_animal
            }

            result = generate_merkle_tree_and_signature(**fields)
            output_text = (f"Name: {first_name} {last_name}, ID: {id_number}, DOB: {date_of_birth}, Nationality: {nationality} \n"
                           f"Starknet Address: {starknet_address} \n Favorite Color: {favorite_color}, Favorite Animal: {favorite_animal} \n")
            output_text += (f"Hashed ID: {pedersen_hash(int(id_number), 0)}\n")
            output_text += (f"Root Hash: {result['root_hash']}\n")
            output_text += (f"Signature: {result['signature'].hex()} \n")
            output_text += (f"Verifying Key: {result['verifying_key']} \n")
            output_text += (f"\nMerkle Tree Visualization:\n{result['tree_representation']}")
        
            return render(request, 'index.html', {'form': form, 'output_text': output_text})
    else:
        form = InputForm()
    return render(request, 'index.html', {'form': form})

# Define URL patterns
urlpatterns = [
    path('', index, name='index'),
]

# WSGI application
application = get_wsgi_application()

# Template directory and template file setup
if not os.path.exists(os.path.join(BASE_DIR, 'templates')):
    os.makedirs(os.path.join(BASE_DIR, 'templates'))

template_path = os.path.join(BASE_DIR, 'templates', 'index.html')
with open(template_path, 'w') as f:
    f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Django Web Service</title>
</head>
<body class="container mt-5">
    <h1 class="mb-4">Django Web Service</h1>
    <form method="post" class="needs-validation" novalidate>
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>
    {% if output_text %}
        <div class="alert alert-success mt-4" role="alert">
            <p>Output: {{ output_text|linebreaksbr }}</p>
        </div>
    {% endif %}
</body>
</html>
''')

# Run the development server
if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    import sys

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '__main__')
    execute_from_command_line([sys.argv[0], 'runserver', '127.0.0.1:8000'])
