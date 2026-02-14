import os
import glob

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
templates_dir = os.path.join(base_dir, 'templates')

skeleton = """{% load static %}
{% extends 'base.html' %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container py-5">
    <h1 class="display-4 text-center mb-4" data-aos="fade-down">{{ title }}</h1>
    <p class="lead text-center" data-aos="fade-up" data-aos-delay="200">This is the {{ title }} page. Customize the structure and content here as needed.</p>
    <!-- Add your form, table, or other components below -->
</div>
{% endblock %}

{% block extra_css %}
<style>
/* Styles specific to {{ title }} */
</style>
{% endblock %}

{% block extra_js %}
<script>
// JS for {{ title }}
</script>
{% endblock %}
"""

for filepath in glob.glob(os.path.join(templates_dir, '**', '*.html'), recursive=True):
    fname = os.path.basename(filepath)
    if fname in ('base.html', 'home.html'):
        continue
    title = os.path.splitext(fname)[0].replace('_', ' ').title()
    content = skeleton.replace('{{ title }}', title)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Updated {filepath}')
