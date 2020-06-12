from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from student.models import student
class TokenGenerator(PasswordResetTokenGenerator):
    
    def _make_hash_value(self, student, timestamp):
        print(student.isActive)
        
        student.save()
        return (
            six.text_type(student.email) + six.text_type(timestamp) +
            six.text_type(student.isActive)
        )
account_activation_token = TokenGenerator()