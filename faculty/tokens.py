from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from faculty.models import faculty
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, faculty, timestamp):
        return (
            six.text_type(faculty.email) + six.text_type(timestamp) +
            six.text_type(faculty.isActive)
        )
account_activation_token = TokenGenerator()