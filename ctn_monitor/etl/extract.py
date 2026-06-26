import logging

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult

from .path_setup import get_path
from .utils import is_nonempty_file, write_bytes_atomic

logger = logging.getLogger(__name__)

_EXTRACT_PARAMS = ExtractPDFParams(
    elements_to_extract=[ExtractElementType.TABLES],
)


def extract_pdf_table(ctn_pdf: str, client_id: str, client_secret: str) -> str:
    """
    Extracts tables from a single CTN.

    Args:
        ctn_pdf: PDF file name to be processed.
        client_id: Adobe PDF Services client ID.
        client_secret: Adobe PDF Services client secret.

    Raises:
        ValueError: If credentials are missing.
        RuntimeError: If table extraction fails.
    """
    ctn_zip = ctn_pdf.removesuffix(".pdf") + ".zip"
    pth_zip = get_path("zip") / ctn_zip

    if is_nonempty_file(pth_zip):
        logger.info("%s already cached; skipping extraction", ctn_zip)
        return ctn_zip

    if not client_id or not client_secret:
        raise ValueError("CLIENT_ID and CLIENT_SECRET are required")

    try:
        credentials = ServicePrincipalCredentials(
            client_id=client_id,
            client_secret=client_secret,
        )
        pdf_services = PDFServices(credentials=credentials)

        input_asset = pdf_services.upload(
            input_stream=(get_path("pdf") / ctn_pdf).read_bytes(),
            mime_type=PDFServicesMediaType.PDF,
        )

        job = ExtractPDFJob(
            input_asset=input_asset,
            extract_pdf_params=_EXTRACT_PARAMS,
        )

        location = pdf_services.submit(job)
        response = pdf_services.get_job_result(location, ExtractPDFResult)

        result = response.get_result().get_resource()
        stream = pdf_services.get_content(result)
    except (FileNotFoundError, ValueError, RuntimeError) as err:
        raise RuntimeError(
            f"Failed to extract table from {ctn_pdf}: {err}"
        ) from err

    write_bytes_atomic(stream.get_input_stream(), pth_zip)

    return ctn_zip
