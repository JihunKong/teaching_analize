"""
Reporting Service Router
Proxies requests to the reporting service (Module 4)
"""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, HTMLResponse
import httpx

from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/reports",
    tags=["reporting"]
)


async def get_http_client():
    """Get HTTP client with timeout"""
    return httpx.AsyncClient(timeout=settings.service_timeout)


@router.get("/html/{job_id}", response_class=HTMLResponse)
async def get_html_report(job_id: str):
    """
    Get HTML report

    Proxies to analysis service (report generators are there)
    """
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.analysis_service_url}/api/reports/html/{job_id}"
            )

            if response.status_code == 200:
                return HTMLResponse(content=response.text, media_type="text/html")
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Report not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Report generation failed"
                )

    except httpx.RequestError as e:
        logger.error(f"Reporting service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Reporting service unavailable"
        )


@router.get("/pdf/{job_id}")
async def get_pdf_report(job_id: str):
    """
    Get PDF report

    Proxies to analysis service (report generators are there)
    """
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.analysis_service_url}/api/reports/pdf/{job_id}"
            )

            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type="application/pdf",
                    headers=dict(response.headers)
                )
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Report not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="PDF generation failed"
                )

    except httpx.RequestError as e:
        logger.error(f"Reporting service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Reporting service unavailable"
        )


@router.get("/pdf-enhanced/{job_id}")
async def get_enhanced_pdf_report(job_id: str, include_cover: bool = True):
    """
    Get enhanced PDF report with rendered charts

    Proxies to analysis service (report generators are there)
    """
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.analysis_service_url}/api/reports/pdf-enhanced/{job_id}",
                params={"include_cover": include_cover}
            )

            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type="application/pdf",
                    headers=dict(response.headers)
                )
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Report not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Enhanced PDF generation failed"
                )

    except httpx.RequestError as e:
        logger.error(f"Reporting service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Reporting service unavailable"
        )


@router.get("/excel/{job_id}")
async def get_excel_report(job_id: str):
    """
    Get Excel report

    Proxies to analysis service (report generators are there)
    """
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.analysis_service_url}/api/reports/excel/{job_id}"
            )

            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers=dict(response.headers)
                )
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Report not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Excel generation failed"
                )

    except httpx.RequestError as e:
        logger.error(f"Reporting service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Reporting service unavailable"
        )


@router.get("/visualization/3d-matrix/{job_id}", response_class=HTMLResponse)
async def get_3d_matrix_visualization(job_id: str):
    """
    Get 3D matrix visualization

    Proxies to analysis service (report generators are there)
    """
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.analysis_service_url}/api/reports/visualization/3d-matrix/{job_id}"
            )

            if response.status_code == 200:
                return HTMLResponse(content=response.text, media_type="text/html")
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Visualization not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Visualization generation failed"
                )

    except httpx.RequestError as e:
        logger.error(f"Reporting service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Reporting service unavailable"
        )


@router.get("/data/{job_id}")
async def get_report_data(job_id: str):
    """
    Get structured report data

    Proxies to analysis service (report generators are there)
    """
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.analysis_service_url}/api/reports/data/{job_id}"
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Report data not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to retrieve report data"
                )

    except httpx.RequestError as e:
        logger.error(f"Reporting service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Reporting service unavailable"
        )


@router.get("/health")
async def check_reporting_service():
    """Check reporting service health"""
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.reporting_service_url}/health",
                timeout=5.0
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
