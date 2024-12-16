# app/forms.py

from django import forms
from .models import Endpoint

class RouteForm(forms.Form):
    start = forms.ModelChoiceField(
        queryset=Endpoint.objects.none(),
        label="Начальная точка",
        widget=forms.Select(attrs={'class': 'form-control'}),
        to_field_name='node_id'  # Используем ID связанного Node
    )
    end = forms.ModelChoiceField(
        queryset=Endpoint.objects.none(),
        label="Конечная точка",
        widget=forms.Select(attrs={'class': 'form-control'}),
        to_field_name='node_id'  # Используем ID связанного Node
    )

    def __init__(self, *args, **kwargs):
        super(RouteForm, self).__init__(*args, **kwargs)
        for field in ['start', 'end']:
            self.fields[field].queryset = Endpoint.objects.select_related('node').all()
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            # Добавляем атрибут data-info для дополнительной информации
            choices = []
            for endpoint in self.fields[field].queryset:
                choices.append((
                    endpoint.node.id,
                    f"{endpoint.name} - {endpoint.additional_info}"
                ))
            self.fields[field].choices = choices


    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')

        if start and end and start.node == end.node:
            raise forms.ValidationError("Начальная и конечная точки не должны совпадать.")

        return cleaned_data

