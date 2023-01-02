from django.urls import path
from kvm_web import views



urlpatterns = [
    path('',views.index,name='index'),
    path('add',views.ajoutKvm,name='ajoutKvm'),
   path('liste',views.listeKvm,name='listeKvm'),
   path('start/<str:name>',views.start,name='start'),
   path('pause/<str:name>',views.pause,name='pause'),
   path('resume/<str:name>',views.resume,name='resume'),
   path('shutdown/<str:name>',views.shutdown,name='shutdown'),
   path('delete/<str:name>',views.delete,name='delete'),
   path('destroy/<str:name>',views.destroy,name='destroy')

]
