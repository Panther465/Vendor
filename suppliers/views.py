from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

def supplier_list(request):
    """Suppliers listing page"""
    return render(request, 'suppliers.html')

def supplier_search(request):
    """AJAX supplier search"""
    # Handle supplier search logic here
    return JsonResponse({'suppliers': []})

def supplier_detail(request, supplier_id):
    """Individual supplier detail page"""
    # Get supplier details
    context = {'supplier_id': supplier_id}
    return render(request, 'supplier_detail.html', context)
