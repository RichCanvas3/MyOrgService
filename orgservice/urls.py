
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, Router
from ninja_extra import NinjaExtraAPI, status
from ninja import Query
from orgservice.good_standing_service import GoodStandingService
from orgservice.schema import GoodStandingSchema

creds = NinjaAPI()

@creds.get("/good-standing/company", response=GoodStandingSchema)
def good_standing_company(request, company: str = Query(...), state: str = Query(...)):
    gs = GoodStandingService()
    return gs.get_cred_company(company, state)

@creds.get("/good-standing/email", response=GoodStandingSchema)
def good_standing_email(request, email: str = Query(...)):
    gs = GoodStandingService()
    return gs.get_cred_email(email)

@creds.get("/good-standing/domain", response=GoodStandingSchema)
def good_standing_domain(request, domain: str = Query(...)):
    gs = GoodStandingService()
    return gs.get_cred_domain(domain)

@creds.get("/good-standing/website", response=GoodStandingSchema)
def good_standing_website(request, website: str = Query(...)):
    gs = GoodStandingService()
    return gs.get_cred_website(website)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("creds/", creds.urls),
]
