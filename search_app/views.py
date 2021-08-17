from django.shortcuts import render
from search_app.utils import query, query_sentence

# Create your views here.
def index(request):
    return render(request, 'index.html', {})


def result(request):
    sentence = request.POST.get('input')
    results = query_sentence(sentence)
    return render(request, 'result.html', {'results': results})