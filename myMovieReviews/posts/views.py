from django.shortcuts import render, redirect, get_object_or_404
from .models import Review

def review_list(request):
    reviews = Review.objects.all().order_by('-id')
    return render(request, 'posts/review_list.html', {'reviews': reviews})

def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, 'posts/review_detail.html', {'review': review})

def review_create(request):
    if request.method == 'POST':
        Review.objects.create(
            title=request.POST['title'],
            year=request.POST['year'],
            genre=request.POST['genre'],
            rating=request.POST['rating'],
            director=request.POST['director'],
            actor=request.POST['actor'],
            running_time=request.POST['running_time'],
            content=request.POST['content'],
        )
        return redirect('review_list')
    return render(request, 'posts/review_form.html', {'mode': 'create'})

def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.title = request.POST['title']
        review.year = request.POST['year']
        review.genre = request.POST['genre']
        review.rating = request.POST['rating']
        review.director = request.POST['director']
        review.actor = request.POST['actor']
        review.running_time = request.POST['running_time']
        review.content = request.POST['content']
        review.save()
        return redirect('review_detail', pk=review.pk)
    return render(request, 'posts/review_form.html', {'mode': 'update', 'review': review})

def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    return redirect('review_list')
