from django import forms


class DatePickerInput(forms.DateInput):
    """Custom date picker widget"""
    input_type = 'date'
    
    def __init__(self, **kwargs):
        kwargs['attrs'] = {'class': 'form-control', 'type': 'date'}
        super().__init__(**kwargs)


class TimePickerInput(forms.TimeInput):
    """Custom time picker widget"""
    input_type = 'time'
    
    def __init__(self, **kwargs):
        kwargs['attrs'] = {'class': 'form-control', 'type': 'time'}
        super().__init__(**kwargs)


class DateTimePickerInput(forms.DateTimeInput):
    """Custom datetime picker widget"""
    input_type = 'datetime-local'
    
    def __init__(self, **kwargs):
        kwargs['attrs'] = {'class': 'form-control', 'type': 'datetime-local'}
        super().__init__(**kwargs)


class Select2Widget(forms.Select):
    """Select2 enhanced select widget"""
    
    def __init__(self, attrs=None, choices=()):
        default_attrs = {'class': 'form-control select2'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs, choices)


class Select2MultipleWidget(forms.SelectMultiple):
    """Select2 enhanced multiple select widget"""
    
    def __init__(self, attrs=None, choices=()):
        default_attrs = {'class': 'form-control select2'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs, choices)


class FilePreviewWidget(forms.ClearableFileInput):
    """File input with preview"""
    
    template_name = 'widgets/file_preview.html'
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class ImagePreviewWidget(forms.ClearableFileInput):
    """Image input with preview"""
    
    template_name = 'widgets/image_preview.html'
    
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
