from django.urls import path

from . import views

# URL routes for each view
urlpatterns = [
    path('home/', views.home, name='home'),
    path('<int:id>/details/', views.details, name='details'),
    path('<int:id>/submissions/', views.view_submissions, name='view_submissions'),
    path('<int:id>/upload/', views.upload_files, name='upload'),
    path('<int:id>/create_section/', views.create_section, name='create_section'),
    path('edit_section/', views.edit_section, name='edit_section'),
    path('<pk>/delete_section/', views.DeleteSectionView.as_view(), name='delete_section'),
    path('<int:submission_id>/download/', views.download, name='download'),
    path('<pk>/delete_file/', views.DeleteFileView.as_view(), name='delete_file'),
    path('<pk>/delete_assignment', views.DeleteAssignmentView.as_view(), name='delete_assignment'),
    path('create/', views.create_assignment, name='create_assignment'),
    path('help/', views.help, name='help')
]
