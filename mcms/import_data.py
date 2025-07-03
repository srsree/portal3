import csv
from mcms.models import *
from django.template.defaultfilters import slugify
from django.core.files import File, images
import urllib
def import_data():
    reader=csv.reader(open("/home/mahiti/Portal/updated_data.csv","rb"), delimiter=",")
    fields=reader.next()
    for i,item in enumerate(reader):
        items = zip(fields,item)
        row = {}
        cat = ''
        for (name,value) in items:
            row[name]=value.strip()
        print row['Title']
        f = ''
        try:
            #import pdb;pdb.set_trace()
            result = urllib.urlretrieve("http://www.civilsocietyonline.com/Admin/News_Main_Images/"+str(row['Image']))
            f = images.ImageFile(open(result[0], 'r'))
        #f = images.ImageFile(open("http://www.civilsocietyonline.com/Admin/News_Main_Images/"+str(row['Image']),"rb"))
        except:
            pass
        if row['category']:
            cat = FrontMenu.objects.get_or_create(name=row['category'])
        if not Article.objects.filter(headline=row['Title']):
            if f:
                print f
                try:
                    Article.objects.create(frontmenu=cat[0],headline=row['Title'],slug=slugify(row['Title']),synopsis = row['Summary'], byline=row['byline'],description=row['description'], icon=f)
                except:
                    Article.objects.create(frontmenu=cat[0],headline=row['Title'],slug=slugify(row['Title']),synopsis = row['Summary'], byline=row['byline'],description=row['description'])
            else:
                Article.objects.create(frontmenu=cat[0],headline=row['Title'],slug=slugify(row['Title']),synopsis = row['Summary'], byline=row['byline'],description=row['description'])
            print "created------------"
        else:
            print "already exisits-------"

from django.contrib.contenttypes.models import ContentType

def import_comments():
    reader=csv.reader(open("/home/mahiti/Portal/comments_data.csv","rb"), delimiter=",")
    fields=reader.next()
    for i,item in enumerate(reader):
        items = zip(fields,item)
        row = {}
        cat = ''
        for (name,value) in items:
            row[name]=value.strip()
        print row['Title']
        art= ''
        try:
            art = Article.objects.get(headline=row['Title'])
        except:
            pass
        if art:
            Comments.objects.create(content_type=ContentType.objects.get_for_model(art), object_id=art.id,name=row['uname'],email=row['email'],comment=row['comments'],created_on=row['created'],publish=True)
            print "created---------------------"
        else:
            print "Not exists -------------"
