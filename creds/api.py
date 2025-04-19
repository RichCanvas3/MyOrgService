from ninja_extra import NinjaExtraAPI, status
from ninja import Query
from .good_standing_service import GoodStandingService
from .schema import GoodStandingSchema

api = NinjaExtraAPI(urls_namespace="creds")

@api.get("/good-standing/company", response=GoodStandingSchema)
def good_standing_company(request, company: str = Query(...), state: str = Query(...)):
    gs = GoodStandingService()
    return gs.get_cred_company(company, state)

@api.get("/good-standing/email", response=GoodStandingSchema)
def good_standing_email(request, email: str = Query(...)):
    gs = GoodStandingService()
    return gs.get_cred_email(email)

@api.get("/good-standing/domain", response=GoodStandingSchema)
def good_standing_domain(request, domain: str = Query(...)):
    gs = GoodStandingService()
    return gs.get_cred_domain(domain)

@api.get("/good-standing/website", response=GoodStandingSchema)
def good_standing_website(request, website: str = Query(...)):
    gs = GoodStandingService()
    return gs.get_cred_website(website)