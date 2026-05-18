from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scraper.fetch import get_page, parse_wage_table, parse_kasambahay_table

app = FastAPI(
    title="PH Minimum Wage API",
    description="Current minimum wage rates per region sourced from NWPC-DOLE.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REGION_URLS = {
    "ncr": "https://nwpc.dole.gov.ph/ncr/",
    "car": "https://nwpc.dole.gov.ph/car/",
    "region-1": "https://nwpc.dole.gov.ph/region-i/",
    "region-2": "https://nwpc.dole.gov.ph/region-ii/",
    "region-3": "https://nwpc.dole.gov.ph/region-iii/",
    "region-4a": "https://nwpc.dole.gov.ph/region-iva/",
    "region-4b": "https://nwpc.dole.gov.ph/region-ivb/",
    "region-5": "https://nwpc.dole.gov.ph/region-v/",
    "region-6": "https://nwpc.dole.gov.ph/region-vi/",
    "region-7": "https://nwpc.dole.gov.ph/region-vii/",
    "region-8": "https://nwpc.dole.gov.ph/region-viii/",
    "region-9": "https://nwpc.dole.gov.ph/region-ix/",
    "region-10": "https://nwpc.dole.gov.ph/region-x/",
    "region-11": "https://nwpc.dole.gov.ph/region-xi/",
    "region-12": "https://nwpc.dole.gov.ph/region-xii/",
    "region-13": "https://nwpc.dole.gov.ph/region-xiii/",
    "barmm": "https://nwpc.dole.gov.ph/barmm/",
}

def scrape_region(region_slug: str) -> dict:
    url = REGION_URLS[region_slug]
    soup = get_page(url)
    return {
        "region": region_slug.upper(),
        "source": url,
        "sectors": parse_wage_table(soup),
        "kasambahay": parse_kasambahay_table(soup),
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/regions")
def list_regions():
    return {"regions": list(REGION_URLS.keys())}

@app.get("/api/v1/wages/{region}")
def get_wages(region: str):
    region = region.lower()
    if region not in REGION_URLS:
        raise HTTPException(
            status_code=404,
            detail=f"Region '{region}' not found. Use /api/v1/regions to see valid slugs."
        )
    try:
        data = scrape_region(region)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/wages")
def get_all_wages():
    results = {}
    for slug in REGION_URLS:
        try:
            results[slug] = scrape_region(slug)
        except Exception as e:
            results[slug] = {"error": str(e)}
    return results