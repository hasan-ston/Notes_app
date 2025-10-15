from django.db import models # import django's module: models

class Note_set(models.Model): # class is a blueprint. Note_set creates an instance(object) from it.
    # models.Model -> Accessing Model class from models
    # Inheriting from models.Model gives the class database functionality.
    title = models.CharField(max_length=100)
    content = models.FileField(upload_to='notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # Makes it easier to read things in admin shell
        return  self.title
    # self refers to the specific instance that the method is being called on

class Questions(models.Model):
    # Each question is linked to one note_set. on_delete tells django to delete all questions if
    # linked note_set is deleted.
    note_set = models.ForeignKey(Note_set, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=300)
    answer_text = models.CharField(max_length=300)
    creation_date = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default = False)


    def __str__(self):
        return self.question_text