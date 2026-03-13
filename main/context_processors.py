from .models import Message

def notification_count(request):
    unread_count_creator = 0
    unread_count_applicant = 0
    
    if request.user.is_authenticated:
        # Count unread messages for creator (project author)
        unread_count_creator = Message.objects.filter(
            join_request__project__author=request.user,
            is_read=False
        ).count()
        
        # Count unread messages for applicant
        unread_count_applicant = Message.objects.filter(
            join_request__user=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
    
    return {
        'unread_count_creator': unread_count_creator,
        'unread_count_applicant': unread_count_applicant,
        'total_unread': unread_count_creator + unread_count_applicant
    }
