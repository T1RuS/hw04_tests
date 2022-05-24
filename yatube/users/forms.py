from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import EmailField


User = get_user_model()


class CreationForm(UserCreationForm):
    email = EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
