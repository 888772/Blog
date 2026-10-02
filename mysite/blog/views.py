from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .models import Post
from .forms import CommentForm, EmailPostForm
from django.http import Http404

from django.core.mail import send_mail

from django.views.generic import ListView

# ## CRIAR A VIZUALIZAÇÃO DA LISTA DE POSTS
def post_list(request):
    post_list = Post.published.all()

    paginator = Paginator(post_list, 3) # 3 POSTS POR PAGINA
    page_number = request.GET.get('page', 1) # PEGANDO O NUMERO DA PAGINA, SE NAO TIVER, VAI PARA A PAGINA 1

    try:
        posts = paginator.get_page(page_number) # PEGANDO OS POSTS DA PAGINA

    except PageNotAnInteger:
#        ## SE O NUMERO DA PAGINA NÃO FOR UM NUMERO INTEIRO ELE VOLTA PARA A PÁGINA 1
        posts = paginator.page(1)
    except EmptyPage:
#       # SE O NUMERO DE PAGINA FOR FORA DE ALCANCE, ELE VOLTA PARA A ULTIMA PAGINA COM RESULTADO.
        posts = paginator.page(paginator.num_pages)

    return render(
        request,
        'blog/post/list.html',
        {'posts': posts}
    )

## DETALHES DE UM POST ESPECIFICO
def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    #LISTAR COMENTARIOS ATIVOS NO POST
    comments = post.comments.filter(active=True)
    #FORMULARIO PARA O USUARIO COMENTAR
    form = CommentForm()

    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form
        }
    )

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

## COMPARTILHAMENTO ATRAVÉS DE EMAILS

def post_share(request, post_id):

    #PEGAR POST POR ID
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    sent = False

    # POST FOI ENVIADO
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # PASSANDO A VALIDAÇÃO DOS CAMPOS DE FORMULARIOS
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommend you read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}\'s comments {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )
            sent = True
            #.....ENVIA EMAIL
    else:
        form = EmailPostForm()
    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    comment = None

    # UM COMENTARIO PARA POSTAR
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # CRIAR UM OBJETO COMENTARIO SEM ADICIONAR AO BANCO DE DADOS
        comment = form.save(commit=False)
        # ATRIBUIR O POST AO COMENTARIO
        comment.post = post
        # SALVAR O COMENTARIO NO BANCO DE DADOS
        comment.save()
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
    )
# Create your views here.
