from django import forms
from django.core.exceptions import ValidationError
from student.models import question
from student.models import questionPaper
from student.models import studyMaterial
from django.forms import ImageField
from string import Template

class questionForm(forms.ModelForm):
    class Meta:
        model=question
        fields=[
            'questionText',
            'questionImage',
            'option1',
            'option2',
            'option3',
            'option4',
            'rightOption',
            'questionMarks'
        ]
        widgets = {
            'questionText': forms.Textarea(attrs={'style':'width: 53vw'}),
            'option1': forms.TextInput(attrs={'style':'width: 25vw'}),
            'option2': forms.TextInput(attrs={'style':'width: 25vw'}),
            'option3': forms.TextInput(attrs={'style':'width: 25vw'}),
            'option4': forms.TextInput(attrs={'style':'width: 25vw'}),
            'rightOption': forms.TextInput(attrs={'style':'width: 25vw'}),
        }
    def clean(self):
        if self.cleaned_data['rightOption'] not in ['A','B','C','D']:
            raise ValidationError('Option can be A,B,C or D')
        return self.cleaned_data

class questionHead(forms.ModelForm):
    class Meta:
        model=questionPaper
        fields=[
            'paperID',
            'questionTag',
        ]
        widgets = {
            'paperID': forms.TextInput(attrs={'style':'width: 25vw'}),
            'questionTag': forms.TextInput(attrs={'style':'width: 25vw'}),
        }

class studyMaterialForm(forms.ModelForm):
    class Meta:
        model=studyMaterial
        fields=[
            'materialID',
            'materialTag',
            'title',
            'materialFile',
        ]