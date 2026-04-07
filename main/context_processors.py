from .models import Message

def activity_pulse(request):
    unread_count_creator = 0
    unread_count_applicant = 0
    
    try:
        if request.user and request.user.is_authenticated:
            unread_count_creator = Message.objects.filter(
                join_request__project__author=request.user,
                is_read=False
            ).count()
            
            unread_count_applicant = Message.objects.filter(
                join_request__user=request.user,
                is_read=False
            ).exclude(sender=request.user).count()
    except Exception as e:

        pass
    
    return {
        'unread_count_creator': unread_count_creator,
        'unread_count_applicant': unread_count_applicant,
        'total_unread': unread_count_creator + unread_count_applicant
    }

#Tis code counts every unread messages from users