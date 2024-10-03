from django import template
register=template.Library()

@register.filter(name='add_form_control')
def add_class_form_control(field):
    return field.as_widget(attrs={'class': 'form-control'})
