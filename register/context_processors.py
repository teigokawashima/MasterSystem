from .models import Subject


def common(request):
    """this is the date which is gonna be passsed """
    context = {
        'subject_list': Subject.objects.all(),
    }
    return context
