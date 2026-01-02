from django.conf import settings
from django.db import models


class DevTool(models.Model):
    name = models.CharField(max_length=50, unique=True)
    kind = models.CharField(max_length=50)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Idea(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="ideas/", blank=True, null=True)
    content = models.TextField()
    interest = models.IntegerField(default=0)
    devtool = models.ForeignKey( #하나의 아이디어는 하나 이상의 개발툴을 가진다.  
        DevTool,
        on_delete=models.PROTECT, #이 개발툴을 사용하는 아이디어가 잇으면, 개발툴을 삭제하지 못함 
        related_name="ideas"  #나중에 개발툴 상세페이지에서 해당 개발툴을 사용하는 아이디어를 불러올 수 잇음 
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class IdeaStar(models.Model): #테이블 이름이 ideastar고 호출할 때는 stars로 한대 
    user = models.ForeignKey(#찜한 사람
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    idea = models.ForeignKey( #찜당한 아이디어 
        Idea,
        on_delete=models.CASCADE,
        related_name="stars" #idea.stars.all 하면 찜한 애들 다 나옴 
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "idea") #한 유저가 한 아이디어를 두번찜못하게 

    def __str__(self):
        return f"{self.user} - {self.idea}"
    

    #IdeaStar.objects.filter(user=u, idea=i).exists() 은 찜 여부 확인가능. 
    #idea.stars.count() 는 아이디어 찜 개수 
    #Idea.objects.filter(stars__user=request.user) 내가 찜한 아이디어 목록
    #Idea.objects.annotate(cnt=Count("stars")).order_by("-cnt")찜하기순 정렬 
