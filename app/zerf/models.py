from django.db import models

class Group(models.Model):
    task_group_name = models.CharField(max_length=200)
    def __str__(self):
        return self.task_group_name

class Entry(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    description = models.TextField()
    def __str__(self):
        return self.description


