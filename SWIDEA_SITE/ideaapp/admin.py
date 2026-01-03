from django.contrib import admin
from .models import Idea, DevTool, IdeaStar

admin.site.register(Idea)
admin.site.register(DevTool)
admin.site.register(IdeaStar)
#admin 페이지에서 관리자가 개발툴 등록, 아이디어 등록, 찜 등록 같은거도 다 할 수 잇음. 