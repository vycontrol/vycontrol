import vyos
import perms
import vmsg
from django.conf import settings

class prepareClass:
    all_instances = []
    hostname_default = None
    is_superuser = False
    request = None
    msg = None
    debug = False

def prepare(request):
    p = prepareClass()

    p.all_instances = perms.instance_getall_by_group(request)
    p.hostname_default = perms.get_hostname_prefered(request)
    p.is_superuser = perms.get_is_superuser(request.user)
    p.request = request
    p.msg = vmsg.msg()
    p.debug = settings.DEBUG
    p.vycontrol_credits = settings.VYCONTROL_CREDITS

    return p

def context(prepare):
    contextPrepare = {
        'instances':                                prepare.all_instances,
        'hostname_default':                         prepare.hostname_default,
        'is_superuser' :                            prepare.is_superuser,
        'username':                                 prepare.request.user,   
        'msg' :                                     prepare.msg.get_all(),
        'debugactive' :                             prepare.debug,
        'vycontrol_credits' :                       prepare.vycontrol_credits,
                               
    }
    return contextPrepare
