from django.db import models

class ImageUpload(models.Model):
    person_image = models.ImageField(upload_to='uploads/')
    saree_image = models.ImageField(upload_to='uploads/')
    output_image = models.ImageField(upload_to='output/', null=True, blank=True)