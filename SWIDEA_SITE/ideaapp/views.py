from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Exists, OuterRef
from .models import Idea, DevTool, IdeaStar
from .forms import IdeaForm, DevToolForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


def idea_list(request):
    sort = request.GET.get("sort", "latest")

    ideas = Idea.objects.select_related("devtool").annotate(
        star_count=Count("stars")
    )



    if request.user.is_authenticated:#로그인한 경우 현재 유저가 찜 했는지 표시 
        ideas = ideas.annotate(
            is_starred = Exists(
                IdeaStar.objects.filter(user = request.user, idea = OuterRef("pk"))
            )
        )
    else:
        ideas = ideas.annotate(is_starred=Exists(IdeaStar.objects.none()))

    if sort == "name":
        ideas = ideas.order_by("title")
    elif sort == "oldest":
        ideas = ideas.order_by("created_at")
    elif sort == "star":
        ideas = ideas.order_by("-star_count", "-created_at")
    else:
        ideas = ideas.order_by("-created_at")

    return render(request, "ideaapp/idea_list.html", {"ideas": ideas, "sort": sort})

def idea_detail(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    return render(request, "ideaapp/idea_detail.html", {"idea": idea})


def idea_create(request):
    if request.method == "POST":
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save()
            return redirect("ideaapp:idea_detail", pk=idea.pk)
    else:
        form = IdeaForm()
    return render(request, "ideaapp/idea_form.html", {"form": form})


def idea_edit(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if request.method == "POST":
        form = IdeaForm(request.POST, request.FILES, instance=idea)
        if form.is_valid():
            idea = form.save()
            return redirect("ideaapp:idea_detail", pk=idea.pk)
    else:
        form = IdeaForm(instance=idea)
    return render(request, "ideaapp/idea_form.html", {"form": form})


def idea_delete(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if request.method == "POST":
        idea.delete()
        return redirect("ideaapp:idea_list")
    return render(request, "ideaapp/confirm_delete.html", {"obj": idea})


@login_required
@require_POST
def toggle_star(request, pk):
    idea = get_object_or_404(Idea, pk = pk)
    star, created = IdeaStar.objects.get_or_create(user = request.user, idea = idea)

    if not created:
        star.delete()
        starred = False
    else:
        starred = True

    star_count = IdeaStar.objects.filter(idea=idea).count()
    return JsonResponse({"starred":starred, "star_count":star_count})

@login_required
@require_POST
def update_interest(request, pk, action):
    idea = get_object_or_404
    if action == "inc":
        idea.interest +=1
    elif action == "dec":
        idea.interest = max(0, idea.interest -1)
    else: 
        return JsonResponse({"error": "invalid action"}, status = 400)
    
    idea.save(update_fields =["interests"])
    return JsonResponse({"interes": idea.interest})





def devtool_list(request):
    devtools = DevTool.objects.all()
    return render(request, "ideaapp/devtool_list.html", {"devtools": devtools})


def devtool_detail(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    ideas = devtool.ideas.all()
    return render(request, "ideaapp/devtool_detail.html", {"devtool": devtool, "ideas": ideas})


def devtool_create(request):
    if request.method == "POST":
        form = DevToolForm(request.POST)
        if form.is_valid():
            devtool = form.save()
            return redirect("ideaapp:devtool_detail", pk=devtool.pk)
    else:
        form = DevToolForm()
    return render(request, "ideaapp/devtool_form.html", {"form": form})


def devtool_edit(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    if request.method == "POST":
        form = DevToolForm(request.POST, instance=devtool)
        if form.is_valid():
            devtool = form.save()
            return redirect("ideaapp:devtool_detail", pk=devtool.pk)
    else:
        form = DevToolForm(instance=devtool)
    return render(request, "ideaapp/devtool_form.html", {"form": form})


def devtool_delete(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    if request.method == "POST":
        devtool.delete()
        return redirect("ideaapp:devtool_list")
    return render(request, "ideaapp/confirm_delete.html", {"obj": devtool})
