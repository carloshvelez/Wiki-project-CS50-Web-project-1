import random
import re
from django import forms
from django.shortcuts import render, redirect
from markdown import markdown
from django.core.files.storage import default_storage
from django.core.validators import RegexValidator
from django.urls import reverse

from . import util

class NewPage(forms.Form):
    new_title = forms.CharField()
    new_content = forms.CharField(widget=forms.Textarea, validators=[RegexValidator(r'^#\s+.+\n.+', 'Just Markdown format allowed')])

class EditPage(forms.Form):
    content_form = forms.CharField(widget=forms.Textarea, validators=[RegexValidator(r'^#\s+.+\n.+', 'Just Markdown format allowed')], initial="")





    


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "title": "All Pages"
    })

def entry(request, title):      
    text = util.get_entry(title)
    if text is None:               
        return render(request, "encyclopedia/entry.html", {
            "text": markdown("#Page not found\nThe page you are looking for doesn't exist"),
            "title": "Entry not found"  
        })
    else:
        
        return render(request, "encyclopedia/entry.html", {
            "text": markdown(text),
            "title": text.split("\n")[0].lstrip("# ")        
        })


def search(request):
    query = request.GET.get("q")
    entry_list = util.list_entries()    
    if query.lower() in [entry.lower() for entry in entry_list]:
        return entry(request, query)
    else:
        similar_entries = [entry for entry in entry_list if query.lower() in entry.lower()]
        return render(request, "encyclopedia/index.html", {
            "entries": similar_entries,
            "title": f'"{query}" not found',
            "subtitle": "Similar entries:"
        })


def new(request):
    if request.method == "POST":
        new_page = NewPage(request.POST)
        if new_page.is_valid():
            title = new_page.cleaned_data["new_title"]
            content= new_page.cleaned_data["new_content"]
            
            #CHECK IF THE ENTRY ALREADY EXISTS, BEFORE CALLING save_entry:
            filename = f"entries/{title.capitalize()}.md"
            if default_storage.exists(filename):
                return render(request, "encyclopedia/entry.html", {
                    "title": "Entry already exists",
                    "text": markdown(f"#Entry {title} already exists\nAdd another entry or edit from the respective page")
                })            

            util.save_entry(title.capitalize(), content)
            return entry(request, title)

        else:
            return render(request, "encyclopedia/new.html", {
                "new_page": new_page
            })

    return render(request, "encyclopedia/new.html", {
        "new_page": NewPage()
            })


#YA CREE LA CLASE ARRIBA. SOLO FALTA ESTA VISTA QUE SERÁ ACTIVADA CUANDO EL USUARIO CLICKE EN EDIT. 
def edit(request):
    
    if request.method == "POST":
        new_content = EditPage(request.POST)
        if new_content.is_valid():
            content = new_content.cleaned_data["content_form"]
            content = re.sub('\r\n', '\n', content) ##Evita la creación artificial de varias líneas. 
            title = content.split("\n")[0].strip("# ").strip()
            util.save_entry(title, content)
            return render(request, "encyclopedia/entry.html", {
                "title":title,
                "text": markdown(content)
                } )           
    title= request.GET.get("title")
    text= util.get_entry(title).rstrip()     
    content = EditPage(initial={'content_form': text})
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content_to_edit": content
    })

def random_pick(request):
    entry_list = util.list_entries()
    random_entry = random.choice(entry_list)
    return entry(request, random_entry)


    