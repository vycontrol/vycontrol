import vyos
import perms
import vycontrol_messages as vmsg
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

    p.all_instances = vyos.instance_getall_by_group(request)
    p.hostname_default = vyos.get_hostname_prefered(request)
    p.is_superuser = perms.get_is_superuser(request.user)
    p.request = request
    p.msg = vmsg.msg()
    p.debug = settings.DEBUG

    return p

def context(prepare):
    contextPrepare = {
        'instances':                                prepare.all_instances,
        'hostname_default':                         prepare.hostname_default,
        'is_superuser' :                            prepare.is_superuser,
        'username':                                 prepare.request.user,   
        'msg' :                                     prepare.msg.get_all(),
        'debugactive' :                             prepare.debug,
                       
    }
    return contextPrepare