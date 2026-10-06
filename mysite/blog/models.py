from django.conf import settings
from django.db import models
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager

class PublishedManager(models.Manager):
    def get_queryset(self):
        return(
            super().get_queryset().filter(status=Post.Status.PUBLISHED)
        )

class Post(models.Model):
    # STATUS DA PUBLICAÇÃO
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish') # O argumento unique_for_date garante que o slug seja único para a data de publicação do post, evitando conflitos de URL.
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, ## METODO DO DJANGO PARA ADICIONAR O USUARIO CRIADOR DO POST. USANDO O django.contrib.auth no modelo do usuario, assim já adicionando o usuario que criar o post automaticamente como o criador do post
        on_delete=models.CASCADE, # DEFINIR O COMPORTAMENTO DA EXCLUSÃO, 
        related_name='blog_posts' # Especificar o nome para o relacionamento reverso.
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT #ORIGINALMENTE COMO RASCUNHO
    )
    objects = models.Manager()
    published = PublishedManager()
    tags = TaggableManager()

    # ADICIONAR METADATA NO MODEL
    class Meta:
        ordering = ['-publish'] # INDICANDO ORDEM DECRESCENTE DAS PUBLICAÇÕES

        # definir um índice de banco de dados para o campo de publicação
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug
            ]
        ) # Essa função irá criar uma URL dinamicamente para cada post, usando o id do post como argumento. A função reverse() é usada para gerar a URL com base no nome da view 'blog:post_detail' e nos argumentos fornecidos.

## CLASSE PARA COMENTAR

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta():
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]
    def __str__(self):
        return f"Comment for {self.name} on {self.post}"