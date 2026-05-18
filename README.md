# PH Minimum Wage API

A REST API that scrapes live minimum wage data per region in the Philippines from the official [NWPC-DOLE website](https://nwpc.dole.gov.ph/).

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/regions` | List all available region slugs |
| GET | `/api/v1/wages/{region}` | Get wage data for a specific region |
| GET | `/api/v1/wages` | Get wage data for all regions |

### Available Region Slugs

`ncr`, `car`, `region-1`, `region-2`, `region-3`, `region-4a`, `region-4b`, `region-5`, `region-6`, `region-7`, `region-8`, `region-9`, `region-10`, `region-11`, `region-12`, `region-13`, `barmm`

### Example Response

```
GET /api/v1/wages/ncr
```

```json
{
  "region": "NCR",
  "source": "https://nwpc.dole.gov.ph/ncr/",
  "sectors": [
    {
      "sector": "Non-Agriculture",
      "current_wage": 610,
      "wage_increase": 35,
      "new_wage": 645
    },
    {
      "sector": "Agriculture",
      "current_wage": 573,
      "wage_increase": 35,
      "new_wage": 608
    }
  ],
  "kasambahay": {
    "sector": "Kasambahay",
    "current_wage": 7000,
    "wage_increase": null,
    "new_wage": null
  }
}
```

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://localhost:8000/docs` for the interactive Swagger UI.

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [httpx](https://www.python-httpx.org/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)

## Deploying to Render

1. Push your code to GitHub
2. Go to [render.com](https://render.com) and create a free account
3. Click **New → Web Service** and connect your GitHub repo
4. Set the following:

   | Setting | Value |
   |---|---|
   | Runtime | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn app:app --host 0.0.0.0 --port $PORT` |

5. Click **Create Web Service**

Your API will be live at `https://your-app.onrender.com`.

> **Note:** The free tier spins down after 15 minutes of inactivity. The first request after idle may take ~30 seconds.

## Data Source

All wage data is sourced from the [National Wages and Productivity Commission (NWPC)](https://nwpc.dole.gov.ph/).
