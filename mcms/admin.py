from django.contrib import admin

from .models import Category, Language, Article,FrontMenu, Comments, Ads, Gallery, Archive, PhotoFeature, Image, Columnists, ColumnCategory, Columns, PhotoFeatureImages, WriteToUs, AboutUs, HomeBanners, Country, UserPasswordChange, NewsLetterEnquiry,Subscribe,Editor

from watson.models import SearchEntry

# Register your models here.
#register Category
admin.site.register(Category)
#register Language
admin.site.register(Language)
#register Article
admin.site.register(Article)
#register FrontMenu
admin.site.register(FrontMenu)
#register Comments
admin.site.register(Comments)
#register Ads
admin.site.register(Ads)
admin.site.register(Country)
#register Gallery
admin.site.register(Gallery)
#register SearchEntry
admin.site.register(SearchEntry)
#register Image
admin.site.register(Image)
#register Archive
admin.site.register(Archive)
#register PhotoFeature
admin.site.register(PhotoFeature)
#register Columnists
admin.site.register(ColumnCategory)
#register Columnists
admin.site.register(Columns)

# register HomeBanners
admin.site.register(HomeBanners)

#register Columnists
admin.site.register(Columnists)
# register PhotoFeatureImage
admin.site.register(PhotoFeatureImages)
# register WriteToUs
admin.site.register(WriteToUs)
# register AboutUs
admin.site.register(AboutUs)
admin.site.register(UserPasswordChange)
admin.site.register(NewsLetterEnquiry)
admin.site.register(Subscribe)
admin.site.register(Editor)

