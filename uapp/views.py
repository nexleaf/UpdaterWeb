# Create your views here.

from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from uapp.models import App, User, Group, Logs, Global#, REGISTRY
import simplejson
import datetime
from pytz import timezone
from haystack.query import SearchQuerySet
from django.shortcuts import render_to_response
from uapp.forms import UserForm, GroupForm, ApplicationForm, ReleaseForm, VersionForm
import ast
from django.contrib import messages


main_page = 'https://updater.nexleaf.org/static/updater/'
login_page = 'http://localhost:8000/login/'


class UserData:
    def __init__(self, user):
        self.imei = user.imei
        self.user_apps = list()

        for app in user.apps.all():
            self.user_apps.append(app.name + "(" + str(app.release) + ")")

        if len(user.group.all()) > 0:
            self.group = user.group.all()[0].name



class AppData:
    def __init__(self, app, checked):
        self.package = app.package
        self.name = app.name
        self.ver = app.ver
        self.release = app.release
        self.checked = checked


class LoggedApp:
    def __init__(self, package, version):
        self.package = package
        self.ver = version



class GroupData:
    def __init__(self, group, count, checked):
        self.name = group.name
        self.checked = checked
        self.users = count


class LogRecord:
    def __init__(self, imei, dt, count, setconf, reported):
        self.imei = imei
        self.time = dt
        self.count = count
        self.setconf = setconf
        self.reported = reported
@login_required
def search_imeis_groups(request):
    if request.method == "POST":
        search_text = request.POST['search_text']
    else:
        search_text=''
    print search_text
    groups = Group.objects.filter(user__imei__contains=search_text)
    groups=set(groups)
    grouplist=list()
    for g in groups:
        user_count = User.objects.filter(group__name=g.name).count()
        app_count = App.objects.filter(group__name=g.name).count()
        grouplist.append({'name': g.name, 'desc': g.desc, 'user_count':user_count,'app_count':app_count})


    return render_to_response('ajax_search.html',{'grouplist':grouplist})

@login_required
def search_imeis(request):
    if request.method == "POST":
        search_text = request.POST['search_text']
    else:
        search_text=''
    print search_text
    users = User.objects.filter(imei__contains=search_text)
    return render_to_response('ajax_search_imei.html',{'users':users})


def login_user(request):
    print request.method
    if request.user.is_authenticated():
        t = loader.get_template('index.html')
        c = RequestContext(request)
        return HttpResponse(t.render(c))

    else:
        return HttpResponseRedirect("/login/")

@login_required
def show_groups(request):
    grouplist = list()
    for g in Group.objects.all():
        user_count = User.objects.filter(group__name=g.name).count()
        app_count = App.objects.filter(group__name=g.name).count()
        grouplist.append({'name': g.name, 'desc': g.desc, 'user_count':user_count,'app_count':app_count})

    return render_to_response('show_groups.html',{"grouplist": grouplist, 'form':GroupForm()})

@login_required
def show_clients(request):
    grouplist = list()
    for g in Group.objects.all():
        user_count = User.objects.filter(group__name=g.name).count()
        app_count = App.objects.filter(group__name=g.name).count()
        grouplist.append({'name': g.name, 'desc': g.desc, 'user_count':user_count,'app_count':app_count})

    return render_to_response('show_clients_in_groups.html',{"grouplist": grouplist,'form':UserForm()})

@login_required
def show_applications(request):
    applist = list()
    releaselist = list()

    for a in App.objects.all():
        if a.name not in [x['name'] for x in applist]:
            group_count = Group.objects.filter(apps__name=a.name).count()

            applist.append({'name':a.name,'group_count':group_count})

    for app in applist:
        apps = App.objects.filter(name=app['name'])
        releaselist=list()
        for a in apps:
            if a.release not in releaselist:
                releaselist.append(a.release)
        app['release_count']=len(releaselist)
    return render_to_response('show_application_names.html',{"applist": applist,'form':ApplicationForm()})

@login_required
def show_logs(request):
    client_count = len(User.objects.all())
    group_count = len(Group.objects.all())
    return render_to_response('logs1.html',{"client_count": client_count,'group_count':group_count})

@login_required
def show_all_clients(request):
    clients = User.objects.all()
    return render_to_response('show_client_logs.html',{"clients": clients, "request":request})

@login_required
def client_logs_details(request, imei):
    log_q = Logs.objects.filter(imei__exact = request.GET["imei"])
    if len(log_q) > 0:
        log_q = log_q.order_by('access')
        count = log_q.count()
    print imei
    package_count = list()
    for log in log_q:
        package_count.append(len(ast.literal_eval(log.packages))+1)
        log.packages = ast.literal_eval(log.packages).iteritems()
    log_q = enumerate(log_q)
    return render_to_response('temp_result.html',{"logs": log_q, "request":request, "package_count":package_count})

@login_required
def final_client_logs(request, imei):
    log_q = Logs.objects.filter(imei__exact = imei)
    if len(log_q) > 0:
        log_q = log_q.order_by('-access')
        count = log_q.count()

    return render_to_response('temp_result2.html',{"logs": log_q, "request":request})

@login_required
def client_logs(request, imei):
    log_q = Logs.objects.filter(imei__exact = request.GET["imei"])

    package_count = list()
    for log in log_q:
        package_count.append(len(ast.literal_eval(log.packages))+1)
        log.packages = ast.literal_eval(log.packages).iteritems()
    log_q = enumerate(log_q)
    return render_to_response('client_logs.html',{"logs": log_q, "request":request, "package_count":package_count})

@login_required
def group_logs_details(request, group):
    group = request.GET['group']
    logs = list()
    thegroup = Group.objects.get(name__exact=group)
    for u in User.objects.filter(group__exact=thegroup).order_by("-imei"):
        log_q = Logs.objects.filter(imei__exact = u.imei)
        log_q = log_q.order_by('-access')
        count = log_q.count()
        reported = ""
        if count > 0:
            access =  log_q.all()[0].access
            reported = ast.literal_eval(log_q[0].packages)
        else:
            access = 'No record'
        setconf = ""
        for grp in u.group.all():
            for ap in grp.apps.all():
                setconf += "" + ap.package + ":" + str(ap.ver) + ", "
        logs.append(LogRecord(u.imei, access , count, setconf, reported))
    return render_to_response('group_logs_details.html',{"logs": logs, "request":request})

@login_required
def final_group_logs(request, groupname):
    group = groupname
    logs = list()
    thegroup = Group.objects.get(name__exact=group)
    for u in User.objects.filter(group__exact=thegroup).order_by("-imei"):
        log_q = Logs.objects.filter(imei__exact = u.imei)
        log_q = log_q.order_by('-access')
        count = log_q.count()
        reported = ""
        if count > 0:
            access =  log_q.all()[0].access
            reported = ast.literal_eval(log_q[0].packages)
        else:
            access = 'No record'
        setconf = ""
        for grp in u.group.all():
            for ap in grp.apps.all():
                setconf += "" + ap.package + ":" + str(ap.ver) + ", "
        logs.append(LogRecord(u.imei, access , count, setconf, reported))
    print "lol"
    return render_to_response('group_logs_details.html',{"logs": logs, "request":request})

@login_required
def show_all_groups(request):
    groups = Group.objects.all()
    return render_to_response('show_group_logs.html',{"groups": groups, "request":request})


def local_time_str(naive_t):
    utc_t = naive_t.replace(tzinfo = timezone('UTC'))
    local_t = utc_t.astimezone(timezone('US/Pacific'))
    return str(local_t)



def addAppToGroup(group, app):
    group.apps.add(app)

def removeAppFromGroup(group, app):
    app.groups.remove(group)
    user_q = User.objects.filter(group__exact = group)

    for user in user_q.all():
        user.apps.remove(app)

def getAppData(app):
    obj = {}
    obj['package'] = app.package
    obj['release'] = app.release
    obj['ver'] = app.ver
    if(app.extra_urls!=""):
        obj['url'] = app.url+","+app.extra_urls
    else:
        obj['url'] = app.url    
    obj['name'] = app.name
    obj['action'] = app.action

    return obj

@login_required
def group_details(request, groupname):

    groupname =request.GET.get('groupname','')
    print groupname
    group = Group.objects.filter(name=groupname)[0]
    apps = App.objects.all()
    group_apps = [app.name for app in group.apps.all()]
    return render_to_response('group_info.html',{"group": group,"apps":apps,"group_apps":group_apps})

@login_required
def app_details(request):
    name =request.GET.get('name','')
    release =request.GET.get('release','')
    version =request.GET.get('version','')

    app = App.objects.filter(name=name,release=release,ver=version)[0]
    group_names = Group.objects.all()
    group = Group.objects.filter(apps__name=name,apps__release=release,apps__ver=version)
    if(len(group)<=0):
        group_name="Unmanaged"
    else:
        group_name = group[0].name
    print group_name
    return render_to_response('app_info.html',{"app":app,"groups":group_names,"group_name":group_name})

@login_required
def client_details(request, imei):

    imei =request.GET.get('imei','')
    print imei
    user = User.objects.filter(imei=imei)[0]
    apps = Group.objects.filter(user__imei = user.imei)[0].apps.all()
    group_name = user.group.all()[0].name
    print group_name
    groups = Group.objects.all()
    return render_to_response('client_info.html',{"user": user,"apps":apps,"group_name":group_name,"groups":groups})


def findGroup(group_name, user):
    print "in find group"
    group_q = Group.objects.filter(name__exact = group_name)
    if len(group_q) > 0:
        print "len group_q >0"
        group = group_q.all()[0]
    else:
        print "len group_q <=0", groupname
        group = Group()
        group.name = group_name
        group.save()

    return group

def get(request, imei):

    unmanaged_str = 'managed=0, '
    managed_str = 'managed=1, '

    user_q = User.objects.filter(imei__exact = imei)

    log = Logs()
    log.imei = imei
    log.access = datetime.datetime.now()

    if request.method == 'GET':
        try:
            log.packages =  request.GET['packages']
        except (KeyError):
            log.packages = "{'error':'could not parse from get request'}"

    log.save()

    applist = []

    # If the user is in the Updater database
    if len(user_q) > 0:
        managed = True
        response = HttpResponse(managed_str)
        myuser = user_q.all()[0]

        for a in myuser.user_apps.all():
            applist.append(getAppData(a))
        for a in myuser.group.all()[0].apps.all():
            applist.append(getAppData(a))

    # If the user is not in the Updater database
    else:
        managed = False
        response = HttpResponse(unmanaged_str)
        unmanaged_group = Group.objects.filter(name__exact="Unmanaged")

        # If the Unmanaged group exists in the database
        if len(unmanaged_group) > 0:

            # Return only the apps in the Unmanaged group
            for a in unmanaged_group[0].apps.all():
                applist.append(getAppData(a))

        # Else, return all the apps in the database
        else:
            for a in App.objects.all():
                applist.append(getAppData(a))

    response.write(simplejson.dumps(applist))

    return response

def get1(request, imei):
    result = {}
    # unmanaged_str = '{"managed"=0, '
    # managed_str = '{"managed"=1, '
    response = HttpResponse()
    result['request_urls'] = Global.objects.all()[0].urls
    user_q = User.objects.filter(imei__exact = imei)

    log = Logs()
    log.imei = imei
    log.access = datetime.datetime.now()

    if request.method == 'GET':
        try:
            log.packages =  request.GET['packages']
        except (KeyError):
            log.packages = "{'error':'could not parse from get request'}"

    log.save()

    applist = []

    # If the user is in the Updater database
    if len(user_q) > 0:
        managed = True
        # response = HttpResponse(managed_str)
        result['managed']=1
        myuser = user_q.all()[0]

        for a in myuser.user_apps.all():
            applist.append(getAppData(a))
        for a in myuser.group.all()[0].apps.all():
            applist.append(getAppData(a))
        result['jitter'] = myuser.jitter
    
    # If the user is not in the Updater database
    else:
        managed = False
        # response = HttpResponse(unmanaged_str)
        result['managed']=0
        unmanaged_group = Group.objects.filter(name__exact="Unmanaged")

        # If the Unmanaged group exists in the database
        if len(unmanaged_group) > 0:

            # Return only the apps in the Unmanaged group
            for a in unmanaged_group[0].apps.all():
                applist.append(getAppData(a))

        # Else, return all the apps in the database
        else:
            for a in App.objects.all():
                applist.append(getAppData(a))

    result['apps']=applist


    response.write(simplejson.dumps(result))

    return response



def register(request):
    cache.delete('clientjson')
    response = HttpResponse("{'result': 'success'}")

    #mydebug = open('/tmp/updaterdebug.txt', 'a')
    DEFAULT_PHONE = "NaN"


    if request.method == 'POST':
        info_str = request.POST['info']
        #mydebug.write(info_str + '\n')


        info = simplejson.loads(info_str)

        if 'id' in info.keys():
            id_imei = info['id']
            #mydebug.write(id_imei + '\n')
        else:
            #mydebug.close()
            return HttpResponseBadRequest("{'result': 'Missing id'}")

        if 'sim_id' in info.keys():
            sim_id = info['sim_id']
            #mydebug.write(sim_id + '\n')
        else:
            #mydebug.close()
            sim_id = ''
            #return HttpResponseBadRequest("{'result': 'Missing sim_id'}")

        if 'asset_tag' in info.keys():
            asset_tag = info['asset_tag']
            #mydebug.write(asset_tag + '\n')
        else:
            #mydebug.close()
            asset_tag = ''
            #return HttpResponseBadRequest("{'result': 'Missing asset_tag'}")


        if 'phone_number' in info.keys():
            phone_number = info['phone_number']
            #mydebug.write(phone_number + '\n')
        else:
            phone_number = ''
            #mydebug.close()
            #return HttpResponseBadRequest("{'result': 'Missing phone_number'}")


        if 'group_name' in info.keys():
            group_name = info['group_name']
            #mydebug.write(group_name + '\n')
        else:
            #mydebug.close()
            group_name = "Unmanaged"
            #return HttpResponseBadRequest("{'result': 'Missing group_name'}")

        user_q = User.objects.filter(imei__exact = id_imei)
        if len(user_q) > 0:
            myuser = user_q.all()[0]
        else:
            myuser = User()
            myuser.locked_inventory = False


        myuser.imei = id_imei

        if not myuser.locked_inventory:
            myuser.simid = sim_id
            myuser.phone = phone_number
            myuser.assettag = asset_tag

        myuser.save()

        if len(myuser.group.all()) == 0:
            myuser.group.add(findGroup(group_name, myuser))

        myuser.save()

    return response



def get_global_urls(request):
    globalObject = Global.objects.all()
    urls_list = []
    if(globalObject):
        urls_list = globalObject[0].urls.split(",")
    return HttpResponse("ok")

def set_global_urls(request):

    urls_list = request.POST.get("urls")
    globalObject = Global.objects.all()
    if globalObject:
        g = globalObject[0]
        g.urls = urls_list
        g.save()
    else:
        g = Global()
        g.urls = urls_list
        g.save()
    return HttpResponseRedirect("/global/")
    # return render_to_response('global_urls_form.html',{"urls_list": urls_list})

def show_global_attributes(request):
    global_object = Global.objects.all()
    global_urls = ""
    if(global_object):
        global_urls = global_object[0].urls
    return render_to_response("show_global_attributes.html",{"global_urls":global_urls})

@login_required
def index(request):

    appslist = list()
    for a in App.objects.all():
        appslist.append(a)


    userslist = list()
    for u in User.objects.all():
        userslist.append(UserData(u))

    t = loader.get_template('main.html')

    c = RequestContext(request, {'apps': appslist,
                 'users': userslist
        })



    return HttpResponse(t.render(c))

@login_required
def listClients(request):
    # Check for advanced search parameters
    if 'basic' in request.POST:
        pbasic = request.POST['basic']
        pbasic = simplejson.loads(pbasic)

    if 'group' in request.POST:
        pgroup = request.POST['group']

    if 'user_apps' in request.POST:
        puser_apps = request.POST['user_apps']
        puser_apps = simplejson.loads(puser_apps)

    if 'group_apps' in request.POST:
        pgroup_apps = request.POST['group_apps']
        pgroup_apps = simplejson.loads(pgroup_apps)

    if 'phone_tags' in request.POST:
        pphone_tags = request.POST['phone_tags']
        pphone_tags = simplejson.loads(pphone_tags)

    if 'manual_tags' in request.POST:
        pmanual_tags = request.POST['manual_tags']
        pmanual_tags = simplejson.loads(pmanual_tags)

    sqs = None
    sqstring = 'SearchQuerySet()'

    a = ('group' in request.POST)
    b = ('user_apps' in request.POST)
    c = ('group_apps' in request.POST)
    d = ('phone_tags' in request.POST)
    e = ('manual_tags' in request.POST)

    # Construct a specialized search query, given the search parameters
    if 'pbasic' in locals():
        for qry in pbasic:
            sqstring += '.filter(content="' + str(qry) + '")'
        sqs = eval(sqstring)

    '''if a and b and c:
        sqstring += '.filter(group="' + str(pgroup) + '")'
        for a in puser_apps:
            sqstring += '.filter(user_apps__startswith="' + str(a) + '")'
        for a in pgroup_apps:
            sqstring += '.filter(group_apps__startswith="' + str(a) + '")'
        sqs = eval(sqstring)

    elif not a and b and c:
        for a in puser_apps:
            sqstring += '.filter(user_apps__startswith="' + str(a) + '")'
        for a in pgroup_apps:
            sqstring += '.filter(group_apps__startswith="' + str(a) + '")'
        sqs = eval(sqstring)

    elif a and not b and c:
        sqstring += '.filter(group="' + str(pgroup) + '")'
        for a in pgroup_apps:
            sqstring += '.filter(group_apps__startswith="' + str(a) + '")'
        sqs = eval(sqstring)

    elif a and b and not c:
        sqstring += '.filter(group="' + str(pgroup) + '")'

        for a in puser_apps:
            sqstring += '.filter(user_apps__startswith="' + str(a) + '")'

        sqs = eval(sqstring)

    elif not a and not b and c:
        for a in pgroup_apps:
            sqstring += '.filter(group_apps__startswith="' + str(a) + '")'
        sqs = eval(sqstring)

    elif a and not b and not c:
        sqstring += '.filter(group="' + str(pgroup) + '")'
        sqs = eval(sqstring)

    elif not a and b and not c:
        for a in puser_apps:
            sqstring += '.filter(user_apps__startswith="' + str(a) + '")'
        sqs = eval(sqstring)'''

    if a:
        sqstring += '.filter(group="' + str(pgroup) + '")'
    if b:
        for a in puser_apps:
            sqstring += '.filter(user_apps__startswith="' + str(a) + '")'
    if c:
        for a in pgroup_apps:
            sqstring += '.filter(group_apps__startswith="' + str(a) + '")'
    if d:
        for a in pphone_tags:
            sqstring += '.filter(phone_tags__startswith="' + str(a) + '")'
    if e:
        for a in pmanual_tags:
            sqstring += '.filter(manual_tags__startswith="' + str(a) + '")'

    sqs = eval(sqstring)


    # Get the actual user objects from the SearchQuerySet
    users = []
    #if sqs is not None:
    if sqstring != 'SearchQuerySet()' and sqs != None:
        for s in sqs:
            users.append(s.object)
    else:
        # If no search filters applied, just return all the users in the database
        users = User.objects.all()

    # Try loading the results from the cache
    # TODO: Uncomment this for performance (to start caching)
    # clientjson = cache.get('clientjson')
    clientjson = None

    # If the data is not already in the cache, we must generate it
    if clientjson == None:
        userslist = list()
        for u in users:
            uapps = ""
            for i in u.user_apps.all():
                uapps = uapps + i.name + "(" + i.release + ":" + str(i.ver) + ")" + ", "
            uapps = uapps[:-2]

            gapps = ""
            for i in u.group.all()[0].apps.all():
                gapps = gapps + i.name + "(" + i.release + ":" + str(i.ver) + ")" + ", "
            gapps = gapps[:-2]

            udict = {   'imei' : u.imei,
                        'user_applications' : uapps,
                        'group_applications' : gapps,
                        'group' : u.group.all()[0].name,
                        'phone_tags' : u.phone_tags,
                        'manual_tags' : u.manual_tags,
                        'asset_tag' : u.assettag,
                        'phone' : u.phone,
                        'sim_id' : u.simid,
                        'locked_inventory' : str(u.locked_inventory)
                    }

            userslist.append(udict)

        clientjson = simplejson.dumps(userslist)
        cache.set('clientjson', clientjson, 60*60*24)

    # Return the data to the user
    return HttpResponse(clientjson, content_type='application/javascript')

@login_required
def listApps(request):
    appslist = list()
    appnames = list()

    for a in App.objects.all():
        #if a.name not in appnames:
        groupslist = list()

        for g in Group.objects.filter(apps__name__exact=a.name):
            groupslist.append(g.name)

        appnames.append(a.name)
        appslist.append({'package': a.package,
                         'version': a.ver,
                         'url': a.url,
                         'action': a.action,
                         'groups': groupslist,
                         'release': a.release,
                         'name': a.name})
    json = simplejson.dumps(appslist)
    return HttpResponse(json, content_type='application/javascript')

@login_required
def listAppNames(request):
    appslist = list()
    appnames = list()

    for a in App.objects.all():
        if a.name not in appnames:
            groupslist = list()
            for g in Group.objects.filter(apps__name__exact=a.name):
                groupslist.append(g.name)
            appnames.append(a.name)
            appslist.append({'package': a.package,
                             'version': a.ver,
                             'url': a.url,
                             'action': a.action,
                             'groups': groupslist,
                             'release': a.release,
                             'name': a.name})
    json = simplejson.dumps(appslist)
    return HttpResponse(json)

@login_required
def listGroups(request):
    grouplist = list()
    for g in Group.objects.all():
        grouplist.append({'name': g.name, 'desc': g.desc})

    json = simplejson.dumps(grouplist)
    return HttpResponse(json, content_type='application/javascript')

@login_required
def getClientTags(request, imei):
    users = User.objects.filter(imei__exact = imei)
    if len(users) > 0:
        myuser = User.objects.filter(imei__exact = imei)[0]
        return HttpResponse(myuser.manual_tags, content_type='application/javascript')
    else:
        return HttpResponse('[]')

@login_required
def getClientApps(request, imei):
    userapps = list()
    userinfo = list()

    user_q = User.objects.filter(imei__exact = imei)
    if len(user_q) > 0:
        myuser = user_q.all()[0]
        for a in myuser.user_apps.all():
            groupslist = list()
            for g in Group.objects.filter(apps__name__exact=a.name):
                groupslist.append(g.name)

            userapps.append({'package': a.package,
                             'version': a.ver,
                             'url': a.url,
                             'action': a.action,
                             'groups': groupslist,
                             'release': a.release,
                             'name': a.name})

        json = simplejson.dumps(userapps)
    return HttpResponse(json, content_type='application/javascript')

@login_required
def getClientLogs(request, imei):
    log_q = Logs.objects.filter(imei__exact = imei)
    if len(log_q) > 0:
        log_q = log_q.order_by('access')
        count = log_q.count()

        access1 = local_time_str(log_q.all()[count - 1].access)
        packages_str = str(log_q.all()[count-1].packages)
        packages = simplejson.loads(packages_str)

        json = list()

        for package in packages.keys():
            json.append({
                'time': access1,
                'package': package,
                'version': packages[package]
            })

        json = simplejson.dumps(json)
        return HttpResponse(json, content_type='application/javascript')
    else:
        return HttpResponse('[]')

@login_required
def deleteClients(request):
    clients = request.POST['clients']
    loadedclients = simplejson.loads(clients)

    if len(loadedclients) > 0:
        cache.delete('clientjson')
        for c in loadedclients:
            u = User.objects.filter(imei__exact = c)
            u.delete()

    return HttpResponse('')

@login_required
def getGroupApps(request, groupname):
    defaultappslist = list()

    #apps = App.objects.all()
    apps = Group.objects.filter(name__exact = groupname)
    if len(apps) > 0:
        for app in apps[0].apps.all():
            groupslist = list()
            for g in Group.objects.filter(apps__name__exact=app.name):
                groupslist.append(g.name)
            defaultappslist.append({'package': app.package,
                             'version': app.ver,
                             'url': app.url,
                             'action': app.action,
                             'groups': groupslist,
                             'release': app.release,
                             'name': app.name})


        return HttpResponse(simplejson.dumps(defaultappslist), content_type='application/javascript')

    else:
        return HttpResponse('[]')
@login_required
def getGroupClients(request, groupname):
    user_list = User.objects.filter(group__name=groupname)
    return render_to_response('show_clients.html',{"user_list": user_list,"groupname":groupname})


@login_required
def getAppGroups(request, appname, release, version):

    groupslist = list()

    for group in Group.objects.filter(apps__name__exact = appname, apps__release__exact = release, apps__ver__exact = version):
        groupslist.append({'name': group.name, 'desc': group.desc})

    return HttpResponse(simplejson.dumps(groupslist), content_type='application/javascript')




@login_required
def add_group(request):
    cache.delete('clientjson')
    print request.POST.get("group")
    # Add the group to the database if it does not already exist
    group_q = Group.objects.filter(name__exact = request.POST.get("group"))
    if len(group_q) > 0:
        group = group_q.all()[0]
        group.desc = request.POST.get("desc")
        group.jitter = request.POST.get("jitter")
        
        group.save()
    else:
        group = Group()
        group.name = request.POST.get("group")
        group.desc = request.POST.get("desc")
        group.jitter = request.POST.get("jitter")
        group.save()

    # Add the specified applications to the group
    for a in App.objects.all():
        app_str = str(a.package) + "(" + str(a.release) + "," + str(a.ver) + ")"
        try:
            app_status = request.POST[app_str]
            if app_status == 'on':

                # Add the selected apps to the group
                group.apps.add(a)

                # Get all the users in the group with the application selected
                for u in User.objects.filter(group__exact = group, user_apps__name__exact = a.name):
                    # Remove the selected group app from those users
                    for app in App.objects.filter(name__exact = a.name):
                        u.user_apps.remove(app)

        except (KeyError):
            group.apps.remove(a)
            # Remove the not-selected applications from the group
            #if group in a.groups.all():
            #   removeAppFromGroup(group, a)


    # return HttpResponse('')
    return HttpResponseRedirect("/groups/")

@login_required
def edit_group(request):
    cache.delete('clientjson')
    print request.POST.get("group")
    # Add the group to the database if it does not already exist
    group_q = Group.objects.filter(name__exact = request.POST.get("group_name_hidden"))
    if len(group_q) > 0:
        group = group_q.all()[0]
        group.name = request.POST.get("group")
        group.desc = request.POST.get("desc")
        group.jitter = request.POST.get("jitter")
        
        group.save()

    # Add the specified applications to the group
    for a in App.objects.all():
        app_str = str(a.package) + "(" + str(a.release) + "," + str(a.ver) + ")"
        try:
            print app_str," - ",request.POST[app_str]
            print "\n"
            app_status = request.POST[app_str]
            if app_status == 'on':

                # Add the selected apps to the group
                print "on",a.name
                group.apps.add(a)

                # Get all the users in the group with the application selected
                for u in User.objects.filter(group__exact = group, user_apps__name__exact = a.name):
                    # Remove the selected group app from those users
                    for app in App.objects.filter(name__exact = a.name):
                        u.user_apps.remove(app)

        except (KeyError):
            group.apps.remove(a)
            # Remove the not-selected applications from the group
            #if group in a.groups.all():
            #   removeAppFromGroup(group, a)


    # return HttpResponse('')
    return HttpResponseRedirect("/groups/")
@login_required
def edit_client(request):
    cache.delete('clientjson')
    # print request.POST.get("group")
    # Add the group to the database if it does not already exist
    user_q = User.objects.filter(imei__exact = request.POST.get("imei_hidden"))
    if len(user_q) > 0:
        user = user_q.all()[0]
        user.imei = request.POST.get("imei")
        group = Group.objects.filter(name=request.POST.get("client_group"))[0]
        user.group.clear()
        user.group.add(group)
        user.simid = request.POST.get("sim_id")
        user.phone = request.POST.get("phone_no")

        user.save()

    # Add the specified applications to the group
    # return HttpResponse('')
    return HttpResponseRedirect("/getGroupClients/"+group.name)

@login_required
def edit_app(request):
    # print request.POST.get("group")
    # Add the group to the database if it does not already exist

    if request.method == 'POST':
        hidden_name = request.POST['name_hidden']
        hidden_release = request.POST['release_hidden']
        hidden_version = int(request.POST['version_hidden'])
        hidden_group = request.POST['group_hidden']
        
        name = request.POST['app_name']
        package = request.POST['package']
        version = int(request.POST['version'])
        release = request.POST['release']
        url = request.POST['url']
        action = request.POST['action']
        group_name = request.POST['app_group']
        extra_urls = request.POST['extra_urls']
        
        
        g = Group.objects.filter(name=group_name)
        if(len(g)>0):
            g=g[0]
            for app in g.apps.all():
                if app.name==name:
                    g.apps.remove(app)
        
        gh = Group.objects.filter(name=hidden_group)
        if(len(gh)>0):
            gh=gh[0]
            for app in gh.apps.all():
                if app.name==name:
                    gh.apps.remove(app)
        
        myapp = App.objects.filter(name=hidden_name,release=hidden_release,ver=hidden_version)[0]
        myapp.name = name
        myapp.package = package
        myapp.ver = version
        myapp.release = release
        myapp.url = url
        myapp.action = action
        myapp.extra_urls = extra_urls

        myapp.save()
        g.apps.add(myapp)
    return HttpResponseRedirect("/getReleaseVersions/"+name+"/"+release)


@login_required
def delete_group(request):
    #cache.delete('clientjson')
    print "deleting"
    group_q = Group.objects.filter(name__exact = request.POST.get('group'))

    # If the group exists in the database
    if len(group_q) > 0:
        print "len group_q >0"
        group = group_q.all()[0]

        # Retrieve the users in the group to be deleted
        users = User.objects.filter(group__exact = group)

        unmanaged = Group.objects.filter(name__exact = 'Unmanaged')[0]

        for u in users:
            # Clear the users old group
            u.group.clear()

            # Add the user to the Unmanaged group
            # Note this is NOT adding the Unmanaged applications to the user...
            # Not sure if this is the behavior that we want?
            u.group.add(unmanaged)

            # Remove any user apps that overlap with the Unmanaged group apps
            for app in unmanaged.apps.all():
                for tbd in u.user_apps.filter(name__exact=app.name):
                    u.user_apps.remove(tbd)

            u.save()

        # Remove the group from the applications that referenced it.
        # Note this is NOT removing the applications from the users who were in
        # this group!
        #for a in App.objects.all():
        #   if group in a.groups.all():
        #       a.groups.remove(group)

        # Delete the group from the table
        group.delete()


    return HttpResponseRedirect("/groups/")
@login_required
def delete_client(request):
    if request.method=="POST":
        client = User.objects.filter(imei=request.POST['imei'])
        groupname = User.objects.filter(imei=request.POST['groupname'])

        client.delete()
    return HttpResponse("ok")
@login_required
def getAppReleases(request, appname):
    releaselist = list()
    apps = App.objects.filter(name__exact = appname)
    for a in apps:
        if a.release not in [x['release'] for x in releaselist]:
            releaselist.append({"release":a.release})

    for release in releaselist:
        curRelease = App.objects.filter(name=appname, release=release["release"])
        versionlist=list()
        for i in curRelease:
            if i.ver not in versionlist:
                versionlist.append(i.ver)
        release["version_count"]=len(versionlist)

    return render_to_response('show_application_releases.html',{"releaselist": releaselist,"appname":appname,"form":ReleaseForm()})

@login_required
def getReleaseVersions(request, appname, release):
    versionlist = list()
    apps = App.objects.filter(name__exact = appname, release__exact = release)
    for a in apps:
        versionlist.append(a.ver)
    return render_to_response('show_application_versions.html',{"versionlist": versionlist,"app_name":appname,"release":release,"form":VersionForm()})

@login_required
def batchEditClients(request, validated):
    if 'group' in request.POST:
        group = request.POST['group']
    if 'add_apps' in request.POST:
        add_apps = request.POST['add_apps']
        add_apps = simplejson.loads(add_apps)

    if 'remove_apps' in request.POST:
        remove_apps = request.POST['remove_apps']
        remove_apps = simplejson.loads(remove_apps)
    if 'clients' in request.POST:
        clients = request.POST['clients']
        clients = simplejson.loads(clients)


    output = ''
    if 'clients' in locals():
        if validated == 'true':
            cache.delete('clientjson')

            # For each of the clients selected to edit
            for c in clients:
                q = User.objects.filter(imei__exact = c)[0]

                # If we want to change the group
                if 'group' in locals():
                    g = Group.objects.filter(name__exact = group)[0]
                    q.group.clear()
                    q.group.add(g)
                    # TODO: Remove overlapping user apps!
                    for a in g.apps.all():
                        overlap = q.user_apps.filter(name__exact=a.name)
                        if len(overlap) > 0:
                            q.user_apps.remove(overlap[0])

                if 'add_apps' in locals():
                    for a in add_apps:
                        app = App.objects.filter(name__exact = a['name'], release__exact = a['release'])[0]
                        q.apps.add(app)

                if 'remove_apps' in locals():
                    for a in remove_apps:
                        app = App.objects.filter(name__exact = a['name'], release__exact = a['release'])[0]
                        q.apps.remove(app)

                q.save()

        else:
            if 'group' in locals():
                g = Group.objects.filter(name__exact = group)[0]

            output = list()

            # For each of the clients selected to edit
            for c in clients:
                q = User.objects.filter(imei__exact = c)[0]

                appstring = ''

                # Check if any of the group apps overlap with user apps for this client
                for a in g.apps.all():
                    overlap = q.user_apps.filter(name__exact=a.name)
                    if len(overlap) > 0:
                        appstring += a.name + '(' + str(a.release) + ':' + str(a.ver) + '), '
                        #output += c + ' : ' + a.name + '\n'
                if appstring != '':
                    output.append({'imei':c, 'application':appstring[:-2]})

    return HttpResponse(simplejson.dumps(output))

@login_required
def getAppDetails(request):
    releaselist = list()
    appname = request.POST['name']
    release = request.POST['release']
    version = request.POST['version']

    app = App.objects.filter(name__exact = appname, release__exact = release, ver__exact = version)[0]

    groupslist = list()
    for g in Group.objects.filter(apps__name__exact=app.name):
        groupslist.append(g.name)

    details = {'package': app.package,
                         'version': app.ver,
                         'url': app.url,
                         'action': app.action,
                         'groups': groupslist,
                         'release': app.release,
                         'name': app.name}

    return HttpResponse(simplejson.dumps(details), content_type='application/javascript')

@login_required
def add_client(request):

    appslist = list()
    userapps = list()

    debug_str = ""

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect("/")

        cache.delete('clientjson')
        debug_str = str(request.POST)
        imei = request.POST['user_imei']
        group_name = request.POST['user_group']
        sim_id = request.POST['sim_id']
        phone = request.POST['phone']
        jitter = request.POST['jitter']
        
        locked_inventory = False
        myuser = User()

        if len(imei) > 0:
            print "len imei >0"
            user_q = User.objects.filter(imei__exact = imei)
            if len(user_q) > 0:
                print "len user_q >0"
                myuser = user_q.all()[0]
                if 'delete' in request.POST:
                    print "delete in post"
                    myuser.delete()
                    return HttpResponseRedirect("/")
            else:
                print "delete not in post"
                myuser.imei = imei
                myuser.save()


            if len(group_name) > 0:
                print "group name >0"
                if len(myuser.group.all()) > 0:
                    print "group.all >0"
                    myuser.group.clear()
                myuser.group.add(findGroup(group_name, myuser))



            for a in App.objects.all():
                app_str = str(a.package) + "(" + str(a.release) + "," + str(a.ver) + ")"
                try:
                    app_status = request.POST[app_str]
                    if app_status == 'on':
                        myuser.user_apps.add(a)

                except (KeyError):
                    if a in myuser.user_apps.all():
                        myuser.user_apps.remove(a)

            myuser.phone = phone
            myuser.simid = sim_id
            myuser.jitter = jitter
            
            myuser.locked_inventory = True
            myuser.save()
            userapps = myuser.user_apps.all()
            message = "Saved user information."
            new_user = False

        else:
            print "imei is empty"
            # message = "IMEI cannot be empty."
            # new_user = True

    return HttpResponseRedirect("/clients/")

def client_extra_info(request, imei):
    result={}
    if(request.method=="GET"):
        print "inside get"
        user_imei = imei
        print user_imei
        user = User.objects.filter(imei=user_imei)
        if len(user)>0:
            print "user found"
            jitter = user[0].jitter
            result["jitter"] = jitter
            print result
    return HttpResponse(simplejson.dumps(result))

@login_required
def add_app(request):
    name=""
    if request.method == 'POST':
        name = request.POST['app_name']
        package = request.POST['package']
        version = request.POST['version']
        release = request.POST['release']
        url = request.POST['url']
        action = request.POST['action']
        group_name = request.POST['app_group']
        extra_urls = request.POST['extra_urls']
        
        applist = list()
        for a in App.objects.all():
            if a.name not in applist:
                applist.append(a.name)
        if name in applist:
            return HttpResponseRedirect("/apps/")

        g = Group.objects.filter(name=group_name)
        if(len(g)>0):
            g=g[0]
            for app in g.apps.all():
                if app.name==name:
                    g.apps.remove(app)

        myapp = App()
        myapp.name = name
        myapp.package = package
        myapp.ver = version
        myapp.release = release
        myapp.url = url
        myapp.action = action
        myapp.extra_urls = extra_urls

        myapp.save()
        g.apps.add(myapp)
    return HttpResponseRedirect("/apps/")

@login_required
def add_release(request):
    name=""
    if request.method == 'POST':
        name = request.POST['app_name']
        package = request.POST['package']
        version = request.POST['version']
        release = request.POST['release']
        url = request.POST['url']
        action = request.POST['action']
        group_name = request.POST['app_group']
        
        releaselist = list()
        apps = App.objects.filter(name__exact = name)
        for a in apps:
            if a.release not in releaselist:
                releaselist.append(a.release)
        if release in releaselist:
            return HttpResponseRedirect("/getAppReleases/"+name)

        g = Group.objects.filter(name=group_name)
        if(len(g)>0):
            g=g[0]
            for app in g.apps.all():
                if app.name==name:
                    g.apps.remove(app)

        myapp = App()
        myapp.name = name
        myapp.package = package
        myapp.ver = version
        myapp.release = release
        myapp.url = url
        myapp.action = action
        myapp.save()
        g.apps.add(myapp)
    return HttpResponseRedirect("/getAppReleases/"+name)

@login_required
def add_version(request):
    name=""
    if request.method == 'POST':

        name = request.POST['app_name']
        package = request.POST['package']
        version = int(request.POST['version'])
        release = request.POST['release']
        url = request.POST['url']
        action = request.POST['action']
        group_name = request.POST['app_group']
        
        versionlist = list()
        apps = App.objects.filter(name__exact = name, release__exact = release)
        for a in apps:
            versionlist.append(a.ver)
        print version


        if version in versionlist:
            return HttpResponseRedirect("/getReleaseVersions/"+name+"/"+release)

        g = Group.objects.filter(name=group_name)
        if(len(g)>0):
            g=g[0]
            for app in g.apps.all():
                if app.name==name:
                    g.apps.remove(app)

        myapp = App()
        myapp.name = name
        myapp.package = package
        myapp.ver = version
        myapp.release = release
        myapp.url = url
        myapp.action = action
        myapp.save()
        g.apps.add(myapp)
    return HttpResponseRedirect("/getReleaseVersions/"+name+"/"+release)


@login_required
def add1_app(request, app_str):
    cache.delete('clientjson')

    t = loader.get_template('app.html')


    debug_str = ""

    appgroups = list()
    grouplist = list()

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect("/")

        debug_str = str(request.POST)
        name = request.POST['app_name']
        ver = request.POST['app_ver']
        release = request.POST['app_release']
        package = request.POST['app_package']
        url = request.POST['app_url']
        action = request.POST['action']


        myapp = App()

        if len(name) == 0 or len(ver) == 0 or len(url) == 0 or len(package) == 0 or len(release) == 0:
            message = "Please specify all values"
            new_app = True
        else:
            app_q = App.objects.filter(name__exact = name, release__exact = release, ver__exact = ver)


            #app_q = App.objects.filter(name__exact = name)
            #app_q = app_q.filter(release__exact = release)

            if len(app_q) == 1:
                myapp = app_q.all()[0]
                if 'delete' in request.POST:
                    myapp.delete()
                    return HttpResponseRedirect("/")

            elif len(app_q) > 1:
                message = "There is a problem. Contact Hossein."

            # Check to make sure there are no other application names with
            # the provided package string
            for a in App.objects.filter(package__exact=package):
                if a.name != name:
                    return HttpResponse('Error: Attempting to re-use package name that is already taken by another application.')

            myapp.name = name
            myapp.package = package
            myapp.ver = eval(ver)
            myapp.release = release
            myapp.url = url
            myapp.action = action
            myapp.save()

            for g in Group.objects.all():
                try:
                    grp_status = request.POST[g.name]
                    if grp_status == 'on':
                        # Make sure there are no other versions of the same app
                        # associated with this group
                        for rem in g.apps.filter(name__exact = myapp.name):
                            g.apps.remove(rem)

                        # Add the app to the Group
                        g.apps.add(myapp)
                        #addAppToGroup(g, myapp)

                except (KeyError):
                        g.apps.remove(myapp)
                   # if g in myapp.groups.all():
                    #    removeAppFromGroup(g, myapp)

            appgroups = Group.objects.filter(apps__name__exact=myapp.name)
            #appgroups = myapp.groups.all()
            message = "Saved application information."


            new_app = False



    else:
        if len(app_str) > 0:
            (name, release) = app_str.rsplit("__")
            if len(name) > 0 and len(release):
                app_q = App.objects.filter(name__exact = name)
                app_q = app_q.filter(release__exact = release)


                if len(app_q) == 1:
                    myapp = app_q.all()[0]
                    appgroups = Group.objects.filter(apps__name__exact=myapp.name)
                    #appgroups = myapp.groups.all()
                    message = "Update application information."
                    new_app = False
                else:
                    message = "Add new application."
                    new_app = True
        else:
            message = "Add new application."
            new_app = True


    for g in Group.objects.all():
        user_count = User.objects.filter(group__exact = g).count()
        #if user_count == 0:
        #    g.delete()
        #else:
        if g in appgroups:
            grouplist.append(GroupData(g, user_count, True))
        else:
            grouplist.append(GroupData(g, user_count, False))




    actions = ['Update', 'Clean']

    c = Context({ 'message': message,
                 'debug' : debug_str,
                 'groups' : grouplist,
                 'actions' : actions,
        })

    if not new_app:
        cur_action = myapp.action
        c.update({'app': myapp,
                 'action' : cur_action

            })


    return HttpResponse(t.render(c))

@login_required
def delete_app_version(request):

    app_name = request.POST['name']
    app_ver = request.POST['version']
    app_release = request.POST['release']

    app_q = App.objects.filter(name__exact=app_name, release__exact=app_release, ver__exact=app_ver)

    # If the app exists in the database
    if len(app_q) > 0:
        app = app_q.all()[0]

        app.delete()


    return HttpResponse('')

@login_required
def logs(request):
    t = loader.get_template('logs.html')

    logs = list()

    for u in User.objects.all().order_by("-imei"):
        log_q = Logs.objects.filter(imei__exact = u.imei)
        log_q = log_q.order_by('-access')
        count = log_q.count()
        reported = ""
        if count > 0:
            access =  local_time_str(log_q.all()[0].access)
            reported = log_q[0].packages
        else:
            access = 'No record'
        setconf = ""
        for grp in u.group.all():
            for ap in grp.apps.all():
                setconf += "" + ap.package + ":" + str(ap.ver) + ", "
        logs.append(LogRecord(u.imei, access , count, setconf, reported))

    c = Context({'logs' : logs,
                 'message' : 'Client access log'
                 })

    return HttpResponse(t.render(c))

@login_required
def logs_group(request, group=None):
    t = loader.get_template('logs.html')

    logs = list()
    thegroup = Group.objects.get(name__exact=group)
    for u in User.objects.filter(group__exact=thegroup).order_by("-imei"):
        log_q = Logs.objects.filter(imei__exact = u.imei)
        log_q = log_q.order_by('-access')
        count = log_q.count()
        reported = ""
        if count > 0:
            access =  local_time_str(log_q.all()[0].access)
            reported = log_q[0].packages
        else:
            access = 'No record'
        setconf = ""
        for grp in u.group.all():
            for ap in grp.apps.all():
                setconf += "" + ap.package + ":" + str(ap.ver) + ", "
        logs.append(LogRecord(u.imei, access , count, setconf, reported))

    c = Context({'logs' : logs,
                 'message' : 'Client access log'
                 })

    return HttpResponse(t.render(c))


@login_required
def logs_imei(request, imei=None):
    t = loader.get_template('logs.html')

    logs = list()
    u = User.objects.get(imei__exact = imei)
    log_q = Logs.objects.filter(imei__exact = imei)
    log_q = log_q.order_by('-access')
    count = log_q.count()
    reported = ""
    access = 'No record'
    if count > 100:
        limit = 90
    else:
        limit = count
    count = 0
    while count < limit:
        access =  local_time_str(log_q[count].access)
        reported = log_q[count].packages
        setconf = ""
        for grp in u.group.all():
            for ap in grp.apps.all():
                setconf += "" + ap.package + ":" + str(ap.ver) + ", "
        logs.append(LogRecord(imei, access, count, setconf, reported))
        count = count + 1

    c = Context({'logs' : logs,
                 'message' : 'Client access log'
                 })

    return HttpResponse(t.render(c))
